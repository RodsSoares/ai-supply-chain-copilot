from src.ai.client import gerar_resposta
from src.ai.inventory_context import preparar_contexto
from src.ai.prompts import (
    INVENTORY_PROMPT,
    SYSTEM_PROMPT,
    TRANSPORTATION_PROMPT,
)
from src.ai.tools import listar_inventario
from src.ai.transportation_context import (
    preparar_contexto_transporte,
)
from src.ai.transportation_dispatcher import (
    executar_intencao_transporte,
)
from src.ai.transportation_router import (
    rotear_pergunta_transporte,
)


DOMINIOS_SUPORTADOS = {
    "inventory",
    "transportation",
}


def responder(
    pergunta: str,
    dominio: str = "inventory",
) -> str:
    """
    Orquestra o fluxo completo do AI Supply Chain Copilot.

    O domínio é definido explicitamente pela camada chamadora.
    Inventory preserva o fluxo original.

    Transportation utiliza LLM apenas para interpretar a intenção.
    A execução analítica permanece determinística.
    """

    if dominio not in DOMINIOS_SUPORTADOS:
        raise ValueError(
            f"Domínio não suportado: {dominio}"
        )

    if dominio == "inventory":
        return responder_inventory(pergunta)

    return responder_transportation(pergunta)


def responder_inventory(pergunta: str) -> str:
    """
    Executa o fluxo de Inventory.
    """

    inventario = listar_inventario()

    contexto = preparar_contexto(inventario)

    instrucoes = (
        SYSTEM_PROMPT
        + "\n\n"
        + INVENTORY_PROMPT
    )

    return gerar_resposta(
        pergunta=pergunta,
        contexto=contexto,
        instrucoes=instrucoes,
    )


def responder_transportation(pergunta: str) -> str:
    """
    Executa o fluxo de Transportation.

    Fluxo:
    pergunta
    -> router probabilístico
    -> intent estruturada
    -> dispatcher determinístico
    -> analytics / SQL
    -> contexto
    -> resposta explicativa
    """

    intencao = rotear_pergunta_transporte(pergunta)

    if intencao.intent == "out_of_scope":
        return (
            "A pergunta está fora do escopo analítico "
            "de Transportation."
        )

    resultado_analitico = executar_intencao_transporte(
        intencao
    )

    contexto = preparar_contexto_transporte(
        tipo_analise=intencao.intent,
        resultado_analitico=resultado_analitico,
    )

    instrucoes = (
        SYSTEM_PROMPT
        + "\n\n"
        + TRANSPORTATION_PROMPT
    )

    return gerar_resposta(
        pergunta=pergunta,
        contexto=contexto,
        instrucoes=instrucoes,
    )


if __name__ == "__main__":
    pergunta = "Quais produtos apresentam prioridade alta?"

    resposta = responder(
        pergunta=pergunta,
        dominio="inventory",
    )

    print("\n")
    print("=" * 80)
    print("AI SUPPLY CHAIN COPILOT")
    print("=" * 80)
    print(resposta)