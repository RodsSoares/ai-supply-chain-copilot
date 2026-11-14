"""Capacidades determinísticas da rede expostas ao Copilot (allow-list).

Cada capacidade recebe parâmetros simples, devolve um dicionário serializável
em JSON e nunca usa LLM. O LLM apenas escolhe a capacidade (intent) e explica
o resultado; todos os números vêm daqui.
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from src.analytics.network import budget, emissions, forecasting, planning, variance
from src.analytics.network.data_quality import relatorio_qualidade
from src.analytics.network.repository import DadosRede, carregar_de_banco, carregar_de_csv
from src.database.connection import conectar_banco


DIRETORIO_CSV = Path("data/synthetic/transportation/network")
MAX_REGISTROS = 15

_dados_injetados: DadosRede | None = None


def configurar_dados(dados: DadosRede | None) -> None:
    """Permite injetar dados (testes) e limpa os caches."""
    global _dados_injetados
    _dados_injetados = dados
    _plano.cache_clear()
    _orcamento.cache_clear()
    _backtest.cache_clear()


def _banco_tem_rede() -> bool:
    try:
        with conectar_banco() as conexao:
            return conexao.execute("SELECT 1 FROM sqlite_master WHERE name = 'tn_routes'").fetchone() is not None
    except Exception:
        return False


@lru_cache(maxsize=1)
def _dados_padrao() -> DadosRede:
    return carregar_de_banco() if _banco_tem_rede() else carregar_de_csv(DIRETORIO_CSV)


def obter_dados() -> DadosRede:
    return _dados_injetados if _dados_injetados is not None else _dados_padrao()


@lru_cache(maxsize=8)
def _plano(scenario_id: str) -> pd.DataFrame:
    return planning.planejar_cenario(obter_dados(), scenario_id)


@lru_cache(maxsize=8)
def _orcamento(scenario_id: str) -> pd.DataFrame:
    return budget.orcamento(obter_dados(), scenario_id, _plano(scenario_id))


@lru_cache(maxsize=1)
def _backtest() -> pd.DataFrame:
    return forecasting.backtest(obter_dados())


# ---------------------------------------------------------------------------
# Serialização
# ---------------------------------------------------------------------------

def _limpar(valor: Any) -> Any:
    if isinstance(valor, float):
        return None if math.isnan(valor) else round(valor, 4)
    if hasattr(valor, "item"):
        return _limpar(valor.item())
    if isinstance(valor, dict):
        return {k: _limpar(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_limpar(v) for v in valor]
    return valor


def _registros(df: pd.DataFrame, limite: int = MAX_REGISTROS) -> list[dict]:
    return _limpar(df.head(limite).to_dict("records"))


def _filtrar_rota(df: pd.DataFrame, route_id: str | None) -> pd.DataFrame:
    return df[df["route_id"] == route_id] if route_id and "route_id" in df.columns else df


# ---------------------------------------------------------------------------
# Capacidades
# ---------------------------------------------------------------------------

def plan_route_week(scenario_id: str = "BUDGET_2027", route_id: str | None = None, **_) -> dict:
    """Q-PLN-01 — plano por rota (viagens, veículo, ocupação, custo por peça)."""
    resumo = _filtrar_rota(planning.resumo_por_rota(_plano(scenario_id)), route_id)
    return {"capability": "plan_route_week", "scenario_id": scenario_id,
            "network": _limpar(planning.resumo_rede(_plano(scenario_id))),
            "routes": _registros(resumo.sort_values("transport_cost", ascending=False))}


def analyze_overflow(scenario_id: str = "BUDGET_2027", route_id: str | None = None, **_) -> dict:
    """Q-PLN-02 — semanas com transbordo e custo spot."""
    t = _filtrar_rota(planning.analisar_transbordo(_plano(scenario_id)), route_id)
    return {"capability": "analyze_overflow", "scenario_id": scenario_id, "overflow_weeks": int(len(t)),
            "overflow_trips": int(t["overflow_trips"].sum()), "overflow_cost": _limpar(float(t["overflow_cost"].sum())),
            "top_weeks": _registros(t)}


def find_consolidation_candidates(scenario_id: str = "BUDGET_2027", **_) -> dict:
    """Q-PLN-03 — rotas abaixo do limite de ocupação e alternativa de menor custo."""
    dados = obter_dados()
    plano = _plano(scenario_id)
    c = planning.candidatos_consolidacao(dados, scenario_id, plano)
    return {"capability": "find_consolidation_candidates", "scenario_id": scenario_id,
            "candidates": _registros(c), "routes_without_demand": planning.rotas_sem_demanda(plano),
            "note": "Alternatives that lower the minimum frequency change the service level and require human approval."}


def run_what_if(scenario_id: str = "BUDGET_2027", overrides: list[dict] | None = None, **_) -> dict:
    """Q-PLN-04 / Q-BUD-03 / Q-SUS-02 — what-if sobre o cenário (o cenário base não muda)."""
    if not overrides:
        raise ValueError("run_what_if requer ao menos um override")
    dados = obter_dados()
    base_plano = _plano(scenario_id)
    alt_plano = planning.planejar_cenario(dados, scenario_id, overrides)
    base_orc = _orcamento(scenario_id)
    alt_orc = budget.orcamento(dados, scenario_id, alt_plano, overrides)
    tb, ta = budget.totais(base_orc), budget.totais(alt_orc)
    eb = emissions.total_emissoes(emissions.emissoes_plano(dados, base_plano))
    ea = emissions.total_emissoes(emissions.emissoes_plano(dados, alt_plano))
    rb, ra = planning.resumo_rede(base_plano), planning.resumo_rede(alt_plano)
    return _limpar({
        "capability": "run_what_if", "scenario_id": scenario_id, "overrides": overrides,
        "plan": {"base": rb, "what_if": ra},
        "budget": {"base_final": tb["final_budget"], "what_if_final": ta["final_budget"],
                   "delta": ta["final_budget"] - tb["final_budget"]},
        "emissions": {"base_t_co2e": eb["t_co2e"], "what_if_t_co2e": ea["t_co2e"], "delta_t_co2e": ea["t_co2e"] - eb["t_co2e"]},
    })


def analyze_dc_load(scenario_id: str = "BUDGET_2027", **_) -> dict:
    """Q-PLN-05 — fator de carga dos CDs (pico e média)."""
    carga = planning.carga_cds(obter_dados(), _plano(scenario_id))
    r = carga.groupby("dc_id")["load_factor"].agg(["mean", "max"]).reset_index()
    pico = carga.loc[carga.groupby("dc_id")["load_factor"].idxmax(), ["dc_id", "week_start"]].rename(columns={"week_start": "peak_week"})
    return {"capability": "analyze_dc_load", "scenario_id": scenario_id, "dcs": _registros(r.merge(pico, on="dc_id"))}


def forecast_accuracy(forecast_version: str = "BUDGET_2026", level: str = "ROUTE", **_) -> dict:
    """Q-FCT-01/02 — acurácia (WAPE) e viés de uma versão de forecast."""
    dados = obter_dados()
    a = forecasting.acuracia_forecast(dados, forecast_version, level)
    total = forecasting.acuracia_forecast(dados, forecast_version, "NETWORK").iloc[0]
    agregado = float(a["abs_error"].sum() / a["actual"].sum())
    return {"capability": "forecast_accuracy", "forecast_version": forecast_version, "level": level,
            "network_bias": _limpar(float(total["bias"])), "wape_at_level": _limpar(agregado),
            "worst": _registros(a.sort_values("wape", ascending=False))}


def forecast_value_added(**_) -> dict:
    """Q-FCT-03 — modelos baseline vs. naïve sazonal (backtest)."""
    bt = _backtest()
    return {"capability": "forecast_value_added", "network": _registros(forecasting.resumo_rede_backtest(bt)),
            "by_route": _registros(forecasting.resumir_backtest(bt).sort_values("fva_vs_naive", ascending=False))}


def demand_variability(**_) -> dict:
    """Q-FCT-04 — lojas com demanda mais volátil (CV)."""
    return {"capability": "demand_variability", "stores": _registros(forecasting.variabilidade_demanda(obter_dados()))}


def budget_summary(scenario_id: str = "BUDGET_2027", by: str = "civil_month", **_) -> dict:
    """Q-BUD-01 — orçamento por mês / CD / rota e componente."""
    linhas = _orcamento(scenario_id)
    return {"capability": "budget_summary", "scenario_id": scenario_id, "totals": _limpar(budget.totais(linhas)),
            "table": _registros(budget.resumo_orcamento(linhas, por=by), limite=40)}


def budget_bridge(base_scenario_id: str = "PLAN_2026", target_scenario_id: str = "BUDGET_2027", **_) -> dict:
    """Q-BUD-02 — ponte volume / eficiência / tarifa / extras / créditos / ajustes."""
    ponte = budget.ponte_orcamento(_plano(base_scenario_id), _orcamento(base_scenario_id),
                                   _plano(target_scenario_id), _orcamento(target_scenario_id))
    return _limpar({"capability": "budget_bridge", "base": base_scenario_id, "target": target_scenario_id,
                    "steps": ponte["steps"], "residual": ponte["residual"], "top_routes": _registros(ponte["by_route"], 10)})


def adjustment_report(scenario_id: str = "BUDGET_2027", **_) -> dict:
    """Q-BUD-04 — ajustes gerenciais, motivos, aprovação e impacto."""
    linhas = _orcamento(scenario_id)
    t = budget.totais(linhas)
    return {"capability": "adjustment_report", "scenario_id": scenario_id,
            "model_budget": _limpar(t["model_budget"]), "final_budget": _limpar(t["final_budget"]),
            "adjustment_share": _limpar(t["adjustment_share"]),
            "adjustments": _registros(budget.relatorio_ajustes(obter_dados(), scenario_id, linhas))}


def new_store_cost_estimate(uf: str, weekly_pieces: float, scenario_id: str = "BUDGET_2027", **_) -> dict:
    """Q-BUD-05 — custo estimado para servir uma loja nova numa UF."""
    est = budget.estimar_custo_loja_nova(obter_dados(), _plano(scenario_id), uf, float(weekly_pieces))
    return _limpar({"capability": "new_store_cost_estimate", "scenario_id": scenario_id, **est})


def plan_vs_actual(scenario_id: str = "PLAN_2026", route_id: str | None = None, **_) -> dict:
    """Q-PRF-01 — plano vs. realizado com decomposição."""
    pv = variance.plano_vs_realizado(obter_dados(), scenario_id, _plano(scenario_id))
    return {"capability": "plan_vs_actual", "scenario_id": scenario_id, "total": _limpar(pv["total"]),
            "routes": _registros(_filtrar_rota(pv["detail"], route_id))}


def extras_analysis(**_) -> dict:
    """Q-PRF-02 — extras por motivo."""
    return {"capability": "extras_analysis", "reasons": _registros(variance.analise_extras(obter_dados()))}


def carrier_performance(**_) -> dict:
    """Q-PRF-03 — entregas no prazo por transportadora vs. meta."""
    return {"capability": "carrier_performance", "carriers": _registros(variance.desempenho_transportadoras(obter_dados()))}


def emissions_summary(scenario_id: str = "BUDGET_2027", route_id: str | None = None, **_) -> dict:
    """Q-SUS-01 — emissões estimadas por rota e por peça (fatores ilustrativos)."""
    e = emissions.emissoes_plano(obter_dados(), _plano(scenario_id))
    return {"capability": "emissions_summary", "scenario_id": scenario_id, "total": _limpar(emissions.total_emissoes(e)),
            "routes": _registros(_filtrar_rota(emissions.resumo_emissoes(e), route_id)),
            "note": "Emission factors are illustrative and must be replaced by an official source before real use."}


def data_quality_report(**_) -> dict:
    """Qualidade e reconciliação da base sintética."""
    return {"capability": "data_quality_report", **_limpar(relatorio_qualidade(obter_dados()))}


CAPACIDADES_NETWORK: dict[str, Callable[..., dict]] = {
    "plan_route_week": plan_route_week,
    "analyze_overflow": analyze_overflow,
    "find_consolidation_candidates": find_consolidation_candidates,
    "run_what_if": run_what_if,
    "analyze_dc_load": analyze_dc_load,
    "forecast_accuracy": forecast_accuracy,
    "forecast_value_added": forecast_value_added,
    "demand_variability": demand_variability,
    "budget_summary": budget_summary,
    "budget_bridge": budget_bridge,
    "adjustment_report": adjustment_report,
    "new_store_cost_estimate": new_store_cost_estimate,
    "plan_vs_actual": plan_vs_actual,
    "extras_analysis": extras_analysis,
    "carrier_performance": carrier_performance,
    "emissions_summary": emissions_summary,
    "data_quality_report": data_quality_report,
}


def executar_capacidade(nome: str, **parametros) -> dict:
    """Executa uma capacidade autorizada; nomes fora da allow-list são recusados."""
    if nome not in CAPACIDADES_NETWORK:
        raise ValueError(f"Capacidade de rede não autorizada: {nome}")
    return CAPACIDADES_NETWORK[nome](**parametros)
