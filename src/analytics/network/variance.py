"""Plano vs. realizado, extras e desempenho de transportadoras (v2.4)."""

from __future__ import annotations

import pandas as pd

from src.analytics.network import budget, planning
from src.analytics.network.repository import DadosRede


def realizado_semanal(dados: DadosRede, inicio: str, fim: str) -> pd.DataFrame:
    v = dados["tn_trips_actual"]
    v = v[(v["week_start"] >= inicio) & (v["week_start"] <= fim)]
    return v.groupby(["route_id", "week_start"]).agg(
        volume=("pieces", "sum"), trips=("trip_id", "count"), cost=("freight_cost", "sum"),
        extra_cost=("extra_cost", "sum"), overflow_trips=("trip_kind", lambda s: int((s == "OVERFLOW_SPOT").sum())),
    ).reset_index()


def plano_vs_realizado(dados: DadosRede, scenario_id: str = "PLAN_2026", plano: pd.DataFrame | None = None,
                       chaves: tuple[str, ...] = ("route_id",)) -> dict:
    """Variação de custo de transporte (frete + spot) com decomposição volume/eficiência/tarifa (Q-PRF-01).

    Compara apenas as semanas com realizado disponível.
    """
    plano = planning.planejar_cenario(dados, scenario_id) if plano is None else plano
    inicio = plano["week_start"].min()
    fim = min(plano["week_start"].max(), dados["tn_trips_actual"]["week_start"].max())
    p = plano[(plano["week_start"] >= inicio) & (plano["week_start"] <= fim)]
    p = p.rename(columns={"total_trips": "trips", "transport_cost": "cost"})
    r = realizado_semanal(dados, inicio, fim)
    for df in (p, r):
        df["dc_id"] = df["route_id"].map(dados.rotas["dc_id"])
        df["retail_month"] = df["week_start"].map(dados.calendario["retail_month"])

    aereas = set(dados["tn_routes"].query("route_type == 'AIR'")["route_id"])
    efeitos = budget.decompor_por_chave(
        p.assign(trips=budget.unidades_de_custo(p, "trips", aereas)),
        r.assign(trips=budget.unidades_de_custo(r, "trips", aereas)),
        list(chaves),
    )
    params = planning.parametros_cenario(dados, scenario_id)
    extras_plano = float((p["cost"] * params.numero("extras_rate", padrao=0.0)).sum())
    extras_real = float(r["extra_cost"].sum())
    total = {
        "period": [inicio, fim],
        "plan_cost": float(p["cost"].sum()),
        "actual_cost": float(r["cost"].sum()),
        "variance": float(r["cost"].sum() - p["cost"].sum()),
        "variance_pct": float(r["cost"].sum() / p["cost"].sum() - 1),
        "volume_effect": float(efeitos["volume_effect"].sum()),
        "efficiency_effect": float(efeitos["efficiency_effect"].sum()),
        "rate_effect": float(efeitos["rate_effect"].sum()),
        "plan_volume": float(p["volume"].sum()),
        "actual_volume": float(r["volume"].sum()),
        "plan_trips": int(p["trips"].sum()),
        "actual_trips": int(r["trips"].sum()),
        "plan_overflow_trips": int(p["overflow_trips"].sum()),
        "actual_overflow_trips": int(r["overflow_trips"].sum()),
        "plan_extras": extras_plano,
        "actual_extras": extras_real,
    }
    efeitos = efeitos.sort_values("variance", key=abs, ascending=False).reset_index(drop=True)
    efeitos["main_driver"] = efeitos[["volume_effect", "efficiency_effect", "rate_effect"]].abs().idxmax(axis=1)
    return {"total": total, "detail": efeitos}


def analise_extras(dados: DadosRede, inicio: str | None = None, fim: str | None = None) -> pd.DataFrame:
    """Custo de extras por motivo e participação sobre o frete (Q-PRF-02)."""
    v = dados["tn_trips_actual"]
    if inicio:
        v = v[v["week_start"] >= inicio]
    if fim:
        v = v[v["week_start"] <= fim]
    frete = v["freight_cost"].sum()
    e = v[v["extra_reason"] != "NONE"].groupby("extra_reason").agg(occurrences=("trip_id", "count"), extra_cost=("extra_cost", "sum"))
    e["share_of_freight"] = e["extra_cost"] / frete
    return e.sort_values("extra_cost", ascending=False).reset_index()


def desempenho_transportadoras(dados: DadosRede, por_mes: bool = False) -> pd.DataFrame:
    """Entregas no prazo por transportadora vs. meta (Q-PRF-03)."""
    v = dados["tn_trips_actual"].copy()
    chaves = ["carrier_id"]
    if por_mes:
        v["month"] = v["ship_date"].str[:7]
        chaves.append("month")
    d = v.groupby(chaves).agg(trips=("trip_id", "count"), on_time=("delivered_on_time", "sum")).reset_index()
    d["on_time_rate"] = d["on_time"] / d["trips"]
    d = d.merge(dados["tn_carriers"][["carrier_id", "on_time_target"]], on="carrier_id")
    d["gap_to_target"] = d["on_time_rate"] - d["on_time_target"]
    return d
