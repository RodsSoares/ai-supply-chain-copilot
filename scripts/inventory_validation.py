import pandas as pd


CAMPOS_CRITICOS = [
    "sku",
    "produto",
    "estoque_atual",
    "estoque_minimo",
    "estoque_maximo",
    "custo_unitario",
    "consumo_medio_mensal",
    "lead_time_dias",
    "classe_abc"
]


def validar_dados(df: pd.DataFrame) -> None:
    """
    Exibe indicadores de qualidade dos dados.

    Esta função não altera o DataFrame.
    Ela apenas identifica e apresenta possíveis problemas.
    """

    print("\n" + "=" * 50)
    print("VALIDAÇÃO DOS DADOS")
    print("=" * 50)

    total_linhas = len(df)
    skus_preenchidos = df["sku"].count()
    skus_unicos = df["sku"].nunique()
    skus_vazios = df["sku"].isna().sum()
    skus_duplicados = df["sku"].duplicated().sum()

    print(f"Total de linhas: {total_linhas}")
    print(f"SKUs preenchidos: {skus_preenchidos}")
    print(f"SKUs únicos: {skus_unicos}")
    print(f"SKUs vazios: {skus_vazios}")
    print(f"SKUs duplicados: {skus_duplicados}")

    detalhar_problemas(df)


def detalhar_problemas(df: pd.DataFrame) -> None:
    """
    Apresenta registros incompletos e SKUs duplicados.
    """

    print("\n" + "=" * 50)
    print("DETALHAMENTO DOS PROBLEMAS")
    print("=" * 50)

    skus_vazios_df = df[
        df["sku"].isna()
    ]

    skus_duplicados_df = df[
        df["sku"].duplicated(keep=False)
    ]

    campos_vazios = df[
        CAMPOS_CRITICOS
    ].isna().sum()

    print("\nCampos críticos vazios:")
    print(campos_vazios)

    if not skus_vazios_df.empty:
        print("\nRegistros com SKU vazio:")
        print(skus_vazios_df)

    if not skus_duplicados_df.empty:
        print("\nRegistros com SKU duplicado:")
        print(
            skus_duplicados_df[
                ["sku", "produto"]
            ]
        )