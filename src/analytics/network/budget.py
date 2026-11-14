"""Motor de orçamento (v2.4): linhas por mês civil, ajustes gerenciais explícitos e ponte.

Convenções:
- o plano cobre as semanas ISO do ano do cenário; cada semana é alocada aos
  meses civis pela participação de dias (semanas de virada caem no mês vizinho);
- tarifas são brutas (com impostos); créditos recuperáveis reduzem o custo líquido;
- ajustes gerenciais APROVADOS entram como linhas próprias, nunca dentro das fórmulas;
  sem ajustes, o orçamento final é exatamente o orçamento do modelo.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.analytics.network import planning
from src.analytics.network.repository import DadosRede


COMPONENTES_MODELO = ("FREIGHT", "OVERFLOW", "EXTRAS", "TAX_CREDIT")


def _alocar_meses(dados: DadosRede, plano: pd.DataFrame) -> pd.DataFrame:
    base = plano[["scenario_id", "week_start", "route_id", "dc_id", "carrier_id", "volume", "total_trips",
                  "freight_cost", "overflow_cost"]]
    alocado = base.merge(dados.participacao_mes_civil, on="week_start")
    for coluna in ("volume", "total_trips", "freight_cost", "overflow_cost"):
        alocado[coluna] = alocado[coluna] * alocado["share"]
    return alocado


def linhas_modelo(dados: DadosRede, scenario_id: str, plano: pd.DataFrame | None = None,
                  overrides: list[dict] | None = None) -> pd.DataFrame:
    """Linhas do orçamento do modelo (antes de ajustes gerenciais)."""
    params = planning.parametros_cenario(dados, scenario_id, overrides)
    plano = planning.planejar_cenario(dados, scenario_id, overrides) if plano is None else plano
    a = _alocar_meses(dados, plano)
    semanas = a["week_start"].unique()
    taxa_extras = {ws: params.numero("extras_rate", padrao=0.0, data=ws) for ws in semanas}
    taxa_credito = {ws: params.numero("credit_rate.PIS_COFINS", padrao=0.0, data=ws) for ws in semanas}
    extras = a["week_start"].map(taxa_extras).to_numpy()
    credito = a["week_start"].map(taxa_credito).to_numpy()
    a["EXTRAS"] = (a["freight_cost"] + a["overflow_cost"]) * extras
    a["TAX_CREDIT"] = -(a["freight_cost"] + a["overflow_cost"] + a["EXTRAS"]) * credito
    a = a.rename(columns={"freight_cost": "FREIGHT", "overflow_cost": "OVERFLOW"})
    chaves = ["scenario_id", "civil_month", "dc_id", "route_id", "carrier_id"]
    agregado = a.groupby(chaves)[list(COMPONENTES_MODELO) + ["volume", "total_trips"]].sum().reset_index()
    linhas = agregado.melt(id_vars=chaves + ["volume", "total_trips"], value_vars=list(COMPONENTES_MODELO),
                           var_name="cost_component", value_name="amount_brl")
    linhas["source"] = "MODEL"
    # volume e viagens ficam só na linha FREIGHT para não duplicar em somas
    linhas.loc[linhas["cost_component"] != "FREIGHT", ["volume", "total_trips"]] = 0.0
    return linhas


def _escopo_mascara(linhas: pd.DataFrame, escopo: str) -> pd.Series:
    tipo, _, chave = escopo.partition(":")
    if tipo == "NETWORK":
        return pd.Series(True, index=linhas.index)
    if tipo == "DC":
        return linhas["dc_id"] == chave
    if tipo == "ROUTE":
        return linhas["route_id"] == chave
    if tipo == "CARRIER":
        return linhas["carrier_id"] == chave
    if tipo == "MONTH":
        return linhas["civil_month"] == chave
    raise ValueError(f"Escopo de ajuste inválido: {escopo}")


def linhas_ajustes(dados: DadosRede, scenario_id: str, modelo: pd.DataFrame,
                   ajustes_extra: list[dict] | None = None) -> pd.DataFrame:
    """Linhas de ajuste gerencial, alocadas proporcionalmente ao modelo dentro do escopo.

    MULTIPLIER: (valor − 1) × total do modelo no escopo (não compõe com outros ajustes).
    ABSOLUTE_BRL: valor distribuído pelo peso do modelo no escopo.
    Somente ajustes APPROVED entram.
    """
    ajustes = dados["tn_management_adjustments"]
    ajustes = ajustes[ajustes["scenario_id"] == scenario_id]
    if ajustes_extra:
        ajustes = pd.concat([ajustes, pd.DataFrame(ajustes_extra)], ignore_index=True)
    aprovados = ajustes[ajustes["status"] == "APPROVED"]
    chaves = ["scenario_id", "civil_month", "dc_id", "route_id", "carrier_id"]
    peso = modelo.groupby(chaves)["amount_brl"].sum().reset_index()
    blocos = []
    for aj in aprovados.itertuples(index=False):
        mascara = _escopo_mascara(peso, aj.scope)
        alvo = peso[mascara].copy()
        total = alvo["amount_brl"].sum()
        if alvo.empty or total == 0:
            continue
        valor = (float(aj.value) - 1) * total if aj.adjustment_type == "MULTIPLIER" else float(aj.value)
        alvo["amount_brl"] = valor * alvo["amount_brl"] / total
        alvo["cost_component"] = "ADJUSTMENT"
        alvo["source"] = f"ADJUSTMENT:{aj.adjustment_id}"
        alvo["volume"] = 0.0
        alvo["total_trips"] = 0.0
        blocos.append(alvo)
    if not blocos:
        return pd.DataFrame(columns=list(modelo.columns))
    return pd.concat(blocos, ignore_index=True)[list(modelo.columns)]


def orcamento(dados: DadosRede, scenario_id: str, plano: pd.DataFrame | None = None,
              overrides: list[dict] | None = None, ajustes_extra: list[dict] | None = None) -> pd.DataFrame:
    """Orçamento completo (equivalente a tn_budget_lines): modelo + ajustes aprovados."""
    modelo = linhas_modelo(dados, scenario_id, plano, overrides)
    ajustes = linhas_ajustes(dados, scenario_id, modelo, ajustes_extra)
    return pd.concat([modelo, ajustes], ignore_index=True) if len(ajustes) else modelo


# ---------------------------------------------------------------------------
# Visões
# ---------------------------------------------------------------------------

def resumo_orcamento(linhas: pd.DataFrame, por: str = "civil_month") -> pd.DataFrame:
    """Pivot por mês (ou dc_id/route_id) × componente, com modelo, ajustes e final."""
    tabela = linhas.pivot_table(index=por, columns="cost_component", values="amount_brl", aggfunc="sum", fill_value=0.0)
    for c in list(COMPONENTES_MODELO) + ["ADJUSTMENT"]:
        if c not in tabela.columns:
            tabela[c] = 0.0
    tabela["MODEL_BUDGET"] = tabela[list(COMPONENTES_MODELO)].sum(axis=1)
    tabela["FINAL_BUDGET"] = tabela["MODEL_BUDGET"] + tabela["ADJUSTMENT"]
    volume = linhas.groupby(por)["volume"].sum()
    tabela["volume"] = volume
    tabela["final_cost_per_piece"] = tabela["FINAL_BUDGET"] / tabela["volume"].replace(0, np.nan)
    return tabela[list(COMPONENTES_MODELO) + ["MODEL_BUDGET", "ADJUSTMENT", "FINAL_BUDGET", "volume", "final_cost_per_piece"]].reset_index()


def totais(linhas: pd.DataFrame) -> dict:
    modelo = float(linhas.loc[linhas["source"] == "MODEL", "amount_brl"].sum())
    ajuste = float(linhas.loc[linhas["source"] != "MODEL", "amount_brl"].sum())
    final = modelo + ajuste
    return {
        "model_budget": modelo,
        "adjustments": ajuste,
        "final_budget": final,
        "adjustment_share": ajuste / final if final else 0.0,
        "volume": float(linhas["volume"].sum()),
        "by_component": linhas.groupby("cost_component")["amount_brl"].sum().to_dict(),
    }


def relatorio_ajustes(dados: DadosRede, scenario_id: str, linhas: pd.DataFrame) -> pd.DataFrame:
    """Ajustes do cenário (aprovados e pendentes) com impacto em R$ (Q-BUD-04)."""
    ajustes = dados["tn_management_adjustments"]
    ajustes = ajustes[ajustes["scenario_id"] == scenario_id].copy()
    impacto = linhas[linhas["source"].str.startswith("ADJUSTMENT:")].groupby("source")["amount_brl"].sum()
    ajustes["impact_brl"] = ajustes["adjustment_id"].map(lambda a: float(impacto.get(f"ADJUSTMENT:{a}", 0.0)))
    final = float(linhas["amount_brl"].sum())
    ajustes["share_of_final_budget"] = ajustes["impact_brl"] / final if final else 0.0
    ajustes["applied"] = ajustes["status"] == "APPROVED"
    return ajustes[["adjustment_id", "scope", "adjustment_type", "value", "status", "applied", "impact_brl",
                    "share_of_final_budget", "reason", "requested_by_role", "approved_by_role", "approved_at"]]


# ---------------------------------------------------------------------------
# Decomposição volume / eficiência / tarifa
# ---------------------------------------------------------------------------

def decompor(v_b: float, t_b: float, c_b: float, v_a: float, t_a: float, c_a: float) -> dict:
    """C = V × (T/V) × (C/T); decomposição sequencial que soma exatamente C_a − C_b.

    Entrada ou saída de rota (V_b = 0 ou V_a = 0) é atribuída integralmente ao efeito volume.
    """
    if v_b <= 0 or v_a <= 0 or t_b <= 0 or t_a <= 0:
        return {"volume_effect": c_a - c_b, "efficiency_effect": 0.0, "rate_effect": 0.0}
    tv_b, tv_a = t_b / v_b, t_a / v_a
    ct_b, ct_a = c_b / t_b, c_a / t_a
    return {
        "volume_effect": (v_a - v_b) * tv_b * ct_b,
        "efficiency_effect": v_a * (tv_a - tv_b) * ct_b,
        "rate_effect": v_a * tv_a * (ct_a - ct_b),
    }


def decompor_por_chave(base: pd.DataFrame, alvo: pd.DataFrame, chaves: list[str]) -> pd.DataFrame:
    """base/alvo com colunas chaves + volume, trips, cost; retorna efeitos por chave."""
    b = base.groupby(chaves)[["volume", "trips", "cost"]].sum()
    a = alvo.groupby(chaves)[["volume", "trips", "cost"]].sum()
    juntos = b.join(a, how="outer", lsuffix="_base", rsuffix="_target").fillna(0.0)
    efeitos = [decompor(r.volume_base, r.trips_base, r.cost_base, r.volume_target, r.trips_target, r.cost_target)
               for r in juntos.itertuples()]
    juntos = juntos.join(pd.DataFrame(efeitos, index=juntos.index))
    juntos["variance"] = juntos["cost_target"] - juntos["cost_base"]
    return juntos.reset_index()


def unidades_de_custo(df: pd.DataFrame, coluna_viagens: str, rotas_aereas: set[str]) -> pd.Series:
    """Unidade de custo para a decomposição: viagens (rodoviário) ou peças (aéreo, tarifa por peça).

    Assim, no aéreo, o efeito eficiência é nulo e toda variação de custo unitário é efeito tarifa.
    """
    return df[coluna_viagens].where(~df["route_id"].isin(rotas_aereas), df["volume"])


def _transporte_por_rota(plano: pd.DataFrame) -> pd.DataFrame:
    aereas = set(plano.loc[plano["route_type"] == "AIR", "route_id"])
    p = plano.assign(trips=unidades_de_custo(plano, "total_trips", aereas))
    return p.groupby("route_id").agg(volume=("volume", "sum"), trips=("trips", "sum"),
                                     cost=("transport_cost", "sum")).reset_index()


def ponte_orcamento(plano_base: pd.DataFrame, linhas_base: pd.DataFrame,
                    plano_alvo: pd.DataFrame, linhas_alvo: pd.DataFrame) -> dict:
    """Ponte (waterfall) entre dois orçamentos (Q-BUD-02). Os passos somam exatamente a variação."""
    efeitos = decompor_por_chave(_transporte_por_rota(plano_base), _transporte_por_rota(plano_alvo), ["route_id"])
    tb, ta = totais(linhas_base), totais(linhas_alvo)
    comp_b, comp_a = tb["by_component"], ta["by_component"]
    passos = [
        ("base_final_budget", tb["final_budget"]),
        ("volume_effect", float(efeitos["volume_effect"].sum())),
        ("efficiency_effect", float(efeitos["efficiency_effect"].sum())),
        ("rate_effect", float(efeitos["rate_effect"].sum())),
        ("extras_change", comp_a.get("EXTRAS", 0.0) - comp_b.get("EXTRAS", 0.0)),
        ("tax_credit_change", comp_a.get("TAX_CREDIT", 0.0) - comp_b.get("TAX_CREDIT", 0.0)),
        ("adjustments_change", ta["adjustments"] - tb["adjustments"]),
    ]
    soma = sum(v for _, v in passos)
    residuo = ta["final_budget"] - soma
    return {
        "steps": [{"step": k, "amount_brl": v} for k, v in passos] + [{"step": "target_final_budget", "amount_brl": ta["final_budget"]}],
        "residual": residuo,
        "by_route": efeitos.sort_values("variance", key=abs, ascending=False).reset_index(drop=True),
    }


def estimar_custo_loja_nova(dados: DadosRede, plano: pd.DataFrame, uf: str, pecas_semanais: float) -> dict:
    """Estimativa de custo anual para servir uma loja nova numa UF (Q-BUD-05).

    Usa o custo por peça médio das rotas da UF no plano (custo médio, não marginal).
    """
    rotas_uf = dados["tn_routes"].query("uf == @uf")["route_id"]
    sub = plano[plano["route_id"].isin(rotas_uf)]
    if sub.empty or sub["volume"].sum() == 0:
        raise ValueError(f"Sem rotas com volume na UF {uf}")
    cpp = float(sub["transport_cost"].sum() / sub["volume"].sum())
    anual = pecas_semanais * 52
    return {"uf": uf, "reference_cost_per_piece": cpp, "annual_pieces": anual, "estimated_annual_cost": anual * cpp,
            "method": "Average cost per piece of the state's routes in the plan; a marginal-cost estimate may be lower if spare capacity exists.",
            "routes_used": rotas_uf.tolist()}
