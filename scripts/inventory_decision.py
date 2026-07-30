import pandas as pd


def aplicar_decisoes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas as regras de negócio do sistema.
    """

    calcular_acao_recomendada(df)
    calcular_prioridade(df)
    gerar_grupo_gerencial(df)

    return df


def calcular_acao_recomendada(df: pd.DataFrame) -> None:
    """
    Define a ação recomendada para cada produto.
    """

    df["acao_recomendada"] = "SEM AÇÃO"

    df.loc[
        df["estoque_atual"] < df["estoque_minimo"],
        "acao_recomendada"
    ] = "REPOR"

    df.loc[
        df["estoque_atual"] > df["estoque_maximo"],
        "acao_recomendada"
    ] = "TRATAR EXCESSO"


def calcular_prioridade(df: pd.DataFrame) -> None:
    """
    Converte o score multicritério
    em níveis de prioridade.
    """

    df["prioridade"] = "SEM AÇÃO"

    df.loc[
        (df["acao_recomendada"] != "SEM AÇÃO")
        & (df["score_prioridade"] < 40),
        "prioridade"
    ] = "BAIXA"

    df.loc[
        (df["acao_recomendada"] != "SEM AÇÃO")
        & (df["score_prioridade"] >= 40)
        & (df["score_prioridade"] < 70),
        "prioridade"
    ] = "MÉDIA"

    df.loc[
        (df["acao_recomendada"] != "SEM AÇÃO")
        & (df["score_prioridade"] >= 70),
        "prioridade"
    ] = "ALTA"


def gerar_grupo_gerencial(df: pd.DataFrame) -> None:
    """
    Gera uma classificação gerencial padronizada,
    utilizada em filtros, dashboards e tabelas dinâmicas.
    """

    def classificar_grupo_gerencial(linha):

        if linha["acao_recomendada"] == "REPOR":

            if linha["prioridade"] == "ALTA":
                return "0 - REPOSIÇÃO — ALTA PRIORIDADE"

            if linha["prioridade"] == "MÉDIA":
                return "2 - REPOSIÇÃO — MÉDIA PRIORIDADE"

            if linha["prioridade"] == "BAIXA":
                return "4 - REPOSIÇÃO — BAIXA PRIORIDADE"

        elif linha["acao_recomendada"] == "TRATAR EXCESSO":

            if linha["prioridade"] == "ALTA":
                return "1 - EXCESSO — ALTA PRIORIDADE"

            if linha["prioridade"] == "MÉDIA":
                return "3 - EXCESSO — MÉDIA PRIORIDADE"

            if linha["prioridade"] == "BAIXA":
                return "5 - EXCESSO — BAIXA PRIORIDADE"

        return "6 - SEM AÇÃO"

    df["grupo_gerencial"] = df.apply(
        classificar_grupo_gerencial,
        axis=1
    )