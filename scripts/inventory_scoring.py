import pandas as pd


def calcular_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula os componentes do score multicritério
    e o score total de prioridade.

    A função altera o DataFrame recebido
    e devolve o DataFrame atualizado.
    """

    calcular_score_financeiro(df)
    calcular_score_classe_abc(df)
    calcular_score_risco_ruptura(df)
    calcular_score_lead_time(df)
    calcular_score_prioridade(df)

    return df


def calcular_score_financeiro(df: pd.DataFrame) -> None:
    """
    Calcula o score baseado no valor financeiro da ação.

    Faixas:
    - Até R$ 999,99: 10 pontos
    - De R$ 1.000 a R$ 4.999,99: 25 pontos
    - A partir de R$ 5.000: 40 pontos
    """

    df["score_financeiro"] = 0

    df.loc[
        (df["valor_acao"] > 0)
        & (df["valor_acao"] < 1000),
        "score_financeiro"
    ] = 10

    df.loc[
        (df["valor_acao"] >= 1000)
        & (df["valor_acao"] < 5000),
        "score_financeiro"
    ] = 25

    df.loc[
        df["valor_acao"] >= 5000,
        "score_financeiro"
    ] = 40


def calcular_score_classe_abc(df: pd.DataFrame) -> None:
    """
    Calcula o score de criticidade com base
    na classificação ABC.
    """

    df["score_classe_abc"] = 0

    df.loc[
        df["classe_abc"] == "C",
        "score_classe_abc"
    ] = 5

    df.loc[
        df["classe_abc"] == "B",
        "score_classe_abc"
    ] = 15

    df.loc[
        df["classe_abc"] == "A",
        "score_classe_abc"
    ] = 25


def calcular_score_risco_ruptura(
    df: pd.DataFrame
) -> None:
    """
    Adiciona pontuação quando o produto
    apresenta risco de ruptura.
    """

    df["score_risco_ruptura"] = 0

    df.loc[
        df["risco_ruptura"] == "SIM",
        "score_risco_ruptura"
    ] = 25


def calcular_score_lead_time(df: pd.DataFrame) -> None:
    """
    Calcula o score relacionado ao prazo
    de reposição do produto.

    Faixas:
    - Menos de 15 dias: 0 pontos
    - De 15 a 29 dias: 5 pontos
    - A partir de 30 dias: 10 pontos
    """

    df["score_lead_time"] = 0

    df.loc[
        (df["lead_time_dias"] >= 15)
        & (df["lead_time_dias"] < 30),
        "score_lead_time"
    ] = 5

    df.loc[
        df["lead_time_dias"] >= 30,
        "score_lead_time"
    ] = 10


def calcular_score_prioridade(
    df: pd.DataFrame
) -> None:
    """
    Soma todos os componentes do score multicritério.
    """

    df["score_prioridade"] = (
        df["score_financeiro"]
        + df["score_classe_abc"]
        + df["score_risco_ruptura"]
        + df["score_lead_time"]
    )