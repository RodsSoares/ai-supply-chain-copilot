import pandas as pd

from business_rules import carregar_regras


REGRAS = carregar_regras()


def calcular_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula todos os componentes do score multicritério
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
    Calcula o score baseado no valor financeiro da ação,
    utilizando os parâmetros definidos no arquivo JSON.
    """

    regras = REGRAS["financial"]

    df["score_financeiro"] = 0

    df.loc[
        (df["valor_acao"] > 0)
        & (df["valor_acao"] < regras["low_limit"]),
        "score_financeiro",
    ] = regras["low_points"]

    df.loc[
        (df["valor_acao"] >= regras["low_limit"])
        & (df["valor_acao"] < regras["high_limit"]),
        "score_financeiro",
    ] = regras["medium_points"]

    df.loc[
        df["valor_acao"] >= regras["high_limit"],
        "score_financeiro",
    ] = regras["high_points"]


def calcular_score_classe_abc(df: pd.DataFrame) -> None:
    """
    Calcula o score baseado na classificação ABC,
    utilizando os pesos definidos no arquivo JSON.
    """

    regras = REGRAS["abc"]

    df["score_classe_abc"] = 0

    for classe, pontos in regras.items():
        df.loc[
            df["classe_abc"] == classe,
            "score_classe_abc",
        ] = pontos


def calcular_score_risco_ruptura(
    df: pd.DataFrame,
) -> None:
    """
    Adiciona pontuação quando existe risco de ruptura.
    """

    regras = REGRAS["stockout"]

    df["score_risco_ruptura"] = 0

    df.loc[
        df["risco_ruptura"] == "SIM",
        "score_risco_ruptura",
    ] = regras["points"]


def calcular_score_lead_time(df: pd.DataFrame) -> None:
    """
    Calcula o score baseado no prazo de reposição,
    utilizando as faixas definidas no arquivo JSON.
    """

    regras = REGRAS["lead_time"]

    df["score_lead_time"] = 0

    df.loc[
        (df["lead_time_dias"] >= regras["medium_days"])
        & (df["lead_time_dias"] < regras["high_days"]),
        "score_lead_time",
    ] = regras["medium_points"]

    df.loc[
        df["lead_time_dias"] >= regras["high_days"],
        "score_lead_time",
    ] = regras["high_points"]


def calcular_score_prioridade(
    df: pd.DataFrame,
) -> None:
    """
    Calcula o score multicritério total.
    """

    df["score_prioridade"] = (
        df["score_financeiro"]
        + df["score_classe_abc"]
        + df["score_risco_ruptura"]
        + df["score_lead_time"]
    )