import os

import pandas as pd


def exportar_resultados(
    df: pd.DataFrame,
    caminho_saida: str = "output/inventory_analysis.csv"
) -> None:
    """
    Exporta o DataFrame final para CSV.

    A função também garante que a pasta de saída exista.
    """

    pasta_saida = os.path.dirname(caminho_saida)

    if pasta_saida:
        os.makedirs(
            pasta_saida,
            exist_ok=True
        )

    df.to_csv(
        caminho_saida,
        sep=";",
        decimal=",",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nArquivo exportado com sucesso!")
    print(f"Local: {caminho_saida}")