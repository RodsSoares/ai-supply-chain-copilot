from src.ai.client import gerar_resposta
from src.ai.tools import listar_inventario


def responder(pergunta: str) -> str:
    """
    Orquestra o fluxo completo do AI Supply Chain Copilot.

    Fluxo:

    Usuário
        ↓
    Tools
        ↓
    API
        ↓
    Client (LLM)
        ↓
    Resposta
    """

    inventario = listar_inventario()

    resposta = gerar_resposta(
        pergunta=pergunta,
        contexto=inventario,
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