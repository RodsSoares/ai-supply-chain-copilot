from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

from src.database.connection import conectar_banco


CAMINHO_INVENTARIO = Path("output/inventory_analysis.csv")


def carregar_inventario() -> pd.DataFrame:
    """
    Carrega o dataset analítico consolidado.
    """
    if not CAMINHO_INVENTARIO.exists():
        raise HTTPException(
            status_code=404,
            detail="Arquivo analítico de inventário não encontrado.",
        )

    return pd.read_csv(
        CAMINHO_INVENTARIO,
        sep=";",
        decimal=",",
    )


app = FastAPI(
    title="AI Supply Chain Copilot API",
    description=(
        "API REST para consulta dos dados e análises "
        "do AI Supply Chain Copilot."
    ),
    version="0.4.0",
)


@app.get("/")
def raiz() -> dict[str, str]:
    """
    Retorna informações básicas da API.
    """
    return {
        "message": "AI Supply Chain Copilot API",
        "status": "online",
    }


@app.get("/health")
def verificar_saude() -> dict[str, str]:
    """
    Verifica se a API está disponível.
    """
    return {
        "status": "healthy",
    }


@app.get("/products")
def listar_produtos() -> list[dict]:
    """
    Retorna todos os produtos cadastrados no banco SQLite.
    """
    conexao = conectar_banco()

    try:
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT
                sku,
                descricao,
                grupo_gerencial,
                unidade_medida,
                peso_kg
            FROM produtos
            ORDER BY sku
            """
        )

        produtos = [
            dict(linha)
            for linha in cursor.fetchall()
        ]

        return produtos

    finally:
        conexao.close()


@app.get("/products/{sku}")
def buscar_produto(sku: str) -> dict:
    """
    Retorna um produto específico pelo SKU.
    """
    conexao = conectar_banco()

    try:
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT
                sku,
                descricao,
                grupo_gerencial,
                unidade_medida,
                peso_kg
            FROM produtos
            WHERE sku = ?
            """,
            (sku,),
        )

        produto = cursor.fetchone()

        if produto is None:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado.",
            )

        return dict(produto)

    finally:
        conexao.close()


@app.get("/inventory")
def listar_inventario() -> list[dict]:
    """
    Retorna os dados analíticos consolidados de estoque.
    """
    df = carregar_inventario()

    df = df.astype(object).where(pd.notna(df), None)

    return df.to_dict(orient="records")


@app.get("/dashboard")
def obter_dashboard() -> dict[str, int | float]:
    """
    Retorna os principais indicadores executivos de estoque.
    """
    df = carregar_inventario()

    return {
        "total_skus": int(df["sku"].nunique()),
        "valor_total_estoque": round(
            float(df["valor_estoque"].sum()),
            2,
        ),
        "valor_total_reposicao": round(
            float(df["valor_reposicao"].sum()),
            2,
        ),
        "valor_total_excesso": round(
            float(df["valor_excesso"].sum()),
            2,
        ),
        "valor_total_acao": round(
            float(df["valor_acao"].sum()),
            2,
        ),
    }