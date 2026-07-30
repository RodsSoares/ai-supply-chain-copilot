import pandas as pd

from inventory_validation import validar_dados
from inventory_metrics import calcular_metricas
from inventory_scoring import calcular_scores
from inventory_decision import aplicar_decisoes
from inventory_reporting import exibir_relatorio
from inventory_export import exportar_resultados


def main() -> None:
    df = pd.read_csv(
        "sample_data/erp_inventory.csv",
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