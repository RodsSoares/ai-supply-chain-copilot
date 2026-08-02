from pathlib import Path

import pandas as pd

from src.database.connection import conectar_banco


CAMINHO_PRODUTOS = Path("data/raw/produtos.csv")


def extrair_produtos() -> pd.DataFrame:
    """
    Lê o arquivo CSV de produtos.
    """

    if not CAMINHO_PRODUTOS.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {CAMINHO_PRODUTOS}"
        )

    return pd.read_csv(CAMINHO_PRODUTOS)


def transformar_produtos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida e padroniza os dados mestres de produtos.
    """

    colunas_esperadas = [
        "sku",
        "descricao",
        "grupo_gerencial",
        "unidade_medida",
        "peso_kg",
    ]

    colunas_ausentes = set(colunas_esperadas) - set(df.columns)

    if colunas_ausentes:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {colunas_ausentes}"
        )

    df = df.copy()

    df["sku"] = (
        df["sku"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["descricao"] = (
        df["descricao"]
        .astype(str)
        .str.strip()
    )

    df["grupo_gerencial"] = (
        df["grupo_gerencial"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    df["unidade_medida"] = (
        df["unidade_medida"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["peso_kg"] = pd.to_numeric(
        df["peso_kg"],
        errors="raise",
    )

    if df["sku"].duplicated().any():
        skus_duplicados = df.loc[
            df["sku"].duplicated(keep=False),
            "sku",
        ].unique()

        raise ValueError(
            f"SKUs duplicados encontrados: {list(skus_duplicados)}"
        )

    if (df["peso_kg"] < 0).any():
        raise ValueError(
            "O peso dos produtos não pode ser negativo."
        )

    return df[colunas_esperadas]


def carregar_produtos(df: pd.DataFrame) -> int:
    """
    Carrega no banco apenas os produtos que ainda não existem.
    """

    conexao = conectar_banco()

    try:
        produtos_existentes = pd.read_sql_query(
            "SELECT sku FROM produtos",
            conexao,
        )

        if not produtos_existentes.empty:
            df = df[
                ~df["sku"].isin(produtos_existentes["sku"])
            ].copy()

        if df.empty:
            print("Nenhum produto novo para carregar.")
            return 0

        df.to_sql(
            "produtos",
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
    Executa o pipeline ETL de produtos.
    """

    produtos = extrair_produtos()
    produtos = transformar_produtos(produtos)

    quantidade = carregar_produtos(produtos)

    print(
        f"{quantidade} produto(s) carregado(s) com sucesso."
    )


if __name__ == "__main__":
    main()