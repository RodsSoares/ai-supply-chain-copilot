"""Estimativa de emissões de GEE (v2.5).

Rodoviário: litros = (2 × distância) × viagens / km_por_litro (ida e volta);
            kgCO2e = litros × fator do diesel.
Aéreo:      t·km = peças × peso_por_peça / 1000 × distância;
            kgCO2e = t·km × fator do frete aéreo.

Os fatores são ILUSTRATIVOS (tn_emission_factors) e devem ser substituídos
por uma fonte oficial antes de qualquer uso real.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.analytics.network.repository import DadosRede


def fatores(dados: DadosRede) -> dict[str, float]:
    f = dados["tn_emission_factors"].sort_values("valid_from").drop_duplicates("factor_key", keep="last")
    return dict(zip(f["factor_key"], f["value"].astype(float)))


def _calcular(dados: DadosRede, df: pd.DataFrame, coluna_viagens: str, coluna_volume: str) -> pd.DataFrame:
    fat = fatores(dados)
    rotas = dados.rotas
    veic = dados.veiculos
    df = df.copy()
    df["distance_km"] = df["route_id"].map(rotas["distance_km"])
    df["mode"] = df["vehicle_type_id"].map(veic["mode"])
    kmpl = df["vehicle_type_id"].map(veic["km_per_liter"]).astype(float)
    rodoviario = df["mode"] == "ROAD"
    df["fuel_liters"] = np.where(rodoviario, 2 * df["distance_km"] * df[coluna_viagens] / kmpl, 0.0)
    tonne_km = df[coluna_volume] * fat["PIECE_WEIGHT"] / 1000 * df["distance_km"]
    df["kg_co2e"] = np.where(rodoviario, df["fuel_liters"] * fat["DIESEL"], tonne_km * fat["AIR_FREIGHT"])
    return df


def emissoes_plano(dados: DadosRede, plano: pd.DataFrame) -> pd.DataFrame:
    return _calcular(dados, plano, "total_trips", "volume")


def emissoes_realizadas(dados: DadosRede, inicio: str | None = None, fim: str | None = None) -> pd.DataFrame:
    v = dados["tn_trips_actual"]
    if inicio:
        v = v[v["week_start"] >= inicio]
    if fim:
        v = v[v["week_start"] <= fim]
    v = v.assign(trips=1)
    return _calcular(dados, v, "trips", "pieces").rename(columns={"pieces": "volume"})


def resumo_emissoes(emissoes: pd.DataFrame, por: str = "route_id") -> pd.DataFrame:
    r = emissoes.groupby(por).agg(volume=("volume", "sum"), fuel_liters=("fuel_liters", "sum"), kg_co2e=("kg_co2e", "sum")).reset_index()
    r["t_co2e"] = r["kg_co2e"] / 1000
    r["kg_co2e_per_piece"] = r["kg_co2e"] / r["volume"].replace(0, np.nan)
    return r.sort_values("t_co2e", ascending=False).reset_index(drop=True)


def total_emissoes(emissoes: pd.DataFrame) -> dict:
    kg = float(emissoes["kg_co2e"].sum())
    vol = float(emissoes["volume"].sum())
    return {"t_co2e": kg / 1000, "kg_co2e_per_piece": kg / vol if vol else 0.0,
            "fuel_liters": float(emissoes["fuel_liters"].sum()),
            "air_share_of_emissions": float(emissoes.loc[emissoes["mode"] == "AIR", "kg_co2e"].sum() / kg) if kg else 0.0}
