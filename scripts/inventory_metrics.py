import pandas as pd


def calcular_metricas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula os principais indicadores operacionais e financeiros
    relacionados ao estoque.

    A função altera o DataFrame recebido e o devolve atualizado.
    """

    calcular_valor_estoque(df)
    calcular_cobertura_e_risco(df)
    calcular_quantidades_e_valores(df)
    calcular_valor_acao(df)

    return df


def calcular_valor_estoque(df: pd.DataFrame) -> None:
    """
    Calcula o valor financeiro atualmente imobilizado em estoque.
    """

    df["valor_estoque"] = (
        df["estoque_atual"]
        * df["custo_unitario"]
    )


def calcular_cobertura_e_risco(df: pd.DataFrame) -> None:
    """
    Calcula cobertura de estoque, lead time em meses
    e risco de ruptura.
    """

    df["cobertura_meses"] = 0.0

    df.loc[
        df["consumo_medio_mensal"] > 0,
        "cobertura_meses"
    ] = (
        df["estoque_atual"]
        / df["consumo_medio_mensal"]
    )

    df["lead_time_meses"] = (
        df["lead_time_dias"] / 30
    )

    df["cobertura_meses"] = (
        df["cobertura_meses"].round(2)
    )

    df["lead_time_meses"] = (
        df["lead_time_meses"].round(2)
    )

    df["risco_ruptura"] = "NÃO"

    df.loc[
        df["cobertura_meses"] < df["lead_time_meses"],
        "risco_ruptura"
    ] = "SIM"


def calcular_quantidades_e_valores(
    df: pd.DataFrame
) -> None:
    """
    Calcula necessidades de reposição, excessos
    e seus respectivos impactos financeiros.
    """

    df["quantidade_repor"] = (
        df["estoque_minimo"]
        - df["estoque_atual"]
    ).clip(lower=0)

    df["valor_reposicao"] = (
        df["quantidade_repor"]
        * df["custo_unitario"]
    )

    df["quantidade_excesso"] = (
        df["estoque_atual"]
        - df["estoque_maximo"]
    ).clip(lower=0)

    df["valor_excesso"] = (
        df["quantidade_excesso"]
        * df["custo_unitario"]
    )


def calcular_valor_acao(df: pd.DataFrame) -> None:
    """
    Define o impacto financeiro principal da ação recomendada.
    """

    df["valor_acao"] = df[
        [
            "valor_reposicao",
            "valor_excesso"
        ]
    ].max(axis=1)