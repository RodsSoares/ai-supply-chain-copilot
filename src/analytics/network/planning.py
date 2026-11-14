"""Motor de planejamento da rede (v2.3): capacidade, frequência, transbordo e what-if."""

from __future__ import annotations

import json
from functools import lru_cache

import numpy as np
import pandas as pd

from src.analytics.network.repository import DadosRede
from src.decision.network import planning_policy as politica
from src.decision.network.parameters import ParametrosCenario


# ---------------------------------------------------------------------------
# Entradas
# ---------------------------------------------------------------------------

def parametros_cenario(dados: DadosRede, scenario_id: str, overrides: list[dict] | None = None) -> ParametrosCenario:
    dados.cenario(scenario_id)  # valida existência
    return ParametrosCenario(scenario_id, dados.parametros(scenario_id), overrides or [])


def semanas_do_ano(dados: DadosRede, ano: int) -> pd.DataFrame:
    cal = dados["tn_calendar"]
    return cal[cal["iso_year"] == ano].copy()


def volume_planejamento(dados: DadosRede, scenario_id: str, params: ParametrosCenario) -> pd.DataFrame:
    """Volume semanal por rota a partir da versão de forecast do cenário (× multiplicadores)."""
    cenario = dados.cenario(scenario_id)
    versao = params.valor("forecast_version", padrao=cenario["forecast_version"])
    fc = dados["tn_forecast"]
    fc = fc[fc["forecast_version"] == versao]
    if fc.empty:
        raise ValueError(f"Forecast {versao} não encontrado para o cenário {scenario_id}")
    semanas = semanas_do_ano(dados, int(cenario["plan_year"]))
    vol = fc.merge(dados.loja_rota, on="store_id").groupby(["route_id", "week_start"])["forecast_pieces"].sum()
    grade = pd.MultiIndex.from_product([dados["tn_routes"]["route_id"], semanas["week_start"]], names=["route_id", "week_start"])
    vol = vol.reindex(grade, fill_value=0).rename("volume").reset_index()

    tem_multiplicador = any(o.get("parameter_key") == "volume_multiplier" for o in params.overrides) or (
        (dados.parametros(scenario_id)["parameter_key"] == "volume_multiplier").any()
    )
    if tem_multiplicador:
        dc_rota = dados.rotas["dc_id"]
        vol["volume"] = [
            v * params.multiplicador_volume(ws, route_id=r, dc_id=dc_rota[r])
            for r, ws, v in vol[["route_id", "week_start", "volume"]].itertuples(index=False)
        ]
    vol["forecast_version"] = versao
    return vol


class TabelaTarifas:
    """Tarifas vigentes por rota × veículo × semana, com reajustes do cenário."""

    def __init__(self, dados: DadosRede, params: ParametrosCenario):
        self.tarifas = {k: g.sort_values("effective_from") for k, g in dados["tn_rates"].groupby(["route_id", "vehicle_type_id"])}
        self.params = params
        self.carrier = dados.rotas["carrier_id"]
        self._fator = lru_cache(maxsize=None)(self.params.fator_reajuste)

    def tarifa(self, route_id: str, vehicle_type_id: str, data: str) -> tuple[float, float, str]:
        if (route_id, vehicle_type_id) not in self.tarifas:
            raise ValueError(f"Veículo {vehicle_type_id} não elegível para a rota {route_id}")
        g = self.tarifas[(route_id, vehicle_type_id)]
        vigente = g[g["effective_from"] <= data].iloc[-1]
        fator = self._fator(self.carrier[route_id], data)
        return float(vigente["rate_value"]) * fator, float(vigente["spot_premium"]), vigente["rate_basis"]


# ---------------------------------------------------------------------------
# Planejamento
# ---------------------------------------------------------------------------

def planejar_cenario(dados: DadosRede, scenario_id: str, overrides: list[dict] | None = None,
                     rotas: list[str] | None = None) -> pd.DataFrame:
    """Plano semanal por rota para o ano do cenário (equivalente a tn_planned_trips)."""
    params = parametros_cenario(dados, scenario_id, overrides)
    volume = volume_planejamento(dados, scenario_id, params)
    tarifas = TabelaTarifas(dados, params)
    cal = dados.calendario
    linhas = []
    for route_id, grupo in volume.groupby("route_id", sort=True):
        if rotas and route_id not in rotas:
            continue
        rota = dados.rotas.loc[route_id]
        vid = params.veiculo(route_id) or dados.veiculo_default[route_id]
        cap = dados.veiculos.loc[vid, "capacity_pieces"]
        grupo = grupo.sort_values("week_start").merge(
            dados["tn_calendar"][["week_start", "week_idx", "retail_year", "retail_month", "season_flag"]], on="week_start")

        # volume por semana de atendimento (rotas de semana alternada consolidam pares)
        if rota["route_type"] == "ALTERNATING_WEEK":
            atendido, acumulado = [], 0.0
            for i, (idx, v) in enumerate(zip(grupo["week_idx"], grupo["volume"])):
                ultimo = i == len(grupo) - 1
                if idx % 2 == 0 and not ultimo:
                    acumulado += v
                    atendido.append(np.nan)
                else:
                    atendido.append(v + acumulado)
                    acumulado = 0.0
            grupo["service_volume"] = atendido
        else:
            grupo["service_volume"] = grupo["volume"]

        rota_info = {
            "route_profile": rota["route_profile"],
            "route_type": rota["route_type"],
            "vehicle_type_id": vid,
            "frequency_min": params.frequencia_minima(rota["route_profile"], route_id),
            "frequency_basis": params.base_frequencia(route_id),
        }

        frequencias = {}
        if rota["route_type"] != "AIR":
            for (ano, mes), g in grupo.dropna(subset=["service_volume"]).groupby(["retail_year", "retail_month"]):
                necessidades = [politica.viagens_necessarias(v, cap) for v in g["service_volume"]]
                frequencias[(ano, mes)] = politica.frequencia_mensal(necessidades, rota_info["frequency_basis"], rota_info["frequency_min"])

        for s in grupo.itertuples(index=False):
            if np.isnan(s.service_volume):
                continue
            tarifa, premio, basis = tarifas.tarifa(route_id, vid, s.week_start)
            if rota["route_type"] == "AIR":
                plano = politica.planejar_semana_aerea(s.service_volume, tarifa)
            else:
                plano = politica.planejar_semana(s.service_volume, cap, frequencias[(s.retail_year, s.retail_month)], tarifa, premio)
            linhas.append(
                {
                    "scenario_id": scenario_id,
                    "week_start": s.week_start,
                    "retail_year": s.retail_year,
                    "retail_month": s.retail_month,
                    "route_id": route_id,
                    "dc_id": rota["dc_id"],
                    "carrier_id": rota["carrier_id"],
                    "route_type": rota["route_type"],
                    "route_profile": rota["route_profile"],
                    "vehicle_type_id": vid,
                    "capacity_pieces": cap,
                    "distance_km": rota["distance_km"],
                    "volume": s.service_volume,
                    "rate": tarifa,
                    **plano,
                    "explanation_json": json.dumps(politica.explicar(rota_info, {"season_flag": s.season_flag}, plano)),
                }
            )
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# Indicadores
# ---------------------------------------------------------------------------

def _indicadores(df: pd.DataFrame, chaves: list[str]) -> pd.DataFrame:
    agg = df.groupby(chaves, dropna=False).agg(
        volume=("volume", "sum"),
        planned_trips=("planned_trips", "sum"),
        overflow_trips=("overflow_trips", "sum"),
        total_trips=("total_trips", "sum"),
        capacity=("planned_capacity", "sum"),
        freight_cost=("freight_cost", "sum"),
        overflow_cost=("overflow_cost", "sum"),
        transport_cost=("transport_cost", "sum"),
        weeks=("week_start", "nunique"),
        overflow_weeks=("overflow_trips", lambda s: int((s > 0).sum())),
        km=("distance_km", "first"),
    ).reset_index()
    agg["cost_per_piece"] = agg["transport_cost"] / agg["volume"].replace(0, np.nan)
    agg["cost_per_trip"] = agg["transport_cost"] / agg["total_trips"].replace(0, np.nan)
    agg["utilization"] = agg["volume"] / agg["capacity"].replace(0, np.nan)
    agg["overflow_rate"] = agg["overflow_weeks"] / agg["weeks"]
    return agg


def resumo_por_rota(plano: pd.DataFrame) -> pd.DataFrame:
    r = _indicadores(plano, ["route_id", "dc_id", "route_type", "route_profile", "vehicle_type_id"])
    rodoviario = plano[plano["route_type"] != "AIR"]
    km = rodoviario.assign(km_total=rodoviario["total_trips"] * rodoviario["distance_km"]).groupby("route_id")["km_total"].sum()
    r["cost_per_km"] = r["route_id"].map(r.set_index("route_id")["transport_cost"] / km)
    return r.drop(columns=["km"])


def resumo_rede(plano: pd.DataFrame) -> dict:
    r = _indicadores(plano.assign(_k=1), ["_k"]).iloc[0]
    rodoviario = plano[plano["route_type"] != "AIR"]
    return {
        "scenario_id": plano["scenario_id"].iloc[0],
        "volume": float(r["volume"]),
        "total_trips": int(r["total_trips"]),
        "overflow_trips": int(r["overflow_trips"]),
        "transport_cost": float(r["transport_cost"]),
        "overflow_cost": float(r["overflow_cost"]),
        "cost_per_piece": float(r["cost_per_piece"]),
        "road_utilization": float(rodoviario["volume"].sum() / rodoviario["planned_capacity"].sum()),
        "overflow_rate": float((rodoviario["overflow_trips"] > 0).mean()),
    }


def analisar_transbordo(plano: pd.DataFrame) -> pd.DataFrame:
    """Semanas com transbordo e o custo spot associado (Q-PLN-02)."""
    t = plano[plano["overflow_trips"] > 0]
    return t[["route_id", "week_start", "volume", "required_trips", "planned_trips", "overflow_trips", "overflow_cost"]] \
        .sort_values("overflow_cost", ascending=False).reset_index(drop=True)


def carga_cds(dados: DadosRede, plano: pd.DataFrame) -> pd.DataFrame:
    """Fator de carga semanal por CD (Q-PLN-05)."""
    carga = plano.groupby(["dc_id", "week_start"])["volume"].sum().reset_index()
    cap = dados["tn_dcs"].set_index("dc_id")["weekly_dispatch_capacity_pieces"]
    carga["load_factor"] = carga["volume"] / carga["dc_id"].map(cap)
    return carga


def comparar_planos(base: pd.DataFrame, alternativo: pd.DataFrame, chaves: list[str] | None = None) -> pd.DataFrame:
    """Diferença de indicadores entre dois planos (alternativo − base)."""
    chaves = chaves or ["route_id"]
    b = _indicadores(base, chaves).set_index(chaves)
    a = _indicadores(alternativo, chaves).set_index(chaves)
    metricas = ["volume", "total_trips", "overflow_trips", "transport_cost", "overflow_cost", "cost_per_piece", "utilization"]
    saida = pd.concat({"base": b[metricas], "scenario": a[metricas]}, axis=1)
    for m in metricas:
        saida[("delta", m)] = saida[("scenario", m)] - saida[("base", m)]
    saida.columns = [f"{x}_{y}" for x, y in saida.columns]
    return saida.reset_index()


def rodar_what_if(dados: DadosRede, scenario_id: str, overrides: list[dict]) -> dict:
    """Executa um what-if sem alterar o cenário base (Q-PLN-04, Q-BUD-03)."""
    base = planejar_cenario(dados, scenario_id)
    alternativo = planejar_cenario(dados, scenario_id, overrides)
    rb, ra = resumo_rede(base), resumo_rede(alternativo)
    return {
        "scenario_id": scenario_id,
        "overrides": overrides,
        "base": rb,
        "what_if": ra,
        "delta": {k: ra[k] - rb[k] for k in rb if isinstance(rb[k], (int, float))},
        "by_route": comparar_planos(base, alternativo),
    }


def avaliar_alternativas(dados: DadosRede, scenario_id: str, route_id: str) -> pd.DataFrame:
    """Custo anual da rota para cada veículo elegível × frequência mínima (atual e atual − 1)."""
    opcoes = dados["tn_route_vehicle_options"]
    elegiveis = opcoes[opcoes["route_id"] == route_id]["vehicle_type_id"].tolist()
    params = parametros_cenario(dados, scenario_id)
    rota = dados.rotas.loc[route_id]
    freq_atual = params.frequencia_minima(rota["route_profile"], route_id)
    frequencias = sorted({freq_atual, max(1, freq_atual - 1)}, reverse=True)
    linhas = []
    for vid in elegiveis:
        for freq in frequencias:
            overrides = [{"parameter_key": "vehicle", "scope": f"ROUTE:{route_id}", "value": vid},
                         {"parameter_key": "frequency_min", "scope": f"ROUTE:{route_id}", "value": freq}]
            plano = planejar_cenario(dados, scenario_id, overrides, rotas=[route_id])
            r = _indicadores(plano, ["route_id"]).iloc[0]
            linhas.append({"route_id": route_id, "vehicle_type_id": vid, "frequency_min": freq,
                           "is_current": vid == dados.veiculo_default[route_id] and freq == freq_atual,
                           "service_change": "NONE" if freq == freq_atual else "LOWER_MIN_FREQUENCY",
                           "transport_cost": r["transport_cost"], "cost_per_piece": r["cost_per_piece"],
                           "utilization": r["utilization"], "overflow_trips": int(r["overflow_trips"]),
                           "total_trips": int(r["total_trips"])})
    return pd.DataFrame(linhas).sort_values("transport_cost").reset_index(drop=True)


def candidatos_consolidacao(dados: DadosRede, scenario_id: str, plano: pd.DataFrame | None = None) -> pd.DataFrame:
    """Rotas abaixo do limite de ocupação e a alternativa de menor custo (Q-PLN-03).

    Alternativas que reduzem a frequência mínima são sinalizadas como mudança de
    nível de serviço: a decisão é humana.
    """
    params = parametros_cenario(dados, scenario_id)
    limite = params.numero("utilization_threshold", padrao=0.60)
    plano = planejar_cenario(dados, scenario_id) if plano is None else plano
    resumo = resumo_por_rota(plano)
    baixos = resumo[(resumo["route_type"] != "AIR") & (resumo["volume"] > 0) & (resumo["utilization"] < limite)]
    linhas = []
    for r in baixos.itertuples(index=False):
        alternativas = avaliar_alternativas(dados, scenario_id, r.route_id)
        atual = alternativas[alternativas["is_current"]].iloc[0]
        melhor = alternativas.iloc[0]
        linhas.append({
            "route_id": r.route_id, "route_profile": r.route_profile,
            "current_vehicle": atual["vehicle_type_id"], "current_frequency_min": int(atual["frequency_min"]),
            "current_utilization": atual["utilization"], "current_cost": atual["transport_cost"],
            "best_vehicle": melhor["vehicle_type_id"], "best_frequency_min": int(melhor["frequency_min"]),
            "best_utilization": melhor["utilization"], "best_cost": melhor["transport_cost"],
            "annual_saving": atual["transport_cost"] - melhor["transport_cost"],
            "service_change": melhor["service_change"], "utilization_threshold": limite,
        })
    if not linhas:
        return pd.DataFrame()
    return pd.DataFrame(linhas).sort_values("annual_saving", ascending=False).reset_index(drop=True)


def rotas_sem_demanda(plano: pd.DataFrame) -> list[str]:
    """Rotas sem volume no ano do plano (ex.: única loja fechada) — candidatas a desativação."""
    r = plano.groupby("route_id")["volume"].sum()
    return r[r == 0].index.tolist()
