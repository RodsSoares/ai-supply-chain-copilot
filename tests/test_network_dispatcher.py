"""Integração das capacidades de rede com o dispatcher de Transportation."""

import pytest

from src.ai import transportation_dispatcher as dispatcher
from src.ai.transportation_router import TransportationIntent


def test_parametros_what_if_construidos_deterministicamente():
    intencao = TransportationIntent(intent="run_what_if", route_id="NR001", what_if_frequency_basis="MAX",
                                    what_if_volume_change_pct=10)
    parametros = dispatcher.parametros_capacidade_network(intencao)
    assert "route_id" not in parametros
    assert parametros["overrides"] == [
        {"parameter_key": "frequency_basis", "value": "MAX"},
        {"parameter_key": "volume_multiplier", "value": pytest.approx(1.10)},
    ]


def test_dispatcher_encaminha_capacidade_de_rede(monkeypatch):
    chamadas = {}

    def fake(nome, **parametros):
        chamadas["nome"], chamadas["parametros"] = nome, parametros
        return {"capability": nome}

    monkeypatch.setattr(dispatcher, "executar_capacidade", fake)
    resultado = dispatcher.executar_intencao_transporte(
        TransportationIntent(intent="forecast_accuracy", forecast_version="BUDGET_2026", level="STORE"))
    assert resultado == {"capability": "forecast_accuracy"}
    assert chamadas["parametros"] == {"forecast_version": "BUDGET_2026", "level": "STORE"}


def test_intencoes_v2_continuam_funcionando(monkeypatch):
    monkeypatch.setitem(dispatcher.ANALISES_TRANSPORTATION, "cost_ranking", lambda: [{"route_id": "R001"}])
    assert dispatcher.executar_intencao_transporte(TransportationIntent(intent="cost_ranking")) == [{"route_id": "R001"}]


def test_todas_capacidades_de_rede_estao_no_contrato():
    from typing import get_args
    from src.ai.transportation_router import TransportationIntentName
    from src.analytics.network.service import CAPACIDADES_NETWORK
    expostas = set(get_args(TransportationIntentName))
    assert set(CAPACIDADES_NETWORK) - {"data_quality_report"} <= expostas
