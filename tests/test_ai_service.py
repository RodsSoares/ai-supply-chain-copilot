from src.ai import service


def test_responder_orquestra_fluxo_corretamente(monkeypatch):
    pergunta = "Quais produtos apresentam prioridade alta?"

    inventario_fake = [
        {"sku": "SKU001"},
        {"sku": "SKU002"},
    ]

    contexto_fake = {
        "contexto": "preparado",
    }

    resposta_fake = "O produto SKU001 apresenta prioridade alta."

    def listar_inventario_fake():
        return inventario_fake

    def preparar_contexto_fake(inventario):
        assert inventario == inventario_fake
        return contexto_fake

    def gerar_resposta_fake(pergunta, contexto, instrucoes):
        assert pergunta == "Quais produtos apresentam prioridade alta?"
        assert contexto == contexto_fake
        assert service.SYSTEM_PROMPT in instrucoes
        assert service.INVENTORY_PROMPT in instrucoes
        return resposta_fake

    monkeypatch.setattr(
        service,
        "listar_inventario",
        listar_inventario_fake,
    )

    monkeypatch.setattr(
        service,
        "preparar_contexto",
        preparar_contexto_fake,
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
    Verifica se uma falha ao obter o invent├írio
    ├® propagada pelo service.
    """

    def listar_inventario_fake():
        raise ConnectionError("API indispon├¡vel")

    monkeypatch.setattr(
        service,
        "listar_inventario",
        listar_inventario_fake,
    )

    try:
        service.responder("Pergunta de teste")

        assert False, "Era esperado um ConnectionError"

    except ConnectionError as erro:
        assert str(erro) == "API indispon├¡vel"


def test_responder_propaga_erro_do_client(monkeypatch):
    """
    Verifica se uma falha no client de IA
    ├® propagada pelo service.
    """

    inventario_fake = [
        {
            "sku": "SKU001",
            "prioridade": "ALTA",
        }
    ]

    def listar_inventario_fake():
        return inventario_fake

    def gerar_resposta_fake(pergunta, contexto, instrucoes):
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
    Verifica se o contexto cont├®m o resumo esperado
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
    Verifica se os registros s├úo ordenados primeiro
    por score de prioridade e depois por valor da a├º├úo.
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


def test_preparar_contexto_trata_campos_ausentes():
    """
    Verifica se registros incompletos n├úo interrompem
    a prepara├º├úo do contexto.
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


def test_preparar_contexto_identifica_contexto_parcial():
    """
    Verifica se o contexto informa corretamente quando apenas
    parte do invent├írio ├® enviada como registros detalhados.
    """

    inventario = [
        {
            "sku": f"SKU{i:03d}",
            "prioridade": "ALTA",
            "risco_ruptura": "SIM",
            "score_prioridade": 100 - i,
            "valor_acao": 1000 - i,
        }
        for i in range(25)
    ]

    contexto = service.preparar_contexto(inventario)

    assert contexto["resumo"]["total_registros"] == 25
    assert len(contexto["registros"]) == 20

    assert contexto["metadados_contexto"]["total_registros_detalhados"] == 20
    assert contexto["metadados_contexto"]["limite_registros_detalhados"] == 20
    assert contexto["metadados_contexto"]["contexto_parcial"] is True

def test_responder_transportation_executa_fluxo_completo(monkeypatch):
    from src.ai.transportation_router import TransportationIntent
    pergunta = "Qual é a rota mais cara?"
    intencao_fake = TransportationIntent(intent="cost_ranking")
    resultado_fake = [{"route_id": "R001", "planned_cost": 5000.0}]
    contexto_fake = {"dominio": "transportation", "tipo_analise": "cost_ranking", "resultado": resultado_fake}
    monkeypatch.setattr(service, "rotear_pergunta_transporte", lambda pergunta: intencao_fake)
    monkeypatch.setattr(service, "executar_intencao_transporte", lambda intencao: resultado_fake)
    monkeypatch.setattr(service, "preparar_contexto_transporte", lambda tipo_analise, resultado_analitico: contexto_fake)
    def gerar_resposta_fake(pergunta, contexto, instrucoes):
        assert pergunta == "Qual é a rota mais cara?"
        assert contexto == contexto_fake
        assert service.SYSTEM_PROMPT in instrucoes
        assert service.TRANSPORTATION_PROMPT in instrucoes
        return "R001 é a rota de maior custo."
    monkeypatch.setattr(service, "gerar_resposta", gerar_resposta_fake)
    resposta = service.responder(pergunta=pergunta, dominio="transportation")
    assert resposta == "R001 é a rota de maior custo."

def test_responder_transportation_bloqueia_out_of_scope(monkeypatch):
    from src.ai.transportation_router import TransportationIntent
    intencao_fake = TransportationIntent(intent="out_of_scope")
    monkeypatch.setattr(service, "rotear_pergunta_transporte", lambda pergunta: intencao_fake)
    def dispatcher_nao_deve_ser_chamado(intencao):
        raise AssertionError("Dispatcher não deveria ser executado.")
    def llm_nao_deve_ser_chamado(*args, **kwargs):
        raise AssertionError("LLM explicador não deveria ser executado.")
    monkeypatch.setattr(service, "executar_intencao_transporte", dispatcher_nao_deve_ser_chamado)
    monkeypatch.setattr(service, "gerar_resposta", llm_nao_deve_ser_chamado)
    resposta = service.responder(pergunta="Qual é o chocolate mais gostoso?", dominio="transportation")
    assert resposta == "A pergunta está fora do escopo analítico de Transportation."

def test_responder_rejeita_dominio_invalido():
    try:
        service.responder(pergunta="Teste", dominio="chocolate")
    except ValueError as erro:
        assert "Domínio não suportado" in str(erro)
    else:
        raise AssertionError("Era esperado ValueError para domínio inválido.")

def test_responder_inventory_permanece_default(monkeypatch):
    monkeypatch.setattr(service, "responder_inventory", lambda pergunta: "inventory-ok")
    resposta = service.responder(pergunta="Quais produtos têm prioridade alta?")
    assert resposta == "inventory-ok"