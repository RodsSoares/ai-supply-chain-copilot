import sqlite3
from pathlib import Path


CAMINHO_BANCO = Path("database/inventory.db")


def conectar_banco() -> sqlite3.Connection:
    """
    Cria e retorna uma conexão com o banco SQLite.
    """

    conexao = sqlite3.connect(CAMINHO_BANCO)

    conexao.row_factory = sqlite3.Row

    return conexao