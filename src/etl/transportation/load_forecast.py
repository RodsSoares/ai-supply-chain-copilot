"""ETL do forecast semanal do domínio Transportation."""

from datetime import date

from pathlib import Path

import pandas as pd

from src.database.connection import conectar_banco


CAMINHO_FORECAST = Path("data/raw/transportation/forecast_raw.csv")


def extrair_forecast() -> pd.DataFrame:
    """Extrai o forecast semanal recebido da fonte."""
    return pd.read_csv(CAMINHO_FORECAST)


def transformar_forecast(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma o forecast da fonte para o modelo canônico."""
    df_transformado = df.copy()

    df_transformado["week_start"] = df_transformado.apply(
        lambda linha: date.fromisocalendar(
            int(linha["year"]),
            int(linha["week"]),
            1,
        ).isoformat(),
        axis=1,
    )

    return df_transformado[
        ["week_start", "route_id", "forecast_pieces"]
    ]


def carregar_forecast_raw(df: pd.DataFrame) -> None:
    """Carrega o forecast recebido da fonte na tabela forecast_raw."""
    with conectar_banco() as conexao:
        df.to_sql(
            "forecast_raw",
            conexao,
            if_exists="append",
            index=False,
        )


def carregar_demand_forecast(df: pd.DataFrame) -> None:
    """Carrega o forecast transformado na tabela canônica demand_forecast."""
    with conectar_banco() as conexao:
        df.to_sql(
            "demand_forecast",
            conexao,
            if_exists="append",
            index=False,
        )

def main() -> None:
    """Executa o ETL do forecast semanal de Transportation."""
    forecast_raw = extrair_forecast()
    demand_forecast = transformar_forecast(forecast_raw)

    carregar_forecast_raw(forecast_raw)
    carregar_demand_forecast(demand_forecast)


if __name__ == "__main__":
    main()
