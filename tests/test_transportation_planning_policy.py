"""Testes das políticas de planejamento de Transportation."""

from src.decision.transportation.planning_policy import (
    calcular_cenarios_planejamento,
    calcular_metricas_alternativa,
    calcular_viagens_necessarias,
    calcular_viagens_por_capacidade,
    classificar_perfil_rota,
    gerar_viagens_planejadas,
    obter_frequencia_alvo,
    selecionar_alternativa,
)

from src.analytics.transportation.planning import (
    analisar_alternativas_planejamento,
    gerar_plano_planejado,
    salvar_viagens_planejadas,
    selecionar_plano,
)

def test_calcular_viagens_necessarias_por_frequencia():
    assert calcular_viagens_necessarias(
        forecast_pieces=7200,
        capacity_pieces=10000,
        target_frequency=2,
    ) == 2


def test_calcular_viagens_necessarias_por_capacidade():
    assert calcular_viagens_necessarias(
        forecast_pieces=25000,
        capacity_pieces=10000,
        target_frequency=2,
    ) == 3


def test_calcular_viagens_necessarias_no_limite_da_capacidade():
    assert calcular_viagens_necessarias(
        forecast_pieces=20000,
        capacity_pieces=10000,
        target_frequency=2,
    ) == 2
    

def test_obter_frequencia_alvo():
    assert obter_frequencia_alvo("SHORT") == 2
    assert obter_frequencia_alvo("MEDIUM") == 2
    assert obter_frequencia_alvo("LONG") == 2


def test_obter_frequencia_alvo_rejeita_perfil_invalido():
    try:
        obter_frequencia_alvo("INVALID")
        assert False, "Era esperado ValueError"
    except ValueError:
        pass


def test_classificar_perfil_rota_short():
    assert classificar_perfil_rota(95) == "SHORT"
    assert classificar_perfil_rota(299) == "SHORT"


def test_classificar_perfil_rota_medium():
    assert classificar_perfil_rota(300) == "MEDIUM"
    assert classificar_perfil_rota(620) == "MEDIUM"
    assert classificar_perfil_rota(800) == "MEDIUM"


def test_classificar_perfil_rota_long():
    assert classificar_perfil_rota(801) == "LONG"
    assert classificar_perfil_rota(2750) == "LONG"


def test_calcular_metricas_alternativa():
    resultado = calcular_metricas_alternativa(
        forecast_pieces=7200,
        capacity_pieces=5000,
        rate_per_trip=850.0,
        target_frequency=2,
    )

    assert resultado["planned_trips"] == 2
    assert resultado["planned_capacity"] == 10000
    assert resultado["planned_cost"] == 1700.0
    assert resultado["utilization"] == 0.72
    assert resultado["cost_per_piece"] == 1700.0 / 7200


def test_selecionar_alternativa_por_menor_custo_por_peca():
    alternativas = [
        {
            "vehicle_name": "VAN",
            "planned_trips": 3,
            "planned_capacity": 7500,
            "planned_cost": 1950.0,
            "utilization": 0.96,
            "cost_per_piece": 1950.0 / 7200,
        },
        {
            "vehicle_name": "LIGHT_TRUCK",
            "planned_trips": 2,
            "planned_capacity": 10000,
            "planned_cost": 1700.0,
            "utilization": 0.72,
            "cost_per_piece": 1700.0 / 7200,
        },
        {
            "vehicle_name": "MEDIUM_TRUCK",
            "planned_trips": 2,
            "planned_capacity": 20000,
            "planned_cost": 2300.0,
            "utilization": 0.36,
            "cost_per_piece": 2300.0 / 7200,
        },
    ]

    resultado = selecionar_alternativa(alternativas)

    assert resultado["vehicle_name"] == "LIGHT_TRUCK"
    assert resultado["selection_reason"] == "LOWEST_COST_PER_PIECE"


def test_selecionar_alternativa_rejeita_lista_vazia():
    try:
        selecionar_alternativa([])
        assert False, "Era esperado ValueError"
    except ValueError:
        pass


def test_gerar_viagens_planejadas_distribui_pecas_corretamente():
    plano = {
        "week_start": "2026-08-24",
        "route_id": "R001",
        "vehicle_type_id": "V002",
        "forecast_pieces": 7201,
        "planned_trips": 2,
        "capacity_pieces": 5000,
        "rate_per_trip": 850.0,
    }

    viagens = gerar_viagens_planejadas(plano)

    assert len(viagens) == 2

    assert viagens[0]["trip_id"] == "20260824-R001-01"
    assert viagens[1]["trip_id"] == "20260824-R001-02"

    assert viagens[0]["planned_pieces"] == 3601
    assert viagens[1]["planned_pieces"] == 3600

    assert sum(
        viagem["planned_pieces"]
        for viagem in viagens
    ) == 7201

    assert max(
        viagem["planned_pieces"]
        for viagem in viagens
    ) - min(
        viagem["planned_pieces"]
        for viagem in viagens
    ) <= 1


def test_gerar_viagens_planejadas_preserva_grain_da_viagem():
    plano = {
        "week_start": "2026-08-24",
        "route_id": "R001",
        "vehicle_type_id": "V002",
        "forecast_pieces": 7200,
        "planned_trips": 2,
        "capacity_pieces": 5000,
        "rate_per_trip": 850.0,
    }

    viagens = gerar_viagens_planejadas(plano)

    assert all(
        viagem["planned_capacity"] == 5000
        for viagem in viagens
    )

    assert all(
        viagem["planned_cost"] == 850.0
        for viagem in viagens
    )

    assert sum(
        viagem["planned_capacity"]
        for viagem in viagens
    ) == 10000

    assert sum(
        viagem["planned_cost"]
        for viagem in viagens
    ) == 1700.0

def test_calcular_viagens_por_capacidade_uma_viagem():
    assert calcular_viagens_por_capacidade(
        forecast_pieces=7200,
        capacity_pieces=10000,
    ) == 1


def test_calcular_viagens_por_capacidade_multiplas_viagens():
    assert calcular_viagens_por_capacidade(
        forecast_pieces=25000,
        capacity_pieces=10000,
    ) == 3


def test_calcular_viagens_por_capacidade_limite_exato():
    assert calcular_viagens_por_capacidade(
        forecast_pieces=20000,
        capacity_pieces=10000,
    ) == 2


def test_calcular_cenarios_planejamento_separa_economico_e_servico():
    resultado = calcular_cenarios_planejamento(
        forecast_pieces=8_000,
        capacity_pieces=10_000,
        rate_per_trip=3_000.0,
        target_frequency=2,
    )

    assert resultado["economic"]["planned_trips"] == 1
    assert resultado["economic"]["offered_capacity"] == 10_000
    assert resultado["economic"]["utilization"] == 0.8
    assert resultado["economic"]["planned_cost"] == 3_000.0
    assert resultado["economic"]["cost_per_piece"] == 0.375

    assert resultado["service"]["planned_trips"] == 2
    assert resultado["service"]["offered_capacity"] == 20_000
    assert resultado["service"]["utilization"] == 0.4
    assert resultado["service"]["planned_cost"] == 6_000.0
    assert resultado["service"]["cost_per_piece"] == 0.75


def test_calcular_cenarios_planejamento_calcula_service_premium():
    resultado = calcular_cenarios_planejamento(
        forecast_pieces=8_000,
        capacity_pieces=10_000,
        rate_per_trip=3_000.0,
        target_frequency=2,
    )

    assert resultado["service_premium"] == 1.0


def test_calcular_cenarios_planejamento_premium_zero_quando_capacidade_ja_exige_frequencia():
    resultado = calcular_cenarios_planejamento(
        forecast_pieces=15_000,
        capacity_pieces=10_000,
        rate_per_trip=3_000.0,
        target_frequency=2,
    )

    assert resultado["economic"]["planned_trips"] == 2
    assert resultado["service"]["planned_trips"] == 2
    assert resultado["service_premium"] == 0.0