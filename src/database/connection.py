from pathlib import Path
import sqlite3


RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
CAMINHO_BANCO = RAIZ_PROJETO / "database" / "inventory.db"


def conectar_banco():
    """
    Abre e retorna uma conexão com o banco SQLite.
    """

    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(CAMINHO_BANCO)

    return conexao