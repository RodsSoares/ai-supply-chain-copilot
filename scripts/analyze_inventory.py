from pathlib import Path

import pandas as pd

from inventory_validation import validar_dados
from inventory_metrics import calcular_metricas
from inventory_scoring import calcular_scores
from inventory_decision import aplicar_decisoes
from inventory_reporting import exibir_relatorio
from inventory_export import exportar_resultados


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_ENTRADA = RAIZ_PROJETO / "sample_data" / "erp_inventory.csv"


def main() -> None:
    """
    Executa o pipeline completo de análise de inventário.
    """

    df = pd.read_csv(
        ARQUIVO_ENTRADA,
        sep=";",
        decimal="."
    )

    validar_dados(df)

    df = calcular_metricas(df)
    df = calcular_scores(df)
    df = aplicar_decisoes(df)

    exibir_relatorio(df)
    exportar_resultados(df)


if __name__ == "__main__":
    main()