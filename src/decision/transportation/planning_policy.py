"""Políticas determinísticas de planejamento de Transportation."""

import math


def calcular_viagens_necessarias(
    forecast_pieces: int,
    capacity_pieces: int,
    target_frequency: int,
) -> int:
    """Calcula viagens necessárias considerando capacidade e frequência-alvo."""
    trips_by_capacity = math.ceil(forecast_pieces / capacity_pieces)

    return max(trips_by_capacity, target_frequency)


def classificar_perfil_rota(distance_km: float) -> str:
    """Classifica uma rota em SHORT, MEDIUM ou LONG pela distância."""
    if distance_km < 300:
        return "SHORT"

    if distance_km <= 800:
        return "MEDIUM"

    return "LONG"


def obter_frequencia_alvo(route_profile: str) -> int:
    """Retorna a frequência semanal desejada por perfil de rota."""
    if route_profile == "SHORT":
        return 2

    if route_profile == "MEDIUM":
        return 2

    if route_profile == "LONG":
        return 2

    raise ValueError(f"Perfil de rota inválido: {route_profile}")


def calcular_metricas_alternativa(
    forecast_pieces: int,
    capacity_pieces: int,
    rate_per_trip: float,
    target_frequency: int,
) -> dict:
    """Calcula as métricas de uma alternativa de planejamento."""
    planned_trips = calcular_viagens_necessarias(
        forecast_pieces=forecast_pieces,
        capacity_pieces=capacity_pieces,
        target_frequency=target_frequency,
    )

    planned_capacity = planned_trips * capacity_pieces
    planned_cost = planned_trips * rate_per_trip
    utilization = forecast_pieces / planned_capacity
    cost_per_piece = planned_cost / forecast_pieces

    return {
        "planned_trips": planned_trips,
        "planned_capacity": planned_capacity,
        "planned_cost": planned_cost,
        "utilization": utilization,
        "cost_per_piece": cost_per_piece,
    }


def selecionar_alternativa(
    alternativas: list[dict],
) -> dict:
    """Seleciona a alternativa de menor R$/peça."""
    if not alternativas:
        raise ValueError("Nenhuma alternativa disponível para seleção.")

    selecionada = min(
        alternativas,
        key=lambda alternativa: (
            alternativa["cost_per_piece"],
            alternativa["planned_cost"],
            alternativa["planned_capacity"],
        ),
    )

    return {
        **selecionada,
        "selection_reason": "LOWEST_COST_PER_PIECE",
    }


def gerar_viagens_planejadas(plano: dict) -> list[dict]:
    """Converte um plano selecionado em viagens individuais."""
    planned_trips = plano["planned_trips"]
    forecast_pieces = plano["forecast_pieces"]

    base_pieces = forecast_pieces // planned_trips
    remainder = forecast_pieces % planned_trips

    week_id = plano["week_start"].replace("-", "")

    viagens = []

    for trip_number in range(1, planned_trips + 1):
        extra_piece = 1 if trip_number <= remainder else 0
        planned_pieces = base_pieces + extra_piece

        trip_id = (
            f"{week_id}-"
            f"{plano['route_id']}-"
            f"{trip_number:02d}"
        )

        viagens.append(
            {
                "trip_id": trip_id,
                "week_start": plano["week_start"],
                "route_id": plano["route_id"],
                "vehicle_type_id": plano["vehicle_type_id"],
                "planned_pieces": planned_pieces,
                "planned_capacity": plano["capacity_pieces"],
                "planned_cost": plano["rate_per_trip"],
            }
        )

    return viagens


def calcular_viagens_por_capacidade(
    forecast_pieces: int,
    capacity_pieces: int,
) -> int:
    """Calcula o número mínimo de viagens exigido pela capacidade."""
    return math.ceil(forecast_pieces / capacity_pieces)


def calcular_cenarios_planejamento(
    forecast_pieces,
    capacity_pieces,
    rate_per_trip,
    target_frequency,
):
    """Compara os cenários econômico e de serviço para uma alternativa."""

    economic_trips = calcular_viagens_por_capacidade(
        forecast_pieces=forecast_pieces,
        capacity_pieces=capacity_pieces,
    )

    service_trips = max(
        economic_trips,
        target_frequency,
    )

    economic_capacity = economic_trips * capacity_pieces
    economic_cost = economic_trips * rate_per_trip

    service_capacity = service_trips * capacity_pieces
    service_cost = service_trips * rate_per_trip

    economic_cost_per_piece = economic_cost / forecast_pieces
    service_cost_per_piece = service_cost / forecast_pieces

    economic = {
        "planned_trips": economic_trips,
        "offered_capacity": economic_capacity,
        "utilization": forecast_pieces / economic_capacity,
        "planned_cost": economic_cost,
        "cost_per_piece": economic_cost_per_piece,
    }

    service = {
        "planned_trips": service_trips,
        "offered_capacity": service_capacity,
        "utilization": forecast_pieces / service_capacity,
        "planned_cost": service_cost,
        "cost_per_piece": service_cost_per_piece,
    }

    service_premium = (
        service_cost_per_piece / economic_cost_per_piece
    ) - 1

    return {
        "economic": economic,
        "service": service,
        "service_premium": service_premium,
    }