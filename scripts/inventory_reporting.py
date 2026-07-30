import pandas as pd


def exibir_relatorio(df: pd.DataFrame) -> None:
    """
    Exibe o relatório completo da análise de estoque.

    Esta função organiza as diferentes visões do relatório,
    sem alterar o DataFrame.
    """

    exibir_exploracao(df)
    exibir_acoes_recomendadas(df)
    exibir_distribuicao_das_acoes(df)
    exibir_resumo_executivo(df)


def exibir_exploracao(df: pd.DataFrame) -> None:
    """
    Exibe informações gerais sobre o conjunto de dados.
    """

    print("\n" + "=" * 50)
    print("EXPLORAÇÃO DOS DADOS")
    print("=" * 50)

    print("\nPRIMEIRAS LINHAS:")
    print(df.head())

    print("\nINFORMAÇÕES DO ARQUIVO:")
    df.info()

    print("\nDIMENSÕES DO ARQUIVO:")
    print(df.shape)

    print("\nNOMES DAS COLUNAS:")
    print(df.columns.tolist())


def exibir_acoes_recomendadas(df: pd.DataFrame) -> None:
    """
    Exibe uma amostra das decisões calculadas
    para os primeiros produtos.
    """

    colunas_relatorio = [
        "sku",
        "produto",
        "classe_abc",
        "estoque_atual",
        "estoque_minimo",
        "estoque_maximo",
        "cobertura_meses",
        "lead_time_meses",
        "risco_ruptura",
        "acao_recomendada",
        "quantidade_repor",
        "valor_reposicao",
        "quantidade_excesso",
        "valor_excesso",
        "valor_acao",
        "score_financeiro",
        "score_classe_abc",
        "score_risco_ruptura",
        "score_lead_time",
        "score_prioridade",
        "prioridade",
        "grupo_gerencial",
    ]

    print("\n" + "=" * 50)
    print("AÇÕES RECOMENDADAS — 10 PRIMEIROS PRODUTOS")
    print("=" * 50)

    print(
        df[colunas_relatorio].head(10)
    )


def exibir_distribuicao_das_acoes(
    df: pd.DataFrame
) -> None:
    """
    Exibe a quantidade de produtos por ação,
    prioridade e grupo gerencial.
    """

    print("\nQUANTIDADE DE PRODUTOS POR AÇÃO:")
    print(
        df["acao_recomendada"].value_counts()
    )

    print("\nQUANTIDADE DE PRODUTOS POR PRIORIDADE:")
    print(
        df["prioridade"].value_counts()
    )

    print("\nQUANTIDADE DE PRODUTOS POR GRUPO GERENCIAL:")
    print(
        df["grupo_gerencial"]
        .value_counts()
        .sort_index()
    )


def exibir_resumo_executivo(
    df: pd.DataFrame
) -> None:
    """
    Exibe os principais indicadores gerenciais
    da análise de estoque.
    """

    total_skus = len(df)

    valor_total_estoque = (
        df["valor_estoque"].sum()
    )

    produtos_reposicao = (
        df["acao_recomendada"] == "REPOR"
    ).sum()

    produtos_excesso = (
        df["acao_recomendada"] == "TRATAR EXCESSO"
    ).sum()

    produtos_sem_acao = (
        df["acao_recomendada"] == "SEM AÇÃO"
    ).sum()

    valor_reposicao = (
        df["valor_reposicao"].sum()
    )

    valor_excesso = (
        df["valor_excesso"].sum()
    )

    produtos_risco_ruptura = (
        df["risco_ruptura"] == "SIM"
    ).sum()

    cobertura_media = (
        df["cobertura_meses"].mean()
    )

    prioridade_alta = (
        df["prioridade"] == "ALTA"
    ).sum()

    prioridade_media = (
        df["prioridade"] == "MÉDIA"
    ).sum()

    prioridade_baixa = (
        df["prioridade"] == "BAIXA"
    ).sum()

    score_medio = (
        df["score_prioridade"].mean()
    )

    print("\n" + "=" * 50)
    print("RESUMO EXECUTIVO DO ESTOQUE")
    print("=" * 50)

    print(f"Total de SKUs: {total_skus}")

    print(
        f"Valor total do estoque: "
        f"R$ {valor_total_estoque:,.2f}"
    )

    print(
        f"Produtos para reposição: "
        f"{produtos_reposicao}"
    )

    print(
        f"Produtos com excesso: "
        f"{produtos_excesso}"
    )

    print(
        f"Produtos sem ação: "
        f"{produtos_sem_acao}"
    )

    print(
        f"Valor estimado para reposição: "
        f"R$ {valor_reposicao:,.2f}"
    )

    print(
        f"Valor financeiro em excesso: "
        f"R$ {valor_excesso:,.2f}"
    )

    print(
        f"Produtos com risco de ruptura: "
        f"{produtos_risco_ruptura}"
    )

    print(
        f"Cobertura média do estoque: "
        f"{cobertura_media:.2f} meses"
    )

    print(
        f"Ações com prioridade alta: "
        f"{prioridade_alta}"
    )

    print(
        f"Ações com prioridade média: "
        f"{prioridade_media}"
    )

    print(
        f"Ações com prioridade baixa: "
        f"{prioridade_baixa}"
    )

    print(
        f"Score médio de prioridade: "
        f"{score_medio:.2f}"
    )