from src.ai.client import gerar_resposta
from src.ai.context import preparar_contexto
from src.ai.tools import listar_inventario


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