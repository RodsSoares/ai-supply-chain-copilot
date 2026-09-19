"""Análises SQL determinísticas do domínio Transportation."""

from src.database.connection import conectar_banco


def analisar_operacao_forecast() -> list[dict]:
    """
    Retorna a operação planejada necessária para atender ao forecast.

    Grão da saída:
        uma linha por route_id + week_start.
    """
    query = """
        SELECT
            f.route_id,
            f.week_start,
            f.forecast_pieces,
            v.vehicle_type_id,
            v.vehicle_name,
            COUNT(p.trip_id) AS planned_trips,
            SUM(p.planned_capacity) AS offered_capacity,
            SUM(p.planned_cost) AS planned_cost,
            ROUND(
                CAST(f.forecast_pieces AS REAL)
                / SUM(p.planned_capacity),
                4
            ) AS utilization,
            ROUND(
                SUM(p.planned_cost)
                / CAST(f.forecast_pieces AS REAL),
                4
            ) AS cost_per_piece
        FROM demand_forecast AS f
        JOIN planned_trips AS p
            ON p.route_id = f.route_id
            AND p.week_start = f.week_start
        JOIN vehicle_types AS v
            ON v.vehicle_type_id = p.vehicle_type_id
        GROUP BY
            f.route_id,
            f.week_start,
            f.forecast_pieces,
            v.vehicle_type_id,
            v.vehicle_name
        ORDER BY
            f.week_start,
            f.route_id
    """

    with conectar_banco() as conexao:
        linhas = conexao.execute(query).fetchall()

    return [dict(linha) for linha in linhas]


def analisar_eficiencia_economica() -> list[dict]:
    """
    Analisa a eficiência econômica das operações rota-semana.

    A CTE consolida primeiro o planejamento no grão rota + semana.
    O SELECT final calcula e ordena os indicadores econômicos.
    """
    query = """
        WITH operacao_base AS (
            SELECT
                f.route_id,
                f.week_start,
                f.forecast_pieces,
                v.vehicle_type_id,
                v.vehicle_name,
                COUNT(p.trip_id) AS planned_trips,
                SUM(p.planned_capacity) AS offered_capacity,
                SUM(p.planned_cost) AS planned_cost
            FROM demand_forecast AS f
            JOIN planned_trips AS p
                ON p.route_id = f.route_id
                AND p.week_start = f.week_start
            JOIN vehicle_types AS v
                ON v.vehicle_type_id = p.vehicle_type_id
            GROUP BY
                f.route_id,
                f.week_start,
                f.forecast_pieces,
                v.vehicle_type_id,
                v.vehicle_name
        )

        SELECT
            route_id,
            week_start,
            forecast_pieces,
            vehicle_type_id,
            vehicle_name,
            planned_trips,
            offered_capacity,
            planned_cost,
            ROUND(
                CAST(forecast_pieces AS REAL)
                / offered_capacity,
                4
            ) AS utilization,
            ROUND(
                planned_cost
                / CAST(forecast_pieces AS REAL),
                4
            ) AS cost_per_piece
        FROM operacao_base
        ORDER BY
            cost_per_piece DESC,
            utilization ASC,
            week_start,
            route_id
    """

    with conectar_banco() as conexao:
        linhas = conexao.execute(query).fetchall()

    return [dict(linha) for linha in linhas]


def analisar_evolucao_semanal() -> list[dict]:
    """
    Analisa a evolução semanal da operação por rota.

    Mantém o grão rota + semana e compara cada semana
    com a semana anterior da mesma rota.
    """
    query = """
        WITH operacao_base AS (
            SELECT
                f.route_id,
                f.week_start,
                f.forecast_pieces,
                SUM(p.planned_capacity) AS offered_capacity,
                SUM(p.planned_cost) AS planned_cost
            FROM demand_forecast AS f
            JOIN planned_trips AS p
                ON p.route_id = f.route_id
                AND p.week_start = f.week_start
            GROUP BY
                f.route_id,
                f.week_start,
                f.forecast_pieces
        ),

        indicadores AS (
            SELECT
                route_id,
                week_start,
                forecast_pieces,
                ROUND(
                    CAST(forecast_pieces AS REAL)
                    / offered_capacity,
                    4
                ) AS utilization,
                ROUND(
                    planned_cost
                    / CAST(forecast_pieces AS REAL),
                    4
                ) AS cost_per_piece
            FROM operacao_base
        ),

        comparacao_temporal AS (
            SELECT
                route_id,
                week_start,
                forecast_pieces,
                utilization,
                cost_per_piece,

                LAG(forecast_pieces) OVER (
                    PARTITION BY route_id
                    ORDER BY week_start
                ) AS previous_forecast_pieces,

                LAG(utilization) OVER (
                    PARTITION BY route_id
                    ORDER BY week_start
                ) AS previous_utilization,

                LAG(cost_per_piece) OVER (
                    PARTITION BY route_id
                    ORDER BY week_start
                ) AS previous_cost_per_piece

            FROM indicadores
        )

        SELECT
            route_id,
            week_start,
            forecast_pieces,
            utilization,
            cost_per_piece,
            previous_forecast_pieces,
            previous_utilization,
            previous_cost_per_piece,

            forecast_pieces
                - previous_forecast_pieces
                AS forecast_change,

            ROUND(
                utilization - previous_utilization,
                4
            ) AS utilization_change,

            ROUND(
                cost_per_piece - previous_cost_per_piece,
                4
            ) AS cost_per_piece_change

        FROM comparacao_temporal
        ORDER BY
            route_id,
            week_start
    """

    with conectar_banco() as conexao:
        linhas = conexao.execute(query).fetchall()

    return [dict(linha) for linha in linhas]


def analisar_participacao_custo_rede() -> list[dict]:
    """
    Analisa a participação de cada operação rota-semana
    no custo planejado total da rede.

    Mantém o grão rota + semana.
    """
    query = """
        WITH operacao_base AS (
            SELECT
                p.route_id,
                p.week_start,
                SUM(p.planned_cost) AS planned_cost
            FROM planned_trips AS p
            GROUP BY
                p.route_id,
                p.week_start
        )

        SELECT
            route_id,
            week_start,
            planned_cost,

            SUM(planned_cost) OVER () AS network_total_cost,

            ROUND(
                planned_cost
                / SUM(planned_cost) OVER (),
                4
            ) AS network_cost_share

        FROM operacao_base
        ORDER BY
            network_cost_share DESC,
            route_id,
            week_start
    """

    with conectar_banco() as conexao:
        linhas = conexao.execute(query).fetchall()

    return [dict(linha) for linha in linhas]

def analisar_ranking_custo_semanal() -> list[dict]:
    """Ranqueia as operações de maior custo dentro de cada semana."""
    query = """
        WITH operacao_base AS (
            SELECT
                p.route_id,
                p.week_start,
                SUM(p.planned_cost) AS planned_cost
            FROM planned_trips AS p
            GROUP BY
                p.route_id,
                p.week_start
        )

        SELECT
            route_id,
            week_start,
            planned_cost,
            RANK() OVER (
                PARTITION BY week_start
                ORDER BY planned_cost DESC
            ) AS weekly_cost_rank
        FROM operacao_base
        ORDER BY
            week_start,
            weekly_cost_rank,
            route_id
    """

    with conectar_banco() as conexao:
        linhas = conexao.execute(query).fetchall()

    return [dict(linha) for linha in linhas]


def analisar_concentracao_custo_rede() -> list[dict]:
    """Calcula participação individual e acumulada no custo planejado da rede."""
    query = """
        WITH operacao_base AS (
            SELECT
                p.route_id,
                p.week_start,
                SUM(p.planned_cost) AS planned_cost
            FROM planned_trips AS p
            GROUP BY
                p.route_id,
                p.week_start
        )

        SELECT
            route_id,
            week_start,
            planned_cost,
            SUM(planned_cost) OVER () AS network_total_cost,
            ROUND(
                planned_cost / SUM(planned_cost) OVER (),
                4
            ) AS network_cost_share,
            SUM(planned_cost) OVER (
                ORDER BY planned_cost DESC, route_id, week_start
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumulative_cost,
            ROUND(
                SUM(planned_cost) OVER (
                    ORDER BY planned_cost DESC, route_id, week_start
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) / SUM(planned_cost) OVER (),
                4
            ) AS cumulative_cost_share
        FROM operacao_base
        ORDER BY
            planned_cost DESC,
            route_id,
            week_start
    """

    with conectar_banco() as conexao:
        linhas = conexao.execute(query).fetchall()

    return [dict(linha) for linha in linhas]


def analisar_tendencia_recente() -> list[dict]:
    """Calcula médias móveis de três semanas por rota sem alterar o grão."""
    query = """
        WITH operacao_base AS (
            SELECT
                f.route_id,
                f.week_start,
                f.forecast_pieces,
                SUM(p.planned_capacity) AS offered_capacity,
                SUM(p.planned_cost) AS planned_cost
            FROM demand_forecast AS f
            JOIN planned_trips AS p
                ON p.route_id = f.route_id
                AND p.week_start = f.week_start
            GROUP BY
                f.route_id,
                f.week_start,
                f.forecast_pieces
        ),

        indicadores AS (
            SELECT
                route_id,
                week_start,
                forecast_pieces,
                CAST(forecast_pieces AS REAL) / offered_capacity AS utilization,
                planned_cost / CAST(forecast_pieces AS REAL) AS cost_per_piece
            FROM operacao_base
        )

        SELECT
            route_id,
            week_start,
            forecast_pieces,
            ROUND(utilization, 4) AS utilization,
            ROUND(cost_per_piece, 4) AS cost_per_piece,
            ROUND(
                AVG(forecast_pieces) OVER (
                    PARTITION BY route_id
                    ORDER BY week_start
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                ),
                2
            ) AS rolling_3w_forecast,
            ROUND(
                AVG(utilization) OVER (
                    PARTITION BY route_id
                    ORDER BY week_start
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                ),
                4
            ) AS rolling_3w_utilization,
            ROUND(
                AVG(cost_per_piece) OVER (
                    PARTITION BY route_id
                    ORDER BY week_start
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                ),
                4
            ) AS rolling_3w_cost_per_piece
        FROM indicadores
        ORDER BY
            route_id,
            week_start
    """

    with conectar_banco() as conexao:
        linhas = conexao.execute(query).fetchall()

    return [dict(linha) for linha in linhas]


def analisar_mudancas_operacionais() -> list[dict]:
    """Detecta mudanças de veículo, viagens ou capacidade entre semanas da rota."""
    query = """
        WITH operacao_base AS (
            SELECT
                p.route_id,
                p.week_start,
                p.vehicle_type_id,
                COUNT(p.trip_id) AS planned_trips,
                SUM(p.planned_capacity) AS offered_capacity,
                SUM(p.planned_cost) AS planned_cost
            FROM planned_trips AS p
            GROUP BY
                p.route_id,
                p.week_start,
                p.vehicle_type_id
        ),

        comparacao_temporal AS (
            SELECT
                route_id,
                week_start,
                vehicle_type_id,
                planned_trips,
                offered_capacity,
                planned_cost,
                LAG(vehicle_type_id) OVER (
                    PARTITION BY route_id
                    ORDER BY week_start
                ) AS previous_vehicle_type_id,
                LAG(planned_trips) OVER (
                    PARTITION BY route_id
                    ORDER BY week_start
                ) AS previous_planned_trips,
                LAG(offered_capacity) OVER (
                    PARTITION BY route_id
                    ORDER BY week_start
                ) AS previous_offered_capacity
            FROM operacao_base
        )

        SELECT
            route_id,
            week_start,
            vehicle_type_id,
            planned_trips,
            offered_capacity,
            planned_cost,
            previous_vehicle_type_id,
            previous_planned_trips,
            previous_offered_capacity,
            CASE
                WHEN previous_vehicle_type_id IS NULL THEN 'INITIAL'
                WHEN vehicle_type_id <> previous_vehicle_type_id THEN 'VEHICLE_CHANGE'
                WHEN planned_trips <> previous_planned_trips THEN 'TRIP_COUNT_CHANGE'
                WHEN offered_capacity <> previous_offered_capacity THEN 'CAPACITY_CHANGE'
                ELSE 'STABLE'
            END AS operational_event
        FROM comparacao_temporal
        ORDER BY
            route_id,
            week_start
    """

    with conectar_banco() as conexao:
        linhas = conexao.execute(query).fetchall()

    return [dict(linha) for linha in linhas]


def analisar_pressao_custo_rede() -> list[dict]:
    """Combina relevância no custo da rede e ranking de custo dentro da semana."""
    query = """
        WITH operacao_base AS (
            SELECT
                p.route_id,
                p.week_start,
                SUM(p.planned_cost) AS planned_cost
            FROM planned_trips AS p
            GROUP BY
                p.route_id,
                p.week_start
        )

        SELECT
            route_id,
            week_start,
            planned_cost,
            SUM(planned_cost) OVER () AS network_total_cost,
            ROUND(
                planned_cost / SUM(planned_cost) OVER (),
                4
            ) AS network_cost_share,
            RANK() OVER (
                PARTITION BY week_start
                ORDER BY planned_cost DESC
            ) AS weekly_cost_rank,
            RANK() OVER (
                ORDER BY planned_cost DESC
            ) AS network_cost_rank
        FROM operacao_base
        ORDER BY
            network_cost_rank,
            route_id,
            week_start
    """

    with conectar_banco() as conexao:
        linhas = conexao.execute(query).fetchall()

    return [dict(linha) for linha in linhas]


def analisar_resumo_executivo_semanal() -> list[dict]:
    """Resume a rede por semana e compara os KPIs com a semana anterior."""
    query = """
        WITH forecast_semanal AS (
            SELECT
                week_start,
                SUM(forecast_pieces) AS forecast_pieces
            FROM demand_forecast
            GROUP BY week_start
        ),

        plano_semanal AS (
            SELECT
                week_start,
                COUNT(trip_id) AS planned_trips,
                SUM(planned_capacity) AS offered_capacity,
                SUM(planned_cost) AS planned_cost
            FROM planned_trips
            GROUP BY week_start
        ),

        indicadores AS (
            SELECT
                f.week_start,
                f.forecast_pieces,
                p.planned_trips,
                p.offered_capacity,
                p.planned_cost,
                CAST(f.forecast_pieces AS REAL)
                    / p.offered_capacity AS utilization,
                p.planned_cost
                    / CAST(f.forecast_pieces AS REAL) AS cost_per_piece
            FROM forecast_semanal AS f
            JOIN plano_semanal AS p
                ON p.week_start = f.week_start
        ),

        comparacao_temporal AS (
            SELECT
                week_start,
                forecast_pieces,
                planned_trips,
                offered_capacity,
                planned_cost,
                utilization,
                cost_per_piece,
                LAG(forecast_pieces) OVER (
                    ORDER BY week_start
                ) AS previous_forecast_pieces,
                LAG(planned_cost) OVER (
                    ORDER BY week_start
                ) AS previous_planned_cost,
                LAG(utilization) OVER (
                    ORDER BY week_start
                ) AS previous_utilization,
                LAG(cost_per_piece) OVER (
                    ORDER BY week_start
                ) AS previous_cost_per_piece
            FROM indicadores
        )

        SELECT
            week_start,
            forecast_pieces,
            planned_trips,
            offered_capacity,
            planned_cost,
            ROUND(utilization, 4) AS utilization,
            ROUND(cost_per_piece, 4) AS cost_per_piece,
            previous_forecast_pieces,
            previous_planned_cost,
            ROUND(previous_utilization, 4) AS previous_utilization,
            ROUND(previous_cost_per_piece, 4) AS previous_cost_per_piece,
            forecast_pieces - previous_forecast_pieces AS forecast_change,
            planned_cost - previous_planned_cost AS planned_cost_change,
            ROUND(
                utilization - previous_utilization,
                4
            ) AS utilization_change,
            ROUND(
                cost_per_piece - previous_cost_per_piece,
                4
            ) AS cost_per_piece_change
        FROM comparacao_temporal
        ORDER BY week_start
    """

    with conectar_banco() as conexao:
        linhas = conexao.execute(query).fetchall()

    return [dict(linha) for linha in linhas]