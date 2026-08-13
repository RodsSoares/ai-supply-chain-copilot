import os

import pandas as pd


CAMINHO_CSV = "output/inventory_analysis.csv"
CAMINHO_EXCEL = "reports/excel/indicadores_r1.xlsx"
ABA_EXCEL = "inventory_analysis"


def exportar_resultados(
    df: pd.DataFrame,
    caminho_saida: str = CAMINHO_CSV
) -> None:
    """
    Exporta o DataFrame final para CSV e atualiza
    a aba de dados do relatório Excel.

    As demais abas existentes no arquivo Excel
    são preservadas.
    """

    exportar_csv(df, caminho_saida)
    exportar_excel(df)


def exportar_csv(
    df: pd.DataFrame,
    caminho_saida: str
) -> None:
    """
    Exporta o DataFrame final para CSV.
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

    print("\nArquivo CSV exportado com sucesso!")
    print(f"Local: {caminho_saida}")


def exportar_excel(
    df: pd.DataFrame,
    caminho_excel: str = CAMINHO_EXCEL
) -> None:
    """
    Atualiza a aba inventory_analysis do relatório Excel,
    preservando as demais abas do workbook.
    """

    pasta_saida = os.path.dirname(caminho_excel)

    if pasta_saida:
        os.makedirs(
            pasta_saida,
            exist_ok=True
        )

    if os.path.exists(caminho_excel):
        with pd.ExcelWriter(
            caminho_excel,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace"
        ) as writer:
            df.to_excel(
                writer,
                sheet_name=ABA_EXCEL,
                index=False
            )
    else:
        with pd.ExcelWriter(
            caminho_excel,
            engine="openpyxl"
        ) as writer:
            df.to_excel(
                writer,
                sheet_name=ABA_EXCEL,
                index=False
            )

    print("\nArquivo Excel atualizado com sucesso!")
    print(f"Local: {caminho_excel}")