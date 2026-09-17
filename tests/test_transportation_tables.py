"""Testes do schema SQLite do domínio Transportation."""

import sqlite3

import src.database.connection as connection
import src.database.create_transportation_tables as transportation_tables


def test_criar_tabelas_transportation(tmp_path, monkeypatch):
    """Deve criar todas as tabelas iniciais do domínio Transportation."""
    banco_teste = tmp_path / "transportation_test.db"

    monkeypatch.setattr(
        connection,
        "CAMINHO_BANCO",
        banco_teste,
    )

    transportation_tables.criar_tabelas_transportation()

    with sqlite3.connect(banco_teste) as conexao:
        tabelas = {
            linha[0]
            for linha in conexao.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            )
        }

    tabelas_esperadas = {
        "routes",
        "vehicle_types",
        "route_vehicle_options",
        "route_vehicle_rates",
        "forecast_raw",
        "demand_forecast",
        "planned_trips",
    }

    assert tabelas_esperadas.issubset(tabelas)
    