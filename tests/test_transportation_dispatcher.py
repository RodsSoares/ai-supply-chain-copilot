import pytest

from src.ai import transportation_dispatcher
from src.ai.transportation_router import TransportationIntent


def test_executar_intencao_transporte_executa_analise_correta(
    monkeypatch,
):
    """
    Verifica se o dispatcher executa a função analítica
    correspondente à intenção recebida.
    """

    resultado_fake = [
        {
            "route_id": "R001",
            "planned_cost": 5000.0,
        },
        {
            "route_id": "R002",
            "planned_cost": 3000.0,
        },
    ]

    def analisar_fake():
        return resultado_fake

    monkeypatch.setitem(
        transportation_dispatcher.ANALISES_TRANSPORTATION,
        "cost_ranking",
        analisar_fake,
    )

    intencao = TransportationIntent(
        intent="cost_ranking",
    )

    resultado = (
        transportation_dispatcher.executar_intencao_transporte(
            intencao
        )
    )

    assert resultado == resultado_fake


def test_executar_intencao_transporte_filtra_route_id(
    monkeypatch,
):
    """
    Verifica se o dispatcher restringe o resultado
    à rota explicitamente solicitada.
    """

    resultado_fake = [
        {
            "route_id": "R001",
            "operational_event": "STABLE",
        },
        {
            "route_id": "R002",
            "operational_event": "VEHICLE_CHANGE",
        },
        {
            "route_id": "R001",
            "operational_event": "TRIPS_CHANGE",
        },
    ]

    def analisar_fake():
        return resultado_fake

    monkeypatch.setitem(
        transportation_dispatcher.ANALISES_TRANSPORTATION,
        "operational_changes",
        analisar_fake,
    )

    intencao = TransportationIntent(
        intent="operational_changes",
        route_id="R001",
    )

    resultado = (
        transportation_dispatcher.executar_intencao_transporte(
            intencao
        )
    )

    assert len(resultado) == 2
    assert all(
        registro["route_id"] == "R001"
        for registro in resultado
    )


def test_executar_intencao_transporte_sem_route_id_nao_filtra(
    monkeypatch,
):
    """
    Verifica se uma análise de rede preserva todos os registros
    quando nenhuma rota específica foi solicitada.
    """

    resultado_fake = [
        {"route_id": "R001"},
        {"route_id": "R002"},
        {"route_id": "R003"},
    ]

    def analisar_fake():
        return resultado_fake

    monkeypatch.setitem(
        transportation_dispatcher.ANALISES_TRANSPORTATION,
        "economic_efficiency",
        analisar_fake,
    )

    intencao = TransportationIntent(
        intent="economic_efficiency",
    )

    resultado = (
        transportation_dispatcher.executar_intencao_transporte(
            intencao
        )
    )

    assert resultado == resultado_fake
    assert len(resultado) == 3


def test_executar_intencao_transporte_bloqueia_out_of_scope():
    intencao = TransportationIntent(
        intent="out_of_scope",
    )

    with pytest.raises(
        ValueError,
        match="fora do escopo analítico",
    ):
        transportation_dispatcher.executar_intencao_transporte(
            intencao
        )
