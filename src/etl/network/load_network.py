"""Carga da rede sintética (CSV -> SQLite, tabelas tn_*)."""

from pathlib import Path

import pandas as pd

from src.database.connection import conectar_banco
from src.database.create_network_tables import (
    ORDEM_CARGA,
    criar_tabelas_network,
    remover_tabelas_network,
)


DIRETORIO_NETWORK = Path("data/synthetic/transportation/network")


def extrair_tabela(nome: str, diretorio: Path = DIRETORIO_NETWORK) -> pd.DataFrame:
    """Lê uma tabela tn_* a partir do CSV gerado."""
    return pd.read_csv(diretorio / f"{nome}.csv", keep_default_na=True)


def carregar_network(diretorio: Path = DIRETORIO_NETWORK, recriar: bool = True) -> dict[str, int]:
    """Carrega todas as tabelas tn_* na ordem de dependência; retorna linhas por tabela."""
    if recriar:
        remover_tabelas_network()
    criar_tabelas_network()
    contagem = {}
    with conectar_banco() as conexao:
        for nome in ORDEM_CARGA:
            df = extrair_tabela(nome, diretorio)
            df = df.astype(object).where(pd.notna(df), None)
            colunas = list(df.columns)
            marcadores = ", ".join("?" for _ in colunas)
            conexao.executemany(
                f"INSERT INTO {nome} ({', '.join(colunas)}) VALUES ({marcadores})",
                df.itertuples(index=False, name=None),
            )
            contagem[nome] = len(df)
    return contagem


if __name__ == "__main__":
    for tabela, linhas in carregar_network().items():
        print(f"{tabela:<28} {linhas:>9,}")
