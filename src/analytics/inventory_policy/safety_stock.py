"""Política dinâmica de estoque (v2.6): estoque de segurança, ponto de pedido e nível máximo.

Fórmulas (revisão contínua, demanda e lead time independentes e aproximadamente normais):

    SS  = z(NS) × sqrt(LT × σd² + d̄² × σLT²)
    ROP = d̄ × LT + SS
    MAX = ROP + d̄ × cobertura_de_revisão          (order-up-to)

d̄ e σd são semanais (janela móvel), LT e σLT em semanas, NS = nível de serviço
por classe ABC. Com σLT = 0 a fórmula se reduz a z × σd × √LT.

A política estática do cadastro (estoque_minimo / estoque_maximo) é preservada
e comparada lado a lado; nenhuma recomendação existente é alterada.
"""

from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np
import pandas as pd


ACOES = ("REPOR", "TRATAR EXCESSO", "SEM AÇÃO")


def z_servico(nivel_servico: float) -> float:
    if not 0.5 <= nivel_servico < 1:
        raise ValueError("Nível de serviço deve estar em [0.5, 1)")
    return NormalDist().inv_cdf(nivel_servico)


def estoque_seguranca(z: float, demanda_media: float, desvio_demanda: float, lead_time: float, desvio_lead_time: float) -> float:
    return z * math.sqrt(lead_time * desvio_demanda ** 2 + demanda_media ** 2 * desvio_lead_time ** 2)


def estatisticas_demanda(demanda: pd.DataFrame, janela: int = 52) -> pd.DataFrame:
    """Média, desvio, CV e participação de semanas sem demanda (últimas `janela` semanas)."""
    semanas = sorted(demanda["week_start"].unique())[-janela:]
    d = demanda[demanda["week_start"].isin(semanas)]
    stats = d.groupby("sku")["demand_units"].agg(mean_weekly="mean", std_weekly="std",
                                                 zero_share=lambda s: float((s == 0).mean())).reset_index()
    stats["cv"] = stats["std_weekly"] / stats["mean_weekly"].replace(0, np.nan)
    stats["window_weeks"] = len(semanas)
    return stats


def acao_estatica(estoque: pd.Series, minimo: pd.Series, maximo: pd.Series) -> pd.Series:
    """Mesma regra da política atual do Copilot (min/max do cadastro)."""
    acao = pd.Series("SEM AÇÃO", index=estoque.index)
    acao[estoque < minimo] = "REPOR"
    acao[estoque > maximo] = "TRATAR EXCESSO"
    return acao


def calcular_politica(erp: pd.DataFrame, demanda: pd.DataFrame, config: dict,
                      niveis_servico: dict[str, float] | None = None) -> pd.DataFrame:
    """Política dinâmica por SKU, lado a lado com a política estática."""
    pol = config["policy"]
    niveis = {**pol["service_level_by_abc"], **(niveis_servico or {})}
    stats = estatisticas_demanda(demanda, pol["stats_window_weeks"])
    df = erp.merge(stats, on="sku", how="left", validate="one_to_one")
    if df["mean_weekly"].isna().any():
        faltantes = df.loc[df["mean_weekly"].isna(), "sku"].tolist()[:5]
        raise ValueError(f"SKUs sem histórico de demanda: {faltantes}")

    df["service_level"] = df["classe_abc"].map(niveis)
    df["z"] = df["service_level"].map(z_servico)
    df["lead_time_weeks"] = df["lead_time_dias"] / config["days_per_week"]
    df["lead_time_std_weeks"] = df["lead_time_weeks"] * config["lead_time_cv"]
    df["safety_stock"] = [
        math.ceil(estoque_seguranca(r.z, r.mean_weekly, r.std_weekly, r.lead_time_weeks, r.lead_time_std_weeks))
        for r in df.itertuples(index=False)
    ]
    df["reorder_point"] = np.ceil(df["mean_weekly"] * df["lead_time_weeks"]).astype(int) + df["safety_stock"]
    df["order_up_to"] = df["reorder_point"] + np.ceil(df["mean_weekly"] * pol["review_cover_weeks"]).astype(int)
    df["coverage_weeks"] = df["estoque_atual"] / df["mean_weekly"].replace(0, np.nan)

    df["static_action"] = acao_estatica(df["estoque_atual"], df["estoque_minimo"], df["estoque_maximo"])
    df["dynamic_action"] = "SEM AÇÃO"
    df.loc[df["estoque_atual"] <= df["reorder_point"], "dynamic_action"] = "REPOR"
    df.loc[df["estoque_atual"] > df["order_up_to"] * pol["excess_tolerance"], "dynamic_action"] = "TRATAR EXCESSO"
    df["action_changed"] = df["static_action"] != df["dynamic_action"]

    df["dynamic_order_qty"] = np.where(df["dynamic_action"] == "REPOR", df["order_up_to"] - df["estoque_atual"], 0)
    df["dynamic_excess_qty"] = np.where(df["dynamic_action"] == "TRATAR EXCESSO", df["estoque_atual"] - df["order_up_to"], 0)
    df["safety_stock_value"] = df["safety_stock"] * df["custo_unitario"]
    df["dynamic_target_avg_units"] = df["safety_stock"] + df["mean_weekly"] * pol["review_cover_weeks"] / 2
    df["static_target_avg_units"] = (df["estoque_minimo"] + df["estoque_maximo"]) / 2
    return df


def comparar_politicas(pol: pd.DataFrame) -> dict:
    """Resumo da mudança de recomendações e do capital alvo (Q-INV-02)."""
    matriz = pd.crosstab(pol["static_action"], pol["dynamic_action"]).reindex(index=ACOES, columns=ACOES, fill_value=0)
    custo = pol["custo_unitario"]
    return {
        "skus": int(len(pol)),
        "actions_changed": int(pol["action_changed"].sum()),
        "transition_matrix": {s: {d: int(matriz.loc[s, d]) for d in ACOES} for s in ACOES},
        "static_counts": pol["static_action"].value_counts().to_dict(),
        "dynamic_counts": pol["dynamic_action"].value_counts().to_dict(),
        "current_inventory_value": float((pol["estoque_atual"] * custo).sum()),
        "static_target_avg_inventory_value": float((pol["static_target_avg_units"] * custo).sum()),
        "dynamic_target_avg_inventory_value": float((pol["dynamic_target_avg_units"] * custo).sum()),
        "safety_stock_value": float(pol["safety_stock_value"].sum()),
        "dynamic_order_value": float((pol["dynamic_order_qty"] * custo).sum()),
        "dynamic_excess_value": float((pol["dynamic_excess_qty"] * custo).sum()),
        "by_abc": pol.groupby("classe_abc").agg(
            skus=("sku", "count"), service_level=("service_level", "first"),
            safety_stock_value=("safety_stock_value", "sum"), actions_changed=("action_changed", "sum"),
        ).reset_index().to_dict("records"),
    }


def cobertura_historica(pol: pd.DataFrame, demanda: pd.DataFrame, janela: int = 52) -> pd.DataFrame:
    """Nível de serviço de ciclo empírico: % de janelas de lead time em que a demanda ≤ ROP.

    Usa as últimas `janela` semanas; a demanda no lead time é aproximada por somas
    móveis de ceil(LT) semanas, escaladas para LT.
    """
    semanas = sorted(demanda["week_start"].unique())[-janela:]
    d = demanda[demanda["week_start"].isin(semanas)].sort_values(["sku", "week_start"])
    series = {sku: g["demand_units"].to_numpy(float) for sku, g in d.groupby("sku")}
    linhas = []
    for r in pol.itertuples(index=False):
        y = series[r.sku]
        k = max(1, math.ceil(r.lead_time_weeks))
        somas = np.convolve(y, np.ones(k), "valid") * (r.lead_time_weeks / k)
        linhas.append({"sku": r.sku, "classe_abc": r.classe_abc, "service_level": r.service_level,
                       "empirical_cycle_service_level": float((somas <= r.reorder_point).mean()), "windows": len(somas)})
    out = pd.DataFrame(linhas)
    out["gap_to_target"] = out["empirical_cycle_service_level"] - out["service_level"]
    return out


def curva_servico_capital(erp: pd.DataFrame, demanda: pd.DataFrame, config: dict,
                          niveis: tuple[float, ...] = (0.90, 0.93, 0.95, 0.97, 0.98, 0.99)) -> pd.DataFrame:
    """Capital em estoque de segurança para um mesmo nível de serviço em todas as classes."""
    linhas = []
    for ns in niveis:
        pol = calcular_politica(erp, demanda, config, {"A": ns, "B": ns, "C": ns})
        linhas.append({"service_level": ns, "safety_stock_value": float(pol["safety_stock_value"].sum()),
                       "reorder_alerts": int((pol["dynamic_action"] == "REPOR").sum())})
    return pd.DataFrame(linhas)
