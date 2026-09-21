import pytest


from src.ai import transportation_router
from pydantic import ValidationError
from src.ai.transportation_router import TransportationIntent


def test_transportation_intent_aceita_cost_ranking():
    """
    Verifica se uma intenção válida de ranking de custo
    é aceita sem exigir uma rota específica.
    """

    resultado = TransportationIntent(
        intent="cost_ranking",
    )

    assert resultado.intent == "cost_ranking"
    assert resultado.route_id is None


def test_transportation_intent_aceita_rota_especifica():
    """
    Verifica se uma intenção pode carregar uma rota
    específica quando a pergunta exigir esse contexto.
    """

    resultado = TransportationIntent(
        intent="operational_changes",
        route_id="R001",
    )

    assert resultado.intent == "operational_changes"
    assert resultado.route_id == "R001"


def test_transportation_intent_rejeita_intent_invalida():
    """
    Verifica se o contrato impede que uma capacidade
    não autorizada seja criada.
    """

    with pytest.raises(ValidationError):
        TransportationIntent(
            intent="inventar_uma_analise",
        )


def test_transportation_intent_aceita_todas_as_capacidades():
    """
    Verifica se todas as capacidades autorizadas
    pelo domínio Transportation são aceitas.
    """

    intents_validas = [
        "network_overview",
        "economic_efficiency",
        "weekly_evolution",
        "cost_share",
        "cost_ranking",
        "cost_concentration",
        "recent_trend",
        "operational_changes",
        "cost_pressure",
        "executive_summary",
    ]

    for intent in intents_validas:
        resultado = TransportationIntent(
            intent=intent,
        )

        assert resultado.intent == intent


def test_rotear_pergunta_transporte_identifica_cost_ranking(
    monkeypatch,
):
    """
    Verifica se o router retorna a intenção estruturada
    produzida pelo cliente para uma pergunta de ranking de custo.
    """

    def gerar_resposta_estruturada_fake(
        pergunta,
        instrucoes,
        modelo_saida,
    ):
        assert pergunta == "Qual é a rota mais cara?"
        assert (
            instrucoes
            == transportation_router.TRANSPORTATION_ROUTER_PROMPT
        )
        assert modelo_saida is TransportationIntent

        return TransportationIntent(
            intent="cost_ranking",
            route_id=None,
        )

    monkeypatch.setattr(
        transportation_router,
        "gerar_resposta_estruturada",
        gerar_resposta_estruturada_fake,
    )

    resultado = transportation_router.rotear_pergunta_transporte(
        "Qual é a rota mais cara?"
    )

    assert resultado.intent == "cost_ranking"
    assert resultado.route_id is None


def test_rotear_pergunta_transporte_identifica_eficiencia(
    monkeypatch,
):
    """
    Verifica o roteamento de uma pergunta sobre
    eficiência e ociosidade.
    """

    def gerar_resposta_estruturada_fake(
        pergunta,
        instrucoes,
        modelo_saida,
    ):
        return TransportationIntent(
            intent="economic_efficiency",
            route_id=None,
        )

    monkeypatch.setattr(
        transportation_router,
        "gerar_resposta_estruturada",
        gerar_resposta_estruturada_fake,
    )

    resultado = transportation_router.rotear_pergunta_transporte(
        "Qual rota está mais ociosa?"
    )

    assert resultado.intent == "economic_efficiency"
    assert resultado.route_id is None


def test_rotear_pergunta_transporte_extrai_route_id(
    monkeypatch,
):
    """
    Verifica se uma rota explicitamente mencionada
    pode ser preservada na intenção estruturada.
    """

    def gerar_resposta_estruturada_fake(
        pergunta,
        instrucoes,
        modelo_saida,
    ):
        return TransportationIntent(
            intent="operational_changes",
            route_id="R001",
        )

    monkeypatch.setattr(
        transportation_router,
        "gerar_resposta_estruturada",
        gerar_resposta_estruturada_fake,
    )

    resultado = transportation_router.rotear_pergunta_transporte(
        "O que mudou na rota R001?"
    )

    assert resultado.intent == "operational_changes"
    assert resultado.route_id == "R001"


def test_transportation_intent_aceita_out_of_scope():
    intencao = TransportationIntent(
        intent="out_of_scope",
    )

    assert intencao.intent == "out_of_scope"
    assert intencao.route_id is None