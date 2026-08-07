from src.ai import service


def test_responder_orquestra_fluxo_corretamente(monkeypatch):
    """
    Verifica se o service obtém o inventário,
    prepara o contexto, envia pergunta e contexto ao client
    e retorna a resposta gerada.
    """

    pergunta = "Quais produtos apresentam prioridade alta?"

    inventario_fake = [
        {
            "sku": "SKU001",
            "prioridade": "ALTA",
        },
        {
            "sku": "SKU002",
            "prioridade": "BAIXA",
        },
    ]

    resposta_fake = "O produto SKU001 apresenta prioridade alta."

    def listar_inventario_fake():
        return inventario_fake

    def gerar_resposta_fake(pergunta, contexto):
        assert pergunta == "Quais produtos apresentam prioridade alta?"

        assert contexto == {
            "resumo": {
                "total_registros": 2,
                "prioridade_alta": 1,
                "risco_ruptura": 0,
            },
            "registros": [
                {
                    "sku": "SKU001",
                    "prioridade": "ALTA",
                },
                {
                    "sku": "SKU002",
                    "prioridade": "BAIXA",
                },
            ],
        }

        return resposta_fake

    monkeypatch.setattr(
        service,
        "listar_inventario",
        listar_inventario_fake,
    )

    monkeypatch.setattr(
        service,
        "gerar_resposta",
        gerar_resposta_fake,
    )

    resultado = service.responder(pergunta)

    assert resultado == resposta_fake


def test_responder_propaga_erro_da_tool(monkeypatch):
    """
    Verifica se uma falha ao obter o inventário
    é propagada pelo service.
    """

    def listar_inventario_fake():
        raise ConnectionError("API indisponível")

    monkeypatch.setattr(
        service,
        "listar_inventario",
        listar_inventario_fake,
    )

    try:
        service.responder("Pergunta de teste")

        assert False, "Era esperado um ConnectionError"

    except ConnectionError as erro:
        assert str(erro) == "API indisponível"


def test_responder_propaga_erro_do_client(monkeypatch):
    """
    Verifica se uma falha no client de IA
    é propagada pelo service.
    """

    inventario_fake = [
        {
            "sku": "SKU001",
            "prioridade": "ALTA",
        }
    ]

    def listar_inventario_fake():
        return inventario_fake

    def gerar_resposta_fake(pergunta, contexto):
        raise RuntimeError("Falha no cliente de IA")

    monkeypatch.setattr(
        service,
        "listar_inventario",
        listar_inventario_fake,
    )

    monkeypatch.setattr(
        service,
        "gerar_resposta",
        gerar_resposta_fake,
    )

    try:
        service.responder("Pergunta de teste")

        assert False, "Era esperado um RuntimeError"

    except RuntimeError as erro:
        assert str(erro) == "Falha no cliente de IA"


def test_preparar_contexto_retorna_resumo_e_registros():
    """
    Verifica se o contexto contém o resumo esperado
    e preserva os registros relevantes.
    """

    inventario = [
        {
            "sku": "SKU001",
            "prioridade": "ALTA",
            "risco_ruptura": "SIM",
            "score_prioridade": 90,
            "valor_acao": 5000,
        },
        {
            "sku": "SKU002",
            "prioridade": "BAIXA",
            "risco_ruptura": "NAO",
            "score_prioridade": 20,
            "valor_acao": 1000,
        },
    ]

    contexto = service.preparar_contexto(inventario)

    assert contexto["resumo"] == {
        "total_registros": 2,
        "prioridade_alta": 1,
        "risco_ruptura": 1,
    }

    assert len(contexto["registros"]) == 2


def test_preparar_contexto_ordena_por_prioridade_e_valor():
    """
    Verifica se os registros são ordenados primeiro
    por score de prioridade e depois por valor da ação.
    """

    inventario = [
        {
            "sku": "SKU001",
            "score_prioridade": 70,
            "valor_acao": 1000,
        },
        {
            "sku": "SKU002",
            "score_prioridade": 90,
            "valor_acao": 500,
        },
        {
            "sku": "SKU003",
            "score_prioridade": 90,
            "valor_acao": 3000,
        },
    ]

    contexto = service.preparar_contexto(inventario)

    skus = [
        item["sku"]
        for item in contexto["registros"]
    ]

    assert skus == [
        "SKU003",
        "SKU002",
        "SKU001",
    ]


def test_preparar_contexto_respeita_limite_de_registros():
    """
    Verifica se o contexto respeita o limite máximo
    de registros detalhados enviados ao cliente.
    """

    inventario = [
        {
            "sku": f"SKU{i:03}",
            "score_prioridade": i,
            "valor_acao": i * 100,
        }
        for i in range(30)
    ]

    contexto = service.preparar_contexto(inventario)

    assert len(contexto["registros"]) == service.LIMITE_REGISTROS_CONTEXTO
    assert len(contexto["registros"]) == 20


def test_preparar_contexto_trata_inventario_vazio():
    """
    Verifica o comportamento quando não existem
    registros de inventário.
    """

    contexto = service.preparar_contexto([])

    assert contexto == {
        "resumo": {
            "total_registros": 0,
            "prioridade_alta": 0,
            "risco_ruptura": 0,
        },
        "registros": [],
    }


def test_preparar_contexto_trata_campos_ausentes():
    """
    Verifica se registros incompletos não interrompem
    a preparação do contexto.
    """

    inventario = [
        {
            "sku": "SKU001",
        },
        {
            "sku": "SKU002",
            "prioridade": "ALTA",
        },
    ]

    contexto = service.preparar_contexto(inventario)

    assert contexto["resumo"]["total_registros"] == 2
    assert contexto["resumo"]["prioridade_alta"] == 1
    assert contexto["resumo"]["risco_ruptura"] == 0

    assert len(contexto["registros"]) == 2       