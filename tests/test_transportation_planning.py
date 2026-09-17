"""Testes de integração do planejamento de Transportation."""

import pytest

import src.database.connection as connection
from src.analytics.transportation.planning import (
    analisar_alternativas_planejamento,
    gerar_plano_planejado,
    salvar_viagens_planejadas,
    selecionar_plano,
)
from src.database.create_transportation_tables import (
    criar_tabelas_transportation,
)


@pytest.fixture
def banco_planejamento(tmp_path, monkeypatch):
    """Cria um banco temporário com cenário mínimo de planejamento."""
    banco_teste = tmp_path / "transportation_planning_test.db"

    monkeypatch.setattr(
        connection,
        "CAMINHO_BANCO",
        banco_teste,
    )

    criar_tabelas_transportation()

    with connection.conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO routes (
                route_id,
                origin_id,
                destination_id,
                distance_km
            )
            VALUES ('R001', 'DC01', 'DEST001', 95)
            """
        )

        conexao.execute(
            """
            INSERT INTO vehicle_types (
                vehicle_type_id,
                vehicle_name,
                capacity_pieces
            )
            VALUES
                ('V001', 'VAN', 2500),
                ('V002', 'LIGHT_TRUCK', 5000),
                ('V003', 'MEDIUM_TRUCK', 10000)
            """
        )

        conexao.execute(
            """
            INSERT INTO route_vehicle_options (
                route_id,
                vehicle_type_id
            )
            VALUES
                ('R001', 'V001'),
                ('R001', 'V002'),
                ('R001', 'V003')
            """
        )

        conexao.execute(
            """
            INSERT INTO route_vehicle_rates (
                route_id,
                vehicle_type_id,
                effective_from,
                rate_per_trip
            )
            VALUES
                ('R001', 'V001', '2026-01-01', 650.0),
                ('R001', 'V002', '2026-01-01', 850.0),
                ('R001', 'V003', '2026-01-01', 1150.0)
            """
        )

        conexao.execute(
            """
            INSERT INTO demand_forecast (
                week_start,
                route_id,
                forecast_pieces
            )
            VALUES ('2026-08-24', 'R001', 7200)
            """
        )

        conexao.commit()

    return banco_teste


def test_analisar_alternativas_planejamento(banco_planejamento):
    """Testa a geração das alternativas de planejamento."""
    resultados = analisar_alternativas_planejamento(
        route_id="R001",
        week_start="2026-08-24",
    )

    assert len(resultados) == 3

    assert resultados[0]["vehicle_name"] == "VAN"
    assert resultados[0]["planned_trips"] == 3
    assert resultados[0]["planned_capacity"] == 7500
    assert resultados[0]["planned_cost"] == 1950.0
    assert resultados[0]["utilization"] == 0.96
    assert resultados[0]["cost_per_piece"] == 1950.0 / 7200


def test_selecionar_plano(banco_planejamento):
    """Testa a seleção end-to-end do plano."""
    resultado = selecionar_plano(
        route_id="R001",
        week_start="2026-08-24",
    )

    assert resultado["route_id"] == "R001"
    assert resultado["week_start"] == "2026-08-24"
    assert resultado["route_profile"] == "SHORT"

    assert resultado["vehicle_type_id"] == "V002"
    assert resultado["vehicle_name"] == "LIGHT_TRUCK"

    assert resultado["planned_trips"] == 2
    assert resultado["planned_capacity"] == 10000
    assert resultado["planned_cost"] == 1700.0
    assert resultado["utilization"] == 0.72
    assert resultado["cost_per_piece"] == 1700.0 / 7200

    assert resultado["selection_reason"] == "LOWEST_COST_PER_PIECE"


def test_salvar_viagens_planejadas(banco_planejamento):
    """Testa geração e persistência das viagens planejadas."""
    viagens = gerar_plano_planejado(
        route_id="R001",
        week_start="2026-08-24",
    )

    salvar_viagens_planejadas(viagens)

    with connection.conectar_banco() as conexao:
        resultado = conexao.execute(
            """
            SELECT
                COUNT(*) AS trip_count,
                SUM(planned_pieces) AS total_pieces,
                SUM(planned_capacity) AS total_capacity,
                SUM(planned_cost) AS total_cost
            FROM planned_trips
            WHERE route_id = ?
              AND week_start = ?
            """,
            ("R001", "2026-08-24"),
        ).fetchone()

    assert resultado["trip_count"] == 2
    assert resultado["total_pieces"] == 7200
    assert resultado["total_capacity"] == 10000
    assert resultado["total_cost"] == 1700.0
    