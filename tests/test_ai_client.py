import pytest

from src.ai import client


def test_gerar_resposta_utiliza_cliente_fake(monkeypatch):
    """
    Verifica se o modo fake chama o cliente simulado
    com a pergunta e o contexto corretos.
    """

    pergunta = "Quais produtos devo priorizar?"

    contexto = [
        {
            "sku": "SKU001",
            "prioridade": "ALTA",
        }
    ]

    resposta_esperada = "Resposta simulada."

    def gerar_resposta_fake(pergunta, contexto):
        assert pergunta == "Quais produtos devo priorizar?"
        assert contexto == [
            {
                "sku": "SKU001",
                "prioridade": "ALTA",
            }
        ]

        return resposta_esperada

    monkeypatch.setattr(
        client,
        "gerar_resposta_fake",
        gerar_resposta_fake,
    )

    monkeypatch.setattr(
        client,
        "MODO_CLIENTE",
        "fake",
    )

    resultado = client.gerar_resposta(
        pergunta=pergunta,
        contexto=contexto,
    )

    assert resultado == resposta_esperada


def test_gerar_resposta_rejeita_pergunta_vazia():
    """
    Verifica se perguntas vazias são rejeitadas.
    """

    with pytest.raises(
        ValueError,
        match="A pergunta não pode estar vazia",
    ):
        client.gerar_resposta("   ")


def test_gerar_resposta_rejeita_modo_nao_suportado(monkeypatch):
    """
    Verifica se um modo de cliente desconhecido
    é rejeitado explicitamente.
    """

    monkeypatch.setattr(
        client,
        "MODO_CLIENTE",
        "modo_inexistente",
    )

    with pytest.raises(
        ValueError,
        match="Modo de cliente não suportado",
    ):
        client.gerar_resposta(
            pergunta="Pergunta válida",
            contexto=[],
        )


def test_gerar_resposta_fake_sem_contexto():
    """
    Verifica o comportamento do cliente fake
    quando nenhum contexto é fornecido.
    """

    resultado = client.gerar_resposta_fake(
        pergunta="Analise o estoque.",
        contexto=None,
    )

    assert (
        resultado
        == "Não foi possível realizar a análise porque nenhum dado "
        "do sistema foi disponibilizado."
    )


def test_gerar_resposta_fake_conta_lista_de_registros():
    """
    Verifica se o cliente fake identifica corretamente
    a quantidade de registros recebidos.
    """

    contexto = [
        {"sku": "SKU001"},
        {"sku": "SKU002"},
        {"sku": "SKU003"},
    ]

    resultado = client.gerar_resposta_fake(
        pergunta="Analise o estoque.",
        contexto=contexto,
    )

    assert "Registros disponíveis para análise: 3." in resultado
    assert "Pergunta recebida: Analise o estoque." in resultado
    assert "cliente simulado" in resultado


def test_gerar_resposta_fake_contexto_nao_lista():
    """
    Verifica o comportamento quando o contexto
    recebido não é uma lista.
    """

    contexto = {
        "total_skus": 100,
        "prioridade_alta": 12,
    }

    resultado = client.gerar_resposta_fake(
        pergunta="Resuma o estoque.",
        contexto=contexto,
    )

    assert "Registros disponíveis para análise: 1." in resultado


def test_montar_requisicao_inclui_system_prompt():
    """
    Verifica se a requisição inclui o system prompt oficial.
    """

    contexto = {
        "resumo": {
            "total_registros": 10,
        },
        "registros": [],
    }

    requisicao = client.montar_requisicao(
        pergunta="Analise o estoque.",
        contexto=contexto,
    )

    assert requisicao["system_prompt"] == client.SYSTEM_PROMPT
    assert requisicao["system_prompt"].strip() != ""


def test_montar_requisicao_preserva_pergunta_e_contexto():
    """
    Verifica se pergunta e contexto são preservados
    na estrutura destinada ao futuro LLM.
    """

    pergunta = "Quais produtos devo priorizar?"

    contexto = {
        "resumo": {
            "total_registros": 100,
            "prioridade_alta": 15,
            "risco_ruptura": 8,
        },
        "registros": [
            {
                "sku": "SKU001",
                "prioridade": "ALTA",
            }
        ],
    }

    requisicao = client.montar_requisicao(
        pergunta=pergunta,
        contexto=contexto,
    )

    assert requisicao["pergunta"] == pergunta
    assert requisicao["contexto"] == contexto


def test_montar_requisicao_rejeita_pergunta_vazia():
    """
    Verifica se uma requisição não pode ser construída
    com uma pergunta vazia.
    """

    with pytest.raises(
        ValueError,
        match="A pergunta não pode estar vazia",
    ):
        client.montar_requisicao(
            pergunta="   ",
            contexto={},
        )


def test_obter_quantidade_registros_contexto_estruturado():
    """
    Verifica a contagem de registros no novo
    formato estruturado de contexto.
    """

    contexto = {
        "resumo": {
            "total_registros": 100,
        },
        "registros": [
            {"sku": "SKU001"},
            {"sku": "SKU002"},
            {"sku": "SKU003"},
        ],
    }

    quantidade = client.obter_quantidade_registros(contexto)

    assert quantidade == 3


def test_validar_configuracao_cliente_aceita_modo_fake(monkeypatch):
    """
    Verifica se o modo fake é aceito normalmente.
    """

    monkeypatch.setattr(
        client,
        "MODO_CLIENTE",
        "fake",
    )

    monkeypatch.setattr(
        client,
        "LLM_REAL_ENABLED",
        False,
    )

    client.validar_configuracao_cliente()


def test_validar_configuracao_cliente_bloqueia_real_sem_autorizacao(
    monkeypatch,
):
    """
    Verifica se o modo real permanece bloqueado
    sem autorização explícita.
    """

    monkeypatch.setattr(
        client,
        "MODO_CLIENTE",
        "real",
    )

    monkeypatch.setattr(
        client,
        "LLM_REAL_ENABLED",
        False,
    )

    with pytest.raises(
        RuntimeError,
        match="modo real está bloqueado",
    ):
        client.validar_configuracao_cliente()


def test_validar_configuracao_cliente_real_exige_api_key(monkeypatch):
    """
    Verifica se o modo real autorizado exige uma API key
    antes de permitir chamadas ao provedor.
    """

    monkeypatch.setattr(
        client,
        "MODO_CLIENTE",
        "real",
    )

    monkeypatch.setattr(
        client,
        "LLM_REAL_ENABLED",
        True,
    )

    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )

    with pytest.raises(
        RuntimeError,
        match="OPENAI_API_KEY não configurada",
    ):
        client.validar_configuracao_cliente()


def test_validar_configuracao_cliente_rejeita_modo_invalido(monkeypatch):
    """
    Verifica se modos desconhecidos são rejeitados.
    """

    monkeypatch.setattr(
        client,
        "MODO_CLIENTE",
        "qualquer_coisa",
    )

    with pytest.raises(
        ValueError,
        match="Modo de cliente não suportado",
    ):
        client.validar_configuracao_cliente()


def test_validar_limites_contexto_aceita_contexto_pequeno():
    """
    Verifica se um contexto normal permanece dentro do limite.
    """

    contexto = {
        "resumo": {
            "total_registros": 100,
        },
        "registros": [
            {
                "sku": "SKU001",
                "prioridade": "ALTA",
            }
        ],
    }

    client.validar_limites_contexto(contexto)


def test_validar_limites_contexto_rejeita_contexto_excessivo(
    monkeypatch,
):
    """
    Verifica se contextos acima do limite são bloqueados
    antes de qualquer chamada externa.
    """

    monkeypatch.setattr(
        client,
        "LIMITE_CARACTERES_CONTEXTO",
        100,
    )

    contexto = {
        "dados": "X" * 500,
    }

    with pytest.raises(
        ValueError,
        match="excede o limite permitido",
    ):
        client.validar_limites_contexto(contexto)


def test_montar_requisicao_bloqueia_contexto_excessivo(
    monkeypatch,
):
    """
    Verifica se a montagem da requisição
    aplica automaticamente o limite de contexto.
    """

    monkeypatch.setattr(
        client,
        "LIMITE_CARACTERES_CONTEXTO",
        100,
    )

    contexto = {
        "dados": "X" * 500,
    }

    with pytest.raises(
        ValueError,
        match="excede o limite permitido",
    ):
        client.montar_requisicao(
            pergunta="Analise os dados.",
            contexto=contexto,
        )


def test_limite_tokens_resposta_possui_valor_controlado():
    """
    Verifica se existe um limite explícito
    para a futura resposta do LLM.
    """

    assert client.LIMITE_TOKENS_RESPOSTA > 0
    assert client.LIMITE_TOKENS_RESPOSTA <= 1500


def test_gerar_resposta_real_utiliza_responses_api(monkeypatch):
    """
    Verifica se o cliente real monta corretamente a chamada
    para a Responses API e retorna o texto da resposta.
    """

    contexto = {
        "resumo": {
            "total_registros": 2,
            "prioridade_alta": 1,
            "risco_ruptura": 1,
        },
        "registros": [
            {
                "sku": "SKU-001",
                "prioridade": "ALTA",
            },
            {
                "sku": "SKU-002",
                "prioridade": "BAIXA",
            },
        ],
    }

    class RespostaFake:
        output_text = "Resposta real simulada."

    class ResponsesFake:
        def create(
            self,
            model,
            instructions,
            input,
            max_output_tokens,
        ):
            assert model == client.MODELO_LLM
            assert instructions == client.SYSTEM_PROMPT
            assert max_output_tokens == client.LIMITE_TOKENS_RESPOSTA

            assert "Contexto fornecido pelo sistema:" in input
            assert '"SKU-001"' in input
            assert "Quais produtos apresentam prioridade alta?" in input

            return RespostaFake()

    class OpenAIFake:
        def __init__(self):
            self.responses = ResponsesFake()

    monkeypatch.setattr(
        client,
        "OpenAI",
        OpenAIFake,
    )

    resposta = client.gerar_resposta_real(
        pergunta="Quais produtos apresentam prioridade alta?",
        contexto=contexto,
    )

    assert resposta == "Resposta real simulada."