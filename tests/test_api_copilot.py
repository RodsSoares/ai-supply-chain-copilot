import pytest
from fastapi.testclient import TestClient

from src.api import main


client = TestClient(main.app)


def test_consultar_copilot_retorna_resposta(monkeypatch):
    """
    Verifica se o endpoint /copilot retorna a pergunta
    e a resposta produzida pela camada de IA.
    """

    pergunta = "Quais produtos apresentam prioridade alta?"
    resposta_fake = "Os produtos prioritários foram identificados."

    def responder_fake(
        pergunta_recebida,
        dominio="inventory",
    ):
        assert pergunta_recebida == pergunta
        assert dominio == "inventory"
        return resposta_fake

    monkeypatch.setattr(
        main,
        "responder",
        responder_fake,
    )

    resposta = client.post(
        "/copilot",
        json={
            "pergunta": pergunta,
        },
    )

    assert resposta.status_code == 200

    assert resposta.json() == {
        "pergunta": pergunta,
        "resposta": resposta_fake,
    }


def test_consultar_copilot_encaminha_dominio_transportation(
    monkeypatch,
):
    """
    Verifica se o endpoint /copilot encaminha explicitamente
    o domínio Transportation para a camada de IA.
    """

    pergunta = "Como está a operação de transporte da rede?"
    resposta_fake = "Resumo executivo da rede."

    def responder_fake(
        pergunta_recebida,
        dominio="inventory",
    ):
        assert pergunta_recebida == pergunta
        assert dominio == "transportation"
        return resposta_fake

    monkeypatch.setattr(
        main,
        "responder",
        responder_fake,
    )

    resposta = client.post(
        "/copilot",
        json={
            "pergunta": pergunta,
            "dominio": "transportation",
        },
    )

    assert resposta.status_code == 200

    assert resposta.json() == {
        "pergunta": pergunta,
        "resposta": resposta_fake,
    }


def test_consultar_copilot_rejeita_corpo_sem_pergunta():
    """
    Verifica se a API rejeita uma requisição
    sem o campo obrigatório pergunta.
    """

    resposta = client.post(
        "/copilot",
        json={},
    )

    assert resposta.status_code == 422


def test_consultar_copilot_rejeita_corpo_invalido():
    """
    Verifica se a API rejeita um corpo
    que não segue o contrato esperado.
    """

    resposta = client.post(
        "/copilot",
        json={
            "pergunta": None,
        },
    )

    assert resposta.status_code == 422


@pytest.mark.parametrize(
    "erro",
    [
        ConnectionError("API indisponível"),
        RuntimeError("Falha no cliente de IA"),
        ValueError("Pergunta inválida"),
    ],
)
def test_consultar_copilot_trata_erros_da_camada_de_ia(
    monkeypatch,
    erro,
):
    """
    Verifica se falhas conhecidas da camada de IA
    são convertidas para resposta HTTP 500.
    """

    def responder_fake(
        pergunta,
        dominio="inventory",
    ):
        assert dominio == "inventory"
        raise erro

    monkeypatch.setattr(
        main,
        "responder",
        responder_fake,
    )

    resposta = client.post(
        "/copilot",
        json={
            "pergunta": "Pergunta de teste",
        },
    )

    assert resposta.status_code == 500
    assert resposta.json() == {
        "detail": str(erro),
    }


def test_obter_mudancas_transporte_retorna_historico_da_rota():
    resposta = client.get(
        "/transportation/routes/R001/changes"
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert isinstance(dados, list)
    assert len(dados) > 0

    assert all(
        registro["route_id"] == "R001"
        for registro in dados
    )

    primeiro = dados[0]

    assert primeiro["week_start"] == "2026-08-24"
    assert primeiro["vehicle_type_id"] == "V002"
    assert primeiro["planned_trips"] == 2
    assert primeiro["offered_capacity"] == 10000
    assert primeiro["planned_cost"] == 1700.0
    assert primeiro["previous_vehicle_type_id"] is None
    assert primeiro["previous_planned_trips"] is None
    assert primeiro["previous_offered_capacity"] is None
    assert primeiro["operational_event"] == "INITIAL"


def test_obter_mudancas_transporte_retorna_404_para_rota_inexistente():
    resposta = client.get(
        "/transportation/routes/ROTA_INEXISTENTE/changes"
    )

    assert resposta.status_code == 404
    assert resposta.json() == {
        "detail": "Rota não encontrada."
    }
    