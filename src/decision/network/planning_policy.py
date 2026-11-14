"""Política determinística de planejamento da rede (v2.3).

Frequência mensal fixa por rota (operação em ondas) + checagem semanal:
semanas cuja necessidade excede a frequência geram transbordo (overflow),
precificado em spot. Nenhum transbordo fica sem custo.
"""

from __future__ import annotations

import math

import numpy as np


BASES_FREQUENCIA = ("MEAN", "P75", "MAX")


def viagens_necessarias(volume: float, capacidade: float) -> int:
    """ceil(volume / capacidade); zero volume => zero viagens necessárias."""
    if capacidade <= 0:
        raise ValueError("Capacidade deve ser positiva")
    return math.ceil(volume / capacidade) if volume > 0 else 0


def arredondar(valor: float) -> int:
    """Arredondamento comercial (0.5 sobe), evitando o arredondamento bancário do Python."""
    return int(math.floor(valor + 0.5))


def frequencia_mensal(necessidades: list[int], base: str, minima: int) -> int:
    """Frequência semanal fixa para o mês a partir das necessidades semanais."""
    if base not in BASES_FREQUENCIA:
        raise ValueError(f"Base de frequência inválida: {base}")
    if not necessidades or sum(necessidades) == 0:
        return 0  # rota sem demanda no mês (ex.: loja fechada) não recebe frequência mínima
    if base == "MEAN":
        valor = arredondar(float(np.mean(necessidades)))
    elif base == "P75":
        valor = arredondar(float(np.quantile(necessidades, 0.75)))
    else:
        valor = max(necessidades)
    return max(minima, int(valor))


def planejar_semana(
    volume: float,
    capacidade: float,
    frequencia: int,
    tarifa: float,
    premio_spot: float,
) -> dict:
    """Plano de uma rota rodoviária numa semana de atendimento."""
    necessarias = viagens_necessarias(volume, capacidade)
    transbordo = max(0, necessarias - frequencia)
    total = frequencia + transbordo
    capacidade_total = total * capacidade
    custo_planejado = frequencia * tarifa
    custo_transbordo = transbordo * tarifa * premio_spot
    return {
        "required_trips": necessarias,
        "planned_trips": frequencia,
        "overflow_trips": transbordo,
        "total_trips": total,
        "planned_capacity": capacidade_total,
        "utilization": (volume / capacidade_total) if capacidade_total else 0.0,
        "freight_cost": custo_planejado,
        "overflow_cost": custo_transbordo,
        "transport_cost": custo_planejado + custo_transbordo,
    }


def planejar_semana_aerea(volume: float, tarifa_por_peca: float) -> dict:
    """Rotas aéreas: custo por peça, uma expedição semanal quando há volume."""
    viagens = 1 if volume > 0 else 0
    custo = volume * tarifa_por_peca
    return {
        "required_trips": viagens,
        "planned_trips": viagens,
        "overflow_trips": 0,
        "total_trips": viagens,
        "planned_capacity": np.nan,
        "utilization": np.nan,
        "freight_cost": custo,
        "overflow_cost": 0.0,
        "transport_cost": custo,
    }


def explicar(rota: dict, semana: dict, plano: dict) -> dict:
    """Explicação estruturada da decisão (RULE-002)."""
    motivos = []
    if plano["overflow_trips"]:
        motivos.append(
            f"Required {plano['required_trips']} trips but the monthly fixed frequency is {plano['planned_trips']}: "
            f"{plano['overflow_trips']} overflow trip(s) priced at spot."
        )
    if plano["planned_trips"] == rota["frequency_min"] and plano["required_trips"] < rota["frequency_min"]:
        motivos.append(f"Minimum service frequency for {rota['route_profile']} routes ({rota['frequency_min']}/week) applied.")
    if rota["route_type"] == "ALTERNATING_WEEK":
        motivos.append("Alternating-week route: two weeks of demand consolidated in each service week.")
    if not motivos:
        motivos.append("Monthly fixed frequency covers the weekly requirement.")
    return {
        "frequency_basis": rota["frequency_basis"],
        "frequency_min": rota["frequency_min"],
        "vehicle_type_id": rota["vehicle_type_id"],
        "season_flag": semana.get("season_flag"),
        "reasons": motivos,
    }
