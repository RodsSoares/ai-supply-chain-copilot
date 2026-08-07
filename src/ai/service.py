from typing import Any

from src.ai.client import gerar_resposta
from src.ai.tools import listar_inventario


LIMITE_REGISTROS_CONTEXTO = 20


def preparar_contexto(
    inventario: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Prepara um contexto enxuto para a camada de IA.

    Mantém indicadores consolidados e limita a quantidade
    de registros detalhados enviados ao cliente.
    """

    if not inventario:
        return {
            "resumo": {
                "total_registros": 0,
                "prioridade_alta": 0,
                "risco_ruptura": 0,
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

    return {
        "resumo": {
            "total_registros": len(inventario),
            "prioridade_alta": prioridade_alta,
            "risco_ruptura": risco_ruptura,
        },
        "registros": registros_selecionados,
    }


def responder(pergunta: str) -> str:
    """
    Orquestra o fluxo completo do AI Supply Chain Copilot.
    """

    inventario = listar_inventario()

    contexto = preparar_contexto(inventario)

    resposta = gerar_resposta(
        pergunta=pergunta,
        contexto=contexto,
    )

    return resposta


if __name__ == "__main__":
    pergunta = "Quais produtos apresentam prioridade alta?"

    resposta = responder(pergunta)

    print("\n")
    print("=" * 80)
    print("AI SUPPLY CHAIN COPILOT")
    print("=" * 80)
    print(resposta)