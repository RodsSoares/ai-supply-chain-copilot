from pathlib import Path
import sqlite3

RAIZ_PROJETO = Path(__file__).resolve().parent.parent

CAMINHO_BANCO = RAIZ_PROJETO / "database" / "inventory.db"

conexao = sqlite3.connect(CAMINHO_BANCO)

conexao.close()

print("Banco de dados criado com sucesso!")