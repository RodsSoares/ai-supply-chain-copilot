from pathlib import Path

import pandas as pd

from src.database.connection import conectar_banco


CAMINHO_DEPOSITOS = Path("data/raw/depositos.csv")


def extrair_depositos() -> pd.DataFrame:
    """
    Lê o arquivo CSV de depósitos.
    """

    if not CAMINHO_DEPOSITOS.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {CAMINHO_DEPOSITOS}"
        )

    return pd.read_csv(CAMINHO_DEPOSITOS)


def transformar_depositos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida e padroniza os dados mestres de depósitos.
    """

    colunas_esperadas = [
        "codigo_deposito",
        "descricao",
        "cidade",
        "uf",
    ]

    colunas_ausentes = set(colunas_esperadas) - set(df.columns)

    if colunas_ausentes:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {colunas_ausentes}"
        )

    df = df.copy()

    df["codigo_deposito"] = (
        df["codigo_deposito"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["descricao"] = (
        df["descricao"]
        .astype(str)
        .str.strip()
    )

    df["cidade"] = (
        df["cidade"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    df["uf"] = (
        df["uf"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    if df["codigo_deposito"].duplicated().any():
        depositos_duplicados = df.loc[
            df["codigo_deposito"].duplicated(keep=False),
            "codigo_deposito",
        ].unique()

        raise ValueError(
            "Códigos de depósito duplicados encontrados: "
            f"{list(depositos_duplicados)}"
        )

    if not df["uf"].str.fullmatch(r"[A-Z]{2}").all():
        raise ValueError(
            "Todos os valores de UF devem possuir exatamente duas letras."
        )

    return df[colunas_esperadas]


def carregar_depositos(df: pd.DataFrame) -> int:
    """
    Carrega no banco apenas os depósitos que ainda não existem.
    """

    conexao = conectar_banco()

    try:
        depositos_existentes = pd.read_sql_query(
            "SELECT codigo_deposito FROM depositos",
            conexao,
        )

        if not depositos_existentes.empty:
            df = df[
                ~df["codigo_deposito"].isin(
                    depositos_existentes["codigo_deposito"]
                )
            ].copy()

        if df.empty:
            print("Nenhum depósito novo para carregar.")
            return 0

        df.to_sql(
            "depositos",
            conexao,
            if_exists="append",
            index=False,
        )

        conexao.commit()

        return len(df)

    finally:
        conexao.close()


def main() -> None:
    """
    Executa o pipeline ETL de depósitos.
    """

    depositos = extrair_depositos()
    depositos = transformar_depositos(depositos)

    quantidade = carregar_depositos(depositos)

    print(
        f"{quantidade} depósito(s) carregado(s) com sucesso."
    )


if __name__ == "__main__":
    main()