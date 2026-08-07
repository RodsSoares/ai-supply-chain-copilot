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

    def responder_fake(pergunta_recebida):
        assert pergunta_recebida == pergunta
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

    def responder_fake(pergunta):
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