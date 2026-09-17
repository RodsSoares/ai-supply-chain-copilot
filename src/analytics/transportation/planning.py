"""Analytics de planejamento do domínio Transportation."""

from src.database.connection import conectar_banco

from src.decision.transportation.planning_policy import (
    calcular_cenarios_planejamento,
    calcular_metricas_alternativa,
    classificar_perfil_rota,
    gerar_viagens_planejadas,
    obter_frequencia_alvo,
    selecionar_alternativa,
)


def buscar_alternativas_veiculo(route_id: str) -> list[dict]:
    """Busca veículos elegíveis e tarifas vigentes para uma rota."""
    with conectar_banco() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                o.route_id,
                v.vehicle_type_id,
                v.vehicle_name,
                v.capacity_pieces,
                r.rate_per_trip
            FROM route_vehicle_options AS o
            JOIN vehicle_types AS v
                ON v.vehicle_type_id = o.vehicle_type_id
            JOIN route_vehicle_rates AS r
                ON r.route_id = o.route_id
                AND r.vehicle_type_id = o.vehicle_type_id
            WHERE o.route_id = ?
            ORDER BY v.capacity_pieces
            """,
            (route_id,),
        ).fetchall()

    return [dict(linha) for linha in linhas]


def analisar_alternativas_planejamento(
    route_id: str,
    week_start: str,
) -> list[dict]:
    """Calcula as alternativas de planejamento para uma rota e semana."""
    with conectar_banco() as conexao:
        contexto = conexao.execute(
            """
            SELECT
                f.forecast_pieces,
                r.distance_km
            FROM demand_forecast AS f
            JOIN routes AS r
                ON r.route_id = f.route_id
            WHERE f.route_id = ?
              AND f.week_start = ?
            """,
            (route_id, week_start),
        ).fetchone()

    if contexto is None:
        raise ValueError(
            f"Forecast não encontrado para rota {route_id} "
            f"na semana {week_start}."
        )

    route_profile = classificar_perfil_rota(contexto["distance_km"])
    target_frequency = obter_frequencia_alvo(route_profile)

    alternativas_veiculo = buscar_alternativas_veiculo(route_id)

    resultados = []

    for alternativa in alternativas_veiculo:
        metricas = calcular_metricas_alternativa(
            forecast_pieces=contexto["forecast_pieces"],
            capacity_pieces=alternativa["capacity_pieces"],
            rate_per_trip=alternativa["rate_per_trip"],
            target_frequency=target_frequency,
        )

        resultados.append(
            {
                "route_id": route_id,
                "week_start": week_start,
                "route_profile": route_profile,
                "forecast_pieces": contexto["forecast_pieces"],
                "vehicle_type_id": alternativa["vehicle_type_id"],
                "vehicle_name": alternativa["vehicle_name"],
                "capacity_pieces": alternativa["capacity_pieces"],
                "rate_per_trip": alternativa["rate_per_trip"],
                **metricas,
            }
        )

    return resultados


def analisar_cenarios_planejamento(
    route_id: str,
    week_start: str,
) -> list[dict]:
    """Compara cenários econômico e de serviço por veículo elegível."""
    with conectar_banco() as conexao:
        contexto = conexao.execute(
            """
            SELECT
                f.forecast_pieces,
                r.distance_km
            FROM demand_forecast AS f
            JOIN routes AS r
                ON r.route_id = f.route_id
            WHERE f.route_id = ?
              AND f.week_start = ?
            """,
            (route_id, week_start),
        ).fetchone()

    if contexto is None:
        raise ValueError(
            f"Forecast não encontrado para rota {route_id} "
            f"na semana {week_start}."
        )

    route_profile = classificar_perfil_rota(contexto["distance_km"])
    target_frequency = obter_frequencia_alvo(route_profile)
    alternativas_veiculo = buscar_alternativas_veiculo(route_id)

    resultados = []

    for alternativa in alternativas_veiculo:
        cenarios = calcular_cenarios_planejamento(
            forecast_pieces=contexto["forecast_pieces"],
            capacity_pieces=alternativa["capacity_pieces"],
            rate_per_trip=alternativa["rate_per_trip"],
            target_frequency=target_frequency,
        )

        resultados.append(
            {
                "route_id": route_id,
                "week_start": week_start,
                "route_profile": route_profile,
                "target_frequency": target_frequency,
                "forecast_pieces": contexto["forecast_pieces"],
                "vehicle_type_id": alternativa["vehicle_type_id"],
                "vehicle_name": alternativa["vehicle_name"],
                "capacity_pieces": alternativa["capacity_pieces"],
                "rate_per_trip": alternativa["rate_per_trip"],
                **cenarios,
            }
        )

    return resultados


def selecionar_plano(
    route_id: str,
    week_start: str,
) -> dict:
    """Seleciona o plano para uma rota e semana."""
    alternativas = analisar_alternativas_planejamento(
        route_id=route_id,
        week_start=week_start,
    )

    return selecionar_alternativa(alternativas)


def gerar_plano_planejado(
    route_id: str,
    week_start: str,
) -> list[dict]:
    """Seleciona o plano e gera suas viagens individuais."""
    plano = selecionar_plano(
        route_id=route_id,
        week_start=week_start,
    )

    return gerar_viagens_planejadas(plano)


def salvar_viagens_planejadas(
    viagens: list[dict],
) -> None:
    """Persiste viagens planejadas no banco."""
    if not viagens:
        return

    with conectar_banco() as conexao:
        conexao.executemany(
            """
            INSERT INTO planned_trips (
                trip_id,
                week_start,
                route_id,
                vehicle_type_id,
                planned_pieces,
                planned_capacity,
                planned_cost
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    viagem["trip_id"],
                    viagem["week_start"],
                    viagem["route_id"],
                    viagem["vehicle_type_id"],
                    viagem["planned_pieces"],
                    viagem["planned_capacity"],
                    viagem["planned_cost"],
                )
                for viagem in viagens
            ],
        )