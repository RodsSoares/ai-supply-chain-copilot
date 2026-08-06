from typing import Any


MODO_CLIENTE = "fake"


def gerar_resposta(
    pergunta: str,
    contexto: Any | None = None,
) -> str:
    """
    Gera uma resposta utilizando o cliente de IA configurado.

    No modo atual, utiliza uma implementação simulada para permitir
    o desenvolvimento da arquitetura sem consumo de API.

    Args:
        pergunta: Pergunta enviada pelo usuário.
        contexto: Dados estruturados disponibilizados ao cliente.

    Returns:
        Resposta textual produzida pelo cliente configurado.
    """

    if not pergunta.strip():
        raise ValueError("A pergunta não pode estar vazia.")

    if MODO_CLIENTE == "fake":
        return gerar_resposta_fake(
            pergunta=pergunta,
            contexto=contexto,
        )

    raise ValueError(
        f"Modo de cliente não suportado: {MODO_CLIENTE}"
    )


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

    quantidade_registros = (
        len(contexto)
        if isinstance(contexto, list)
        else 1
    )

    return (
        "Os dados do sistema foram recebidos corretamente.\n\n"
        f"Registros disponíveis para análise: {quantidade_registros}.\n\n"
        f"Pergunta recebida: {pergunta}\n\n"
        "Esta resposta foi produzida pelo cliente simulado. "
        "A interpretação em linguagem natural será realizada por um "
        "modelo real quando a integração com o provedor de IA for ativada."
    )


if __name__ == "__main__":
    contexto_teste = [
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
    ]

    resposta = gerar_resposta(
        pergunta="Quais produtos devo priorizar?",
        contexto=contexto_teste,
    )

    print(resposta)