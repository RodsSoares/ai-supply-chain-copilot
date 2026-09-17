import sqlite3
from pathlib import Path


CAMINHO_BANCO = Path("database/supply_chain.db")


def conectar_banco() -> sqlite3.Connection:
    """
    Cria e retorna uma conexão com o banco SQLite.
    """

    conexao = sqlite3.connect(CAMINHO_BANCO)

    conexao.row_factory = sqlite3.Row

    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao