"""Carga dos dados mestres do domínio Transportation."""

from pathlib import Path

import pandas as pd

from src.database.connection import conectar_banco


CAMINHO_ROUTES = Path("data/synthetic/transportation/routes.csv")
CAMINHO_VEHICLE_TYPES = Path("data/synthetic/transportation/vehicle_types.csv")
CAMINHO_ROUTE_VEHICLE_OPTIONS = Path("data/synthetic/transportation/route_vehicle_options.csv")
CAMINHO_ROUTE_VEHICLE_RATES = Path("data/synthetic/transportation/route_vehicle_rates.csv")


def extrair_routes() -> pd.DataFrame:
    """Extrai os dados sintéticos de rotas."""
    return pd.read_csv(CAMINHO_ROUTES)


def carregar_routes(df: pd.DataFrame) -> None:
    """Carrega as rotas na tabela routes."""
    with conectar_banco() as conexao:
        df.to_sql(
            "routes",
            conexao,
            if_exists="append",
            index=False,
        )


def extrair_vehicle_types() -> pd.DataFrame:
    """Extrai os dados sintéticos de tipos de veículos."""
    return pd.read_csv(CAMINHO_VEHICLE_TYPES)


def carregar_vehicle_types(df: pd.DataFrame) -> None:
    """Carrega os tipos de veículos na tabela vehicle_types."""
    with conectar_banco() as conexao:
        df.to_sql(
            "vehicle_types",
            conexao,
            if_exists="append",
            index=False,
        )


def extrair_route_vehicle_options() -> pd.DataFrame:
    """Extrai as combinações válidas entre rota e veículo."""
    return pd.read_csv(CAMINHO_ROUTE_VEHICLE_OPTIONS)


def carregar_route_vehicle_options(df: pd.DataFrame) -> None:
    """Carrega as combinações válidas entre rota e veículo."""
    with conectar_banco() as conexao:
        df.to_sql(
            "route_vehicle_options",
            conexao,
            if_exists="append",
            index=False,
        )


def extrair_route_vehicle_rates() -> pd.DataFrame:
    """Extrai as tarifas por combinação de rota e veículo."""
    return pd.read_csv(CAMINHO_ROUTE_VEHICLE_RATES)


def carregar_route_vehicle_rates(df: pd.DataFrame) -> None:
    """Carrega as tarifas por combinação de rota e veículo."""
    with conectar_banco() as conexao:
        df.to_sql(
            "route_vehicle_rates",
            conexao,
            if_exists="append",
            index=False,
        )


def main() -> None:
    """Executa a carga dos dados mestres de Transportation."""
    routes = extrair_routes()
    vehicle_types = extrair_vehicle_types()
    route_vehicle_options = extrair_route_vehicle_options()
    route_vehicle_rates = extrair_route_vehicle_rates()

    carregar_routes(routes)
    carregar_vehicle_types(vehicle_types)
    carregar_route_vehicle_options(route_vehicle_options)
    carregar_route_vehicle_rates(route_vehicle_rates)


if __name__ == "__main__":
    main()