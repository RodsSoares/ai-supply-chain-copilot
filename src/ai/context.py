from collections import Counter
from typing import Any


LIMITE_REGISTROS_CONTEXTO = 20


def calcular_agregacao_fornecedores(
    registros: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calcula deterministicamente a distribuição dos fornecedores
    presentes nos registros detalhados enviados ao LLM.

    Preserva todos os fornecedores empatados tanto na maior
    quanto na menor frequência.
    """

    fornecedores = [
        item.get("fornecedor")
        for item in registros
        if item.get("fornecedor")
    ]

    if not fornecedores:
        return {
            "contagem": {},
            "maior_frequencia": 0,
            "mais_frequentes": [],
            "menor_frequencia": 0,
            "menos_frequentes": [],
        }

    contagem = Counter(fornecedores)

    maior_frequencia = max(contagem.values())
    menor_frequencia = min(contagem.values())

    mais_frequentes = sorted(
        fornecedor
        for fornecedor, quantidade in contagem.items()
        if quantidade == maior_frequencia
    )

    menos_frequentes = sorted(
        fornecedor
        for fornecedor, quantidade in contagem.items()
        if quantidade == menor_frequencia
    )

    return {
        "contagem": dict(contagem),
        "maior_frequencia": maior_frequencia,
        "mais_frequentes": mais_frequentes,
        "menor_frequencia": menor_frequencia,
        "menos_frequentes": menos_frequentes,
    }


def preparar_contexto(
    inventario: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Prepara e enriquece deterministicamente o contexto
    enviado à camada de IA.

    Mantém indicadores consolidados, limita a quantidade
    de registros detalhados e adiciona agregações calculadas
    antes da chamada ao LLM.
    """

    if not inventario:
        return {
            "resumo": {
                "total_registros": 0,
                "prioridade_alta": 0,
                "risco_ruptura": 0,
            },
            "metadados_contexto": {
                "total_registros_detalhados": 0,
                "limite_registros_detalhados": LIMITE_REGISTROS_CONTEXTO,
                "criterio_selecao": (
                    "Registros ordenados por score_prioridade e valor_acao, "
                    "ambos em ordem decrescente."
                ),
                "contexto_parcial": False,
            },
            "agregacoes": {
                "fornecedores": calcular_agregacao_fornecedores([]),
            },
            "registros": [],
        }

    prioridade_alta = sum(
        1
        for item in inventario
        if item.get("prioridade") == "ALTA"
    )

    risco_ruptura = sum(
        1
        for item in inventario
        if item.get("risco_ruptura") == "SIM"
    )

    registros_ordenados = sorted(
        inventario,
        key=lambda item: (
            item.get("score_prioridade") or 0,
            item.get("valor_acao") or 0,
        ),
        reverse=True,
    )

    registros_selecionados = registros_ordenados[
        :LIMITE_REGISTROS_CONTEXTO
    ]

    agregacao_fornecedores = calcular_agregacao_fornecedores(
        registros_selecionados
    )

    return {
        "resumo": {
            "total_registros": len(inventario),
            "prioridade_alta": prioridade_alta,
            "risco_ruptura": risco_ruptura,
        },
        "metadados_contexto": {
            "total_registros_detalhados": len(registros_selecionados),
            "limite_registros_detalhados": LIMITE_REGISTROS_CONTEXTO,
            "criterio_selecao": (
                "Registros ordenados por score_prioridade e valor_acao, "
                "ambos em ordem decrescente."
            ),
            "contexto_parcial": (
                len(inventario) > len(registros_selecionados)
            ),
        },
        "agregacoes": {
            "fornecedores": agregacao_fornecedores,
        },
        "registros": registros_selecionados,
    }