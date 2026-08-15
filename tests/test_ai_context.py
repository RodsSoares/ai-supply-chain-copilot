from src.ai.context import (
    calcular_agregacao_fornecedores,
    preparar_contexto,
)

from src.ai.context import LIMITE_REGISTROS_CONTEXTO

def test_preparar_contexto_respeita_limite_de_registros() -> None:
    inventario = [
        {
            "sku": f"SKU{i:03}",
            "score_prioridade": i,
            "valor_acao": i * 100,
        }
        for i in range(30)
    ]

    contexto = preparar_contexto(inventario)

    assert len(contexto["registros"]) == LIMITE_REGISTROS_CONTEXTO

def test_calcular_agregacao_fornecedores_preserva_empate() -> None:
    registros = [
        {"fornecedor": "Delta Manutenção"},
        {"fornecedor": "Conecta Suprimentos"},
        {"fornecedor": "Delta Manutenção"},
        {"fornecedor": "Conecta Suprimentos"},
        {"fornecedor": "Fornecedor Beta"},
    ]

    resultado = calcular_agregacao_fornecedores(registros)

    assert resultado["contagem"] == {
        "Delta Manutenção": 2,
        "Conecta Suprimentos": 2,
        "Fornecedor Beta": 1,
    }

    assert resultado["maior_frequencia"] == 2

    assert resultado["mais_frequentes"] == [
        "Conecta Suprimentos",
        "Delta Manutenção",
    ]

    assert resultado["menor_frequencia"] == 1

    assert resultado["menos_frequentes"] == [
    "Fornecedor Beta",
    ]


def test_calcular_agregacao_fornecedores_sem_dados() -> None:
    resultado = calcular_agregacao_fornecedores([])

    assert resultado == {
    "contagem": {},
    "maior_frequencia": 0,
    "mais_frequentes": [],
    "menor_frequencia": 0,
    "menos_frequentes": [],
    }


def test_preparar_contexto_inclui_agregacao_fornecedores() -> None:
    inventario = [
        {
            "sku": "SKU-001",
            "fornecedor": "Delta Manutenção",
            "prioridade": "ALTA",
            "risco_ruptura": "SIM",
            "score_prioridade": 100,
            "valor_acao": 1000,
        },
        {
            "sku": "SKU-002",
            "fornecedor": "Conecta Suprimentos",
            "prioridade": "ALTA",
            "risco_ruptura": "SIM",
            "score_prioridade": 100,
            "valor_acao": 900,
        },
        {
            "sku": "SKU-003",
            "fornecedor": "Delta Manutenção",
            "prioridade": "MEDIA",
            "risco_ruptura": "NAO",
            "score_prioridade": 50,
            "valor_acao": 500,
        },
        {
            "sku": "SKU-004",
            "fornecedor": "Conecta Suprimentos",
            "prioridade": "MEDIA",
            "risco_ruptura": "NAO",
            "score_prioridade": 50,
            "valor_acao": 400,
        },
    ]

    contexto = preparar_contexto(inventario)

    assert contexto["resumo"]["total_registros"] == 4
    assert contexto["resumo"]["prioridade_alta"] == 2
    assert contexto["resumo"]["risco_ruptura"] == 2

    fornecedores = contexto["agregacoes"]["fornecedores"]

    assert fornecedores["maior_frequencia"] == 2
    assert fornecedores["mais_frequentes"] == [
        "Conecta Suprimentos",
        "Delta Manutenção",
    ]


def test_preparar_contexto_vazio_mantem_estrutura() -> None:
    contexto = preparar_contexto([])

    assert contexto["agregacoes"]["fornecedores"] == {
    "contagem": {},
    "maior_frequencia": 0,
    "mais_frequentes": [],
    "menor_frequencia": 0,
    "menos_frequentes": [],
    }

    assert contexto["registros"] == []