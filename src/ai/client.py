import json
import os
from typing import Any

from openai import OpenAI

from src.ai.prompts import SYSTEM_PROMPT


MODO_CLIENTE = os.getenv(
    "LLM_MODE",
    "fake",
).strip().lower()

LLM_REAL_ENABLED = os.getenv(
    "LLM_REAL_ENABLED",
    "false",
).strip().lower() == "true"

LIMITE_CARACTERES_CONTEXTO = 20000
LIMITE_TOKENS_RESPOSTA = 1500
MODELO_LLM = "gpt-5.6-terra"


def validar_configuracao_cliente() -> None:
    """
    Valida a configuração do cliente de IA.

    O modo real exige autorização explícita por meio
    de duas variáveis de ambiente independentes.
    """

    if MODO_CLIENTE == "fake":
        return

    if MODO_CLIENTE == "real":
        if not LLM_REAL_ENABLED:
            raise RuntimeError(
                "O modo real está bloqueado. "
                "Defina LLM_REAL_ENABLED=true para autorizar "
                "explicitamente chamadas ao provedor."
            )

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY não configurada."
            )

        return

    raise ValueError(
        f"Modo de cliente não suportado: {MODO_CLIENTE}"
    )


def validar_limites_contexto(
    contexto: Any | None,
) -> None:
    """
    Valida o tamanho do contexto antes de qualquer chamada ao LLM.

    O limite em caracteres funciona como uma barreira simples
    e independente de provedor contra requisições excessivamente grandes.
    """

    if contexto is None:
        return

    try:
        contexto_serializado = json.dumps(
            contexto,
            ensure_ascii=False,
            default=str,
        )

    except (TypeError, ValueError) as erro:
        raise ValueError(
            "O contexto não pôde ser serializado."
        ) from erro

    if len(contexto_serializado) > LIMITE_CARACTERES_CONTEXTO:
        raise ValueError(
            "O contexto excede o limite permitido "
            f"de {LIMITE_CARACTERES_CONTEXTO} caracteres."
        )


def montar_requisicao(
    pergunta: str,
    contexto: Any | None = None,
) -> dict[str, Any]:
    """
    Monta a estrutura lógica que será enviada ao LLM.

    Esta função não realiza chamadas externas.
    Ela apenas organiza system prompt, contexto e pergunta.
    """

    if not pergunta.strip():
        raise ValueError("A pergunta não pode estar vazia.")

    validar_limites_contexto(contexto)

    return {
        "system_prompt": SYSTEM_PROMPT,
        "contexto": contexto,
        "pergunta": pergunta,
    }


def gerar_resposta(
    pergunta: str,
    contexto: Any | None = None,
) -> str:
    """
    Gera uma resposta utilizando o cliente de IA configurado.

    O modo fake permite desenvolvimento e testes sem consumo de API.
    O modo real utiliza o provedor configurado.
    """

    validar_configuracao_cliente()

    requisicao = montar_requisicao(
        pergunta=pergunta,
        contexto=contexto,
    )

    if MODO_CLIENTE == "fake":
        return gerar_resposta_fake(
            pergunta=requisicao["pergunta"],
            contexto=requisicao["contexto"],
        )

    if MODO_CLIENTE == "real":
        return gerar_resposta_real(
            pergunta=requisicao["pergunta"],
            contexto=requisicao["contexto"],
        )

    raise RuntimeError(
        f"Modo de cliente não suportado: {MODO_CLIENTE}"
    )


def gerar_resposta_real(
    pergunta: str,
    contexto: Any | None = None,
) -> str:
    """
    Gera uma resposta utilizando o provedor real de IA.
    """

    validar_limites_contexto(contexto)

    cliente = OpenAI()

    contexto_serializado = json.dumps(
        contexto,
        ensure_ascii=False,
        default=str,
    )

    entrada = (
        "Contexto fornecido pelo sistema:\n\n"
        f"{contexto_serializado}\n\n"
        "Pergunta do usuário:\n\n"
        f"{pergunta}"
    )

    resposta = cliente.responses.create(
        model=MODELO_LLM,
        instructions=SYSTEM_PROMPT,
        input=entrada,
        max_output_tokens=LIMITE_TOKENS_RESPOSTA,
    )

    return resposta.output_text


def gerar_resposta_fake(
    pergunta: str,
    contexto: Any | None = None,
) -> str:
    """
    Simula a resposta de um modelo de linguagem.

    Esta implementação não utiliza inteligência artificial real.
    Ela existe para validar a integração entre os componentes.
    """

    if contexto is None:
        return (
            "Não foi possível realizar a análise porque nenhum dado "
            "do sistema foi disponibilizado."
        )

    quantidade_registros = obter_quantidade_registros(contexto)

    return (
        "Os dados do sistema foram recebidos corretamente.\n\n"
        f"Registros disponíveis para análise: {quantidade_registros}.\n\n"
        f"Pergunta recebida: {pergunta}\n\n"
        "Esta resposta foi produzida pelo cliente simulado. "
        "A interpretação em linguagem natural será realizada por um "
        "modelo real quando a integração com o provedor de IA for ativada."
    )


def obter_quantidade_registros(
    contexto: Any,
) -> int:
    """
    Obtém a quantidade de registros detalhados disponíveis no contexto.
    """

    if isinstance(contexto, list):
        return len(contexto)

    if isinstance(contexto, dict):
        registros = contexto.get("registros")

        if isinstance(registros, list):
            return len(registros)

    return 1


if __name__ == "__main__":
    contexto_teste = {
        "resumo": {
            "total_registros": 2,
            "prioridade_alta": 1,
            "risco_ruptura": 1,
        },
        "registros": [
            {
                "sku": "SKU-001",
                "prioridade": "ALTA",
                "acao_recomendada": "REPOR",
            },
            {
                "sku": "SKU-002",
                "prioridade": "MEDIA",
                "acao_recomendada": "TRATAR EXCESSO",
            },
        ],
    }

    resposta = gerar_resposta(
        pergunta="Quais produtos devo priorizar?",
        contexto=contexto_teste,
    )

    print(resposta)