import pandas as pd

from business_rules import carregar_regras


REGRAS = carregar_regras()


def aplicar_decisoes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica as regras de decisão do sistema.

    A função define a ação recomendada, a prioridade
    e o grupo gerencial de cada produto.
    """

    calcular_acao_recomendada(df)
    calcular_prioridade(df)
    gerar_grupo_gerencial(df)

    return df


def calcular_acao_recomendada(df: pd.DataFrame) -> None:
    """
    Define a ação recomendada de acordo com os limites
    mínimo e máximo de estoque de cada produto.
    """

    df["acao_recomendada"] = "SEM AÇÃO"

    df.loc[
        df["estoque_atual"] < df["estoque_minimo"],
        "acao_recomendada",
    ] = "REPOR"

    df.loc[
        df["estoque_atual"] > df["estoque_maximo"],
        "acao_recomendada",
    ] = "TRATAR EXCESSO"


def calcular_prioridade(df: pd.DataFrame) -> None:
    """
    Converte o score multicritério em níveis de prioridade,
    utilizando os limites definidos em business_rules.json.
    """

    regras = REGRAS["priority"]

    limite_medio = regras["medium_threshold"]
    limite_alto = regras["high_threshold"]

    possui_acao = df["acao_recomendada"] != "SEM AÇÃO"

    df["prioridade"] = "SEM AÇÃO"

    df.loc[
        possui_acao
        & (df["score_prioridade"] < limite_medio),
        "prioridade",
    ] = "BAIXA"

    df.loc[
        possui_acao
        & (df["score_prioridade"] >= limite_medio)
        & (df["score_prioridade"] < limite_alto),
        "prioridade",
    ] = "MÉDIA"

    df.loc[
        possui_acao
        & (df["score_prioridade"] >= limite_alto),
        "prioridade",
    ] = "ALTA"


def gerar_grupo_gerencial(df: pd.DataFrame) -> None:
    """
    Gera uma classificação gerencial padronizada,
    utilizada em filtros, dashboards e tabelas dinâmicas.
    """

    def classificar_grupo_gerencial(linha: pd.Series) -> str:
        """
        Classifica uma linha conforme a ação recomendada
        e o nível de prioridade.
        """

        grupos = {
            ("REPOR", "ALTA"): "0 - REPOSIÇÃO — ALTA PRIORIDADE",
            (
                "TRATAR EXCESSO",
                "ALTA",
            ): "1 - EXCESSO — ALTA PRIORIDADE",
            ("REPOR", "MÉDIA"): "2 - REPOSIÇÃO — MÉDIA PRIORIDADE",
            (
                "TRATAR EXCESSO",
                "MÉDIA",
            ): "3 - EXCESSO — MÉDIA PRIORIDADE",
            ("REPOR", "BAIXA"): "4 - REPOSIÇÃO — BAIXA PRIORIDADE",
            (
                "TRATAR EXCESSO",
                "BAIXA",
            ): "5 - EXCESSO — BAIXA PRIORIDADE",
        }

        chave = (
            linha["acao_recomendada"],
            linha["prioridade"],
        )

        return grupos.get(
            chave,
            "6 - SEM AÇÃO",
        )

    df["grupo_gerencial"] = df.apply(
        classificar_grupo_gerencial,
        axis=1,
    )