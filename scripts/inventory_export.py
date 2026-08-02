from pathlib import Path

import pandas as pd


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_SAIDA_PADRAO = (
    RAIZ_PROJETO
    / "output"
    / "inventory_analysis.csv"
)


def exportar_resultados(
    df: pd.DataFrame,
    caminho_saida: str | Path = ARQUIVO_SAIDA_PADRAO,
) -> None:
    """
    Exporta o DataFrame final para CSV.

    A função garante que a pasta de saída exista e utiliza
    o diretório output da raiz como destino padrão.
    """
    caminho_saida = Path(caminho_saida)

    caminho_saida.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        caminho_saida,
        sep=";",
        decimal=",",
        index=False,
        encoding="utf-8-sig",
    )

    print("\nArquivo exportado com sucesso!")
    print(f"Local: {caminho_saida}")