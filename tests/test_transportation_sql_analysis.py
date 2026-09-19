"""Testes das análises SQL do domínio Transportation."""

import pytest

import src.database.connection as connection
from src.analytics.transportation.planning import materializar_plano_completo
from src.analytics.transportation.sql_analysis import (
    analisar_concentracao_custo_rede,
    analisar_eficiencia_economica,
    analisar_evolucao_semanal,
    analisar_operacao_forecast,
    analisar_participacao_custo_rede,
    analisar_mudancas_operacionais,
    analisar_pressao_custo_rede,
    analisar_ranking_custo_semanal,
    analisar_resumo_executivo_semanal,
    analisar_tendencia_recente,
)
from src.database.create_transportation_tables import (
    criar_tabelas_transportation,
)


@pytest.fixture
def banco_sql_analysis(tmp_path, monkeypatch):
    """Cria banco temporário com cenário mínimo para análises SQL."""
    banco_teste = tmp_path / "transportation_sql_analysis_test.db"

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

    materializar_plano_completo()

    return banco_teste


def test_analisar_operacao_forecast(banco_sql_analysis):
    """Testa a consolidação SQL da operação planejada."""
    resultado = analisar_operacao_forecast()

    assert len(resultado) == 1

    linha = resultado[0]

    assert linha["route_id"] == "R001"
    assert linha["week_start"] == "2026-08-24"
    assert linha["forecast_pieces"] == 7200

    assert linha["vehicle_type_id"] == "V002"
    assert linha["vehicle_name"] == "LIGHT_TRUCK"

    assert linha["planned_trips"] == 2
    assert linha["offered_capacity"] == 10000
    assert linha["planned_cost"] == 1700.0

    assert linha["utilization"] == pytest.approx(0.72)
    assert linha["cost_per_piece"] == pytest.approx(
        1700 / 7200,
        abs=0.0001,
    )


def test_analisar_eficiencia_economica(banco_sql_analysis):
    """Testa a comparação e ordenação econômica entre operações."""

    with connection.conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO routes (
                route_id,
                origin_id,
                destination_id,
                distance_km
            )
            VALUES ('R002', 'DC01', 'DEST002', 180)
            """
        )

        conexao.execute(
            """
            INSERT INTO route_vehicle_options (
                route_id,
                vehicle_type_id
            )
            VALUES
                ('R002', 'V001'),
                ('R002', 'V002'),
                ('R002', 'V003')
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
                ('R002', 'V001', '2026-01-01', 750.0),
                ('R002', 'V002', '2026-01-01', 1100.0),
                ('R002', 'V003', '2026-01-01', 1500.0)
            """
        )

        conexao.execute(
            """
            INSERT INTO demand_forecast (
                week_start,
                route_id,
                forecast_pieces
            )
            VALUES ('2026-08-24', 'R002', 9400)
            """
        )

        conexao.commit()

    materializar_plano_completo()

    resultado = analisar_eficiencia_economica()

    assert len(resultado) == 2

    assert resultado[0]["cost_per_piece"] >= resultado[1]["cost_per_piece"]

    rotas = {linha["route_id"] for linha in resultado}

    assert rotas == {"R001", "R002"}

    for linha in resultado:
        assert linha["planned_trips"] > 0
        assert linha["offered_capacity"] >= linha["forecast_pieces"]
        assert linha["planned_cost"] > 0
        assert 0 < linha["utilization"] <= 1
        assert linha["cost_per_piece"] > 0


def test_analisar_evolucao_semanal(banco_sql_analysis):
    """Testa a comparação temporal entre semanas da mesma rota."""

    with connection.conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO demand_forecast (
                week_start,
                route_id,
                forecast_pieces
            )
            VALUES ('2026-08-31', 'R001', 8000)
            """
        )

        conexao.commit()

    materializar_plano_completo()

    resultado = analisar_evolucao_semanal()

    assert len(resultado) == 2

    primeira_semana = resultado[0]
    segunda_semana = resultado[1]

    assert primeira_semana["route_id"] == "R001"
    assert primeira_semana["week_start"] == "2026-08-24"
    assert primeira_semana["forecast_pieces"] == 7200

    assert primeira_semana["previous_forecast_pieces"] is None
    assert primeira_semana["previous_utilization"] is None
    assert primeira_semana["previous_cost_per_piece"] is None

    assert segunda_semana["route_id"] == "R001"
    assert segunda_semana["week_start"] == "2026-08-31"
    assert segunda_semana["forecast_pieces"] == 8000

    assert segunda_semana["previous_forecast_pieces"] == 7200
    assert segunda_semana["previous_utilization"] == primeira_semana["utilization"]
    assert (
        segunda_semana["previous_cost_per_piece"]
        == primeira_semana["cost_per_piece"]
    )

    assert primeira_semana["forecast_change"] is None
    assert primeira_semana["utilization_change"] is None
    assert primeira_semana["cost_per_piece_change"] is None

    assert segunda_semana["forecast_change"] == 800

    assert segunda_semana["utilization_change"] == pytest.approx(
        segunda_semana["utilization"]
        - primeira_semana["utilization"],
        abs=0.0001,
    )

    assert segunda_semana["cost_per_piece_change"] == pytest.approx(
        segunda_semana["cost_per_piece"]
        - primeira_semana["cost_per_piece"],
        abs=0.0001,
    )


def test_analisar_participacao_custo_rede(banco_sql_analysis):
    """Testa a participação de cada operação no custo total da rede."""

    with connection.conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO routes (
                route_id,
                origin_id,
                destination_id,
                distance_km
            )
            VALUES ('R002', 'DC01', 'DEST002', 180)
            """
        )

        conexao.execute(
            """
            INSERT INTO route_vehicle_options (
                route_id,
                vehicle_type_id
            )
            VALUES
                ('R002', 'V001'),
                ('R002', 'V002'),
                ('R002', 'V003')
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
                ('R002', 'V001', '2026-01-01', 750.0),
                ('R002', 'V002', '2026-01-01', 1100.0),
                ('R002', 'V003', '2026-01-01', 1500.0)
            """
        )

        conexao.execute(
            """
            INSERT INTO demand_forecast (
                week_start,
                route_id,
                forecast_pieces
            )
            VALUES ('2026-08-24', 'R002', 9400)
            """
        )

        conexao.commit()

    materializar_plano_completo()

    resultado = analisar_participacao_custo_rede()

    assert len(resultado) == 2

    custo_total = sum(
        linha["planned_cost"]
        for linha in resultado
    )

    participacao_total = sum(
        linha["network_cost_share"]
        for linha in resultado
    )

    for linha in resultado:
        assert linha["network_total_cost"] == pytest.approx(custo_total)

        assert linha["network_cost_share"] == pytest.approx(
            linha["planned_cost"] / custo_total,
            abs=0.0001,
        )

    assert participacao_total == pytest.approx(
        1.0,
        abs=0.0001,
    )

    assert (
        resultado[0]["network_cost_share"]
        >= resultado[1]["network_cost_share"]
    )

def _adicionar_rota_r002():
    """Adiciona uma segunda rota comparável aos cenários analíticos."""
    with connection.conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO routes (
                route_id,
                origin_id,
                destination_id,
                distance_km
            )
            VALUES ('R002', 'DC01', 'DEST002', 180)
            """
        )

        conexao.execute(
            """
            INSERT INTO route_vehicle_options (
                route_id,
                vehicle_type_id
            )
            VALUES
                ('R002', 'V001'),
                ('R002', 'V002'),
                ('R002', 'V003')
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
                ('R002', 'V001', '2026-01-01', 750.0),
                ('R002', 'V002', '2026-01-01', 1100.0),
                ('R002', 'V003', '2026-01-01', 1500.0)
            """
        )

        conexao.execute(
            """
            INSERT INTO demand_forecast (
                week_start,
                route_id,
                forecast_pieces
            )
            VALUES ('2026-08-24', 'R002', 9400)
            """
        )

        conexao.commit()


def test_analisar_ranking_custo_semanal(banco_sql_analysis):
    """Testa ranking de custo reiniciado dentro de cada semana."""
    _adicionar_rota_r002()
    materializar_plano_completo()

    resultado = analisar_ranking_custo_semanal()

    assert len(resultado) == 2
    assert resultado[0]["weekly_cost_rank"] == 1
    assert resultado[0]["planned_cost"] >= resultado[1]["planned_cost"]
    assert {linha["week_start"] for linha in resultado} == {"2026-08-24"}


def test_analisar_concentracao_custo_rede(banco_sql_analysis):
    """Testa participação e concentração acumulada do custo da rede."""
    _adicionar_rota_r002()
    materializar_plano_completo()

    resultado = analisar_concentracao_custo_rede()

    assert len(resultado) == 2
    assert resultado[0]["planned_cost"] >= resultado[1]["planned_cost"]
    assert resultado[0]["cumulative_cost"] == pytest.approx(
        resultado[0]["planned_cost"]
    )
    assert resultado[-1]["cumulative_cost"] == pytest.approx(
        resultado[-1]["network_total_cost"]
    )
    assert resultado[-1]["cumulative_cost_share"] == pytest.approx(1.0)
    assert (
        resultado[0]["cumulative_cost_share"]
        <= resultado[1]["cumulative_cost_share"]
    )


def test_analisar_tendencia_recente(banco_sql_analysis):
    """Testa média móvel de até três semanas dentro da mesma rota."""
    with connection.conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO demand_forecast (
                week_start,
                route_id,
                forecast_pieces
            )
            VALUES
                ('2026-08-31', 'R001', 8000),
                ('2026-09-07', 'R001', 9000)
            """
        )
        conexao.commit()

    materializar_plano_completo()
    resultado = analisar_tendencia_recente()

    assert len(resultado) == 3
    assert resultado[0]["rolling_3w_forecast"] == pytest.approx(7200.0)
    assert resultado[1]["rolling_3w_forecast"] == pytest.approx(7600.0)
    assert resultado[2]["rolling_3w_forecast"] == pytest.approx(
        (7200 + 8000 + 9000) / 3,
        abs=0.01,
    )

    assert resultado[2]["rolling_3w_utilization"] == pytest.approx(
        sum(linha["utilization"] for linha in resultado) / 3,
        abs=0.0001,
    )


def test_analisar_mudancas_operacionais(banco_sql_analysis):
    """Testa detecção de mudança de veículo entre semanas da rota."""
    with connection.conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO demand_forecast (
                week_start,
                route_id,
                forecast_pieces
            )
            VALUES ('2026-08-31', 'R001', 10300)
            """
        )
        conexao.commit()

    materializar_plano_completo()
    resultado = analisar_mudancas_operacionais()

    assert len(resultado) == 2
    assert resultado[0]["operational_event"] == "INITIAL"
    assert resultado[0]["vehicle_type_id"] == "V002"
    assert resultado[1]["previous_vehicle_type_id"] == "V002"
    assert resultado[1]["vehicle_type_id"] == "V003"
    assert resultado[1]["operational_event"] == "VEHICLE_CHANGE"


def test_analisar_pressao_custo_rede(banco_sql_analysis):
    """Testa múltiplas janelas para relevância e ranking econômico."""
    _adicionar_rota_r002()
    materializar_plano_completo()

    resultado = analisar_pressao_custo_rede()

    assert len(resultado) == 2
    assert resultado[0]["network_cost_rank"] == 1
    assert resultado[0]["weekly_cost_rank"] == 1

    custo_total = sum(linha["planned_cost"] for linha in resultado)
    for linha in resultado:
        assert linha["network_total_cost"] == pytest.approx(custo_total)
        assert linha["network_cost_share"] == pytest.approx(
            linha["planned_cost"] / custo_total,
            abs=0.0001,
        )


def test_analisar_resumo_executivo_semanal(banco_sql_analysis):
    """Testa consolidação semanal da rede e comparação com semana anterior."""
    with connection.conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO demand_forecast (
                week_start,
                route_id,
                forecast_pieces
            )
            VALUES ('2026-08-31', 'R001', 8000)
            """
        )
        conexao.commit()

    materializar_plano_completo()
    resultado = analisar_resumo_executivo_semanal()

    assert len(resultado) == 2

    primeira_semana = resultado[0]
    segunda_semana = resultado[1]

    assert primeira_semana["week_start"] == "2026-08-24"
    assert primeira_semana["previous_forecast_pieces"] is None
    assert primeira_semana["forecast_change"] is None
    assert primeira_semana["planned_cost_change"] is None

    assert segunda_semana["week_start"] == "2026-08-31"
    assert segunda_semana["previous_forecast_pieces"] == 7200
    assert segunda_semana["forecast_change"] == 800
    assert segunda_semana["previous_planned_cost"] == pytest.approx(
        primeira_semana["planned_cost"]
    )
    assert segunda_semana["planned_cost_change"] == pytest.approx(
        segunda_semana["planned_cost"] - primeira_semana["planned_cost"]
    )
    assert segunda_semana["utilization_change"] == pytest.approx(
        segunda_semana["utilization"] - primeira_semana["utilization"],
        abs=0.0001,
    )
