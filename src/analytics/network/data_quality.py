"""Checagens de qualidade e reconciliação da rede sintética (v2.1).

Retornam estruturas simples (listas/dicts) para que testes, relatórios e o
Copilot consumam o mesmo resultado determinístico.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from src.analytics.network.repository import DadosRede


def checar_integridade_referencial(dados: DadosRede) -> list[str]:
    """Lista FKs que não resolvem (vazia = OK)."""
    problemas = []
    pares = [
        ("tn_stores", "primary_dc_id", "tn_dcs", "dc_id"),
        ("tn_routes", "dc_id", "tn_dcs", "dc_id"),
        ("tn_routes", "carrier_id", "tn_carriers", "carrier_id"),
        ("tn_route_stops", "route_id", "tn_routes", "route_id"),
        ("tn_route_stops", "store_id", "tn_stores", "store_id"),
        ("tn_route_vehicle_options", "vehicle_type_id", "tn_vehicles", "vehicle_type_id"),
        ("tn_demand_history", "store_id", "tn_stores", "store_id"),
        ("tn_demand_history", "week_start", "tn_calendar", "week_start"),
        ("tn_forecast", "store_id", "tn_stores", "store_id"),
        ("tn_trips_actual", "route_id", "tn_routes", "route_id"),
        ("tn_parameters", "scenario_id", "tn_scenarios", "scenario_id"),
        ("tn_management_adjustments", "scenario_id", "tn_scenarios", "scenario_id"),
    ]
    for filha, fk, pai, pk in pares:
        orfaos = set(dados[filha][fk].dropna()) - set(dados[pai][pk])
        if orfaos:
            problemas.append(f"{filha}.{fk} -> {pai}.{pk}: {sorted(orfaos)[:5]}")
    return problemas


def checar_cobertura_tarifas(dados: DadosRede) -> list[str]:
    """Toda combinação rota × veículo elegível precisa de tarifa vigente em toda semana."""
    problemas = []
    tarifas = dados["tn_rates"]
    semanas = dados["tn_calendar"]["week_start"]
    for (rid, vid), grupo in tarifas.groupby(["route_id", "vehicle_type_id"]):
        for ws in semanas:
            vigentes = grupo[(grupo["effective_from"] <= ws) & (grupo["effective_to"].isna() | (grupo["effective_to"] >= ws))]
            if ws >= "2024-01-01" and len(vigentes) != 1:
                problemas.append(f"{rid}/{vid} {ws}: {len(vigentes)} tarifas vigentes")
                break
    opcoes = set(map(tuple, dados["tn_route_vehicle_options"][["route_id", "vehicle_type_id"]].to_numpy()))
    com_tarifa = set(map(tuple, tarifas[["route_id", "vehicle_type_id"]].drop_duplicates().to_numpy()))
    for faltante in sorted(opcoes - com_tarifa):
        problemas.append(f"{faltante}: sem tarifa")
    return problemas


def checar_atribuicao_lojas(dados: DadosRede) -> list[str]:
    """Cada loja deve pertencer a exatamente uma rota."""
    contagem = dados["tn_route_stops"].groupby("store_id")["route_id"].nunique()
    problemas = [f"{s}: {n} rotas" for s, n in contagem.items() if n != 1]
    sem_rota = set(dados["tn_stores"]["store_id"]) - set(contagem.index)
    problemas += [f"{s}: sem rota" for s in sorted(sem_rota)]
    return problemas


def checar_calendario(dados: DadosRede) -> list[str]:
    problemas = []
    for ws, js in dados["tn_calendar"][["week_start", "civil_month_share_json"]].itertuples(index=False):
        if abs(sum(json.loads(js).values()) - 1) > 1e-4:
            problemas.append(f"{ws}: participação civil != 1")
    semanas_ano = dados["tn_calendar"].groupby("iso_year")["iso_week"].max()
    for ano, maximo in semanas_ano.items():
        if maximo not in (52, 53):
            problemas.append(f"{ano}: {maximo} semanas")
    return problemas


def reconciliar_viagens_historico(dados: DadosRede) -> dict:
    """Σ peças das viagens realizadas = Σ expedição histórica das lojas da rota no período."""
    viagens = dados["tn_trips_actual"]
    inicio, fim = viagens["week_start"].min(), viagens["week_start"].max()
    hist = dados["tn_demand_history"]
    hist = hist[(hist["week_start"] >= inicio) & (hist["week_start"] <= fim)]
    esperado = hist.merge(dados.loja_rota, on="store_id").groupby("route_id")["pieces_shipped"].sum()
    realizado = viagens.groupby("route_id")["pieces"].sum()
    comparacao = pd.concat([esperado.rename("history"), realizado.rename("trips")], axis=1).fillna(0)
    divergentes = comparacao[comparacao["history"] != comparacao["trips"]]
    return {
        "period": [inicio, fim],
        "routes_checked": int(len(comparacao)),
        "routes_divergent": divergentes.index.tolist(),
        "total_history": int(comparacao["history"].sum()),
        "total_trips": int(comparacao["trips"].sum()),
    }


def checar_capacidade_viagens(dados: DadosRede, tolerancia: float = 1e-9) -> list[str]:
    """Nenhuma viagem rodoviária pode exceder a capacidade do veículo."""
    v = dados["tn_trips_actual"].merge(dados["tn_vehicles"][["vehicle_type_id", "capacity_pieces"]], on="vehicle_type_id")
    v = v[v["capacity_pieces"].notna()]
    excedidas = v[v["pieces"] > v["capacity_pieces"] * (1 + tolerancia)]
    return excedidas["trip_id"].tolist()


def detectar_anomalias_demanda(dados: DadosRede, z_limite: float = 6.0) -> dict:
    """Detecta expedição zero, linhas faltantes e outliers no histórico."""
    hist = dados["tn_demand_history"]
    cal = dados["tn_calendar"][["week_start", "week_idx"]]
    zeros = int((hist["pieces_shipped"] == 0).sum())

    # Faltantes: semanas sem linha entre a primeira e a última semana de cada série
    h = hist.merge(cal, on="week_start")
    chaves = ["store_id", "brand", "channel"]
    faixa = h.groupby(chaves)["week_idx"].agg(["min", "max", "count"])
    faltantes = int((faixa["max"] - faixa["min"] + 1 - faixa["count"]).sum())

    # Outliers: z-score robusto contra a mediana móvel da série
    h = h.sort_values(chaves + ["week_idx"])
    mediana = h.groupby(chaves)["pieces_shipped"].transform(lambda s: s.rolling(9, center=True, min_periods=3).median())
    desvio = (h["pieces_shipped"] - mediana).abs()
    mad = desvio.groupby([h[c] for c in chaves]).transform("median").replace(0, np.nan)
    z = 0.6745 * (h["pieces_shipped"] - mediana) / mad
    outliers = int((z > z_limite).sum())
    return {"zero_shipments": zeros, "missing_rows": faltantes, "outliers": outliers}


def relatorio_qualidade(dados: DadosRede) -> dict:
    """Resumo completo usado por testes e pelo Copilot."""
    return {
        "referential_integrity": checar_integridade_referencial(dados),
        "rate_coverage": checar_cobertura_tarifas(dados),
        "store_assignment": checar_atribuicao_lojas(dados),
        "calendar": checar_calendario(dados),
        "trip_capacity": checar_capacidade_viagens(dados),
        "trip_reconciliation": reconciliar_viagens_historico(dados),
        "demand_anomalies": detectar_anomalias_demanda(dados),
    }
