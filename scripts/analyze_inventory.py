import pandas as pd


# ==================================================
# LEITURA DOS DADOS
# ==================================================

df = pd.read_csv(
    "sample_data/erp_inventory.csv",
    sep=";",
    decimal="."
)


# ==================================================
# EXPLORAÇÃO DOS DADOS
# ==================================================

print("\nPRIMEIRAS LINHAS:")
print(df.head())

print("\nINFORMAÇÕES DO ARQUIVO:")
df.info()

print("\nDIMENSÕES DO ARQUIVO:")
print(df.shape)

print("\nNOMES DAS COLUNAS:")
print(df.columns.tolist())


# ==================================================
# VALIDAÇÃO DOS DADOS
# ==================================================

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


# ==================================================
# DETALHAMENTO DOS PROBLEMAS
# ==================================================

print("\n" + "=" * 50)
print("DETALHAMENTO DOS PROBLEMAS")
print("=" * 50)

skus_vazios_df = df[df["sku"].isna()]

skus_duplicados_df = df[
    df["sku"].duplicated(keep=False)
]

campos_criticos = [
    "sku",
    "produto",
    "estoque_atual",
    "estoque_minimo",
    "estoque_maximo",
    "custo_unitario"
]

campos_vazios = df[campos_criticos].isna().sum()

print("\nCampos críticos vazios:")
print(campos_vazios)

if len(skus_vazios_df) > 0:
    print("\nRegistros com SKU vazio:")
    print(skus_vazios_df)

if len(skus_duplicados_df) > 0:
    print("\nRegistros com SKU duplicado:")
    print(
        skus_duplicados_df[
            ["sku", "produto"]
        ]
    )


# ==================================================
# VALOR DO ESTOQUE
# ==================================================

df["valor_estoque"] = (
    df["estoque_atual"]
    * df["custo_unitario"]
)

print("\nVALOR EM ESTOQUE — 5 PRIMEIROS PRODUTOS:")

print(
    df[
        ["sku", "produto", "valor_estoque"]
    ].head()
)

print("\nVALOR TOTAL DO ESTOQUE:")

print(
    f"R$ {df['valor_estoque'].sum():,.2f}"
)

# ==================================================
# COBERTURA E RISCO DE RUPTURA
# ==================================================

df["cobertura_meses"] = 0.0

df.loc[
    df["consumo_medio_mensal"] > 0,
    "cobertura_meses"
] = (
    df["estoque_atual"]
    / df["consumo_medio_mensal"]
)

df["lead_time_meses"] = (
    df["lead_time_dias"] / 30
)

# Arredondamento para apresentação
df["cobertura_meses"] = df["cobertura_meses"].round(2)
df["lead_time_meses"] = df["lead_time_meses"].round(2)

df["risco_ruptura"] = "NÃO"

df.loc[
    df["cobertura_meses"] < df["lead_time_meses"],
    "risco_ruptura"
] = "SIM"

# ==================================================
# AÇÃO RECOMENDADA
# ==================================================

df["acao_recomendada"] = "SEM AÇÃO"

df.loc[
    df["estoque_atual"] < df["estoque_minimo"],
    "acao_recomendada"
] = "REPOR"

df.loc[
    df["estoque_atual"] > df["estoque_maximo"],
    "acao_recomendada"
] = "TRATAR EXCESSO"


# ==================================================
# QUANTIDADES E VALORES PARA AÇÃO
# ==================================================

df["quantidade_repor"] = (
    df["estoque_minimo"]
    - df["estoque_atual"]
).clip(lower=0)

df["valor_reposicao"] = (
    df["quantidade_repor"]
    * df["custo_unitario"]
)

df["quantidade_excesso"] = (
    df["estoque_atual"]
    - df["estoque_maximo"]
).clip(lower=0)

df["valor_excesso"] = (
    df["quantidade_excesso"]
    * df["custo_unitario"]
)


# ==================================================
# VALOR FINANCEIRO DA AÇÃO
# ==================================================

df["valor_acao"] = df[
    ["valor_reposicao", "valor_excesso"]
].max(axis=1)


# ==================================================
# PRIORIDADE DA AÇÃO
# ==================================================

df["prioridade"] = "SEM AÇÃO"

df.loc[
    (df["acao_recomendada"] != "SEM AÇÃO")
    & (df["valor_acao"] < 1000),
    "prioridade"
] = "BAIXA"

df.loc[
    (df["acao_recomendada"] != "SEM AÇÃO")
    & (df["valor_acao"] >= 1000)
    & (df["valor_acao"] < 5000),
    "prioridade"
] = "MÉDIA"

df.loc[
    (df["acao_recomendada"] != "SEM AÇÃO")
    & (df["valor_acao"] >= 5000),
    "prioridade"
] = "ALTA"


# ==================================================
# VISUALIZAÇÃO DAS AÇÕES
# ==================================================

print("\nAÇÕES RECOMENDADAS — 10 PRIMEIROS PRODUTOS:")

print(
    df[
        [
            "sku",
            "produto",
            "estoque_atual",
            "estoque_minimo",
            "estoque_maximo",
            "acao_recomendada",
            "valor_acao",
            "prioridade"
        ]
    ].head(10)
)

print("\nQUANTIDADE DE PRODUTOS POR AÇÃO:")

print(
    df["acao_recomendada"].value_counts()
)

print("\nQUANTIDADE DE PRODUTOS POR PRIORIDADE:")

print(
    df["prioridade"].value_counts()
)


# ==================================================
# RESUMO EXECUTIVO
# ==================================================

print("\n" + "=" * 50)
print("RESUMO EXECUTIVO DO ESTOQUE")
print("=" * 50)

print(f"Total de SKUs: {len(df)}")

print(
    f"Valor total do estoque: "
    f"R$ {df['valor_estoque'].sum():,.2f}"
)

print(
    f"Produtos para reposição: "
    f"{(df['acao_recomendada'] == 'REPOR').sum()}"
)

print(
    f"Produtos com excesso: "
    f"{(df['acao_recomendada'] == 'TRATAR EXCESSO').sum()}"
)

print(
    f"Produtos sem ação: "
    f"{(df['acao_recomendada'] == 'SEM AÇÃO').sum()}"
)

print(
    f"Valor estimado para reposição: "
    f"R$ {df['valor_reposicao'].sum():,.2f}"
)

print(
    f"Valor financeiro em excesso: "
    f"R$ {df['valor_excesso'].sum():,.2f}"
)

print(
    f"Ações com prioridade alta: "
    f"{(df['prioridade'] == 'ALTA').sum()}"
)

print(
    f"Ações com prioridade média: "
    f"{(df['prioridade'] == 'MÉDIA').sum()}"
)

print(
    f"Ações com prioridade baixa: "
    f"{(df['prioridade'] == 'BAIXA').sum()}"

    
)

print(
    f"Produtos com risco de ruptura: "
    f"{(df['risco_ruptura'] == 'SIM').sum()}"
)

print(
    f"Cobertura média do estoque: "
    f"{df['cobertura_meses'].mean():.2f} meses"
)

# ==================================================
# EXPORTAÇÃO DOS RESULTADOS
# ==================================================

df.to_csv(
    "output/inventory_analysis.csv",
    sep=";",
    decimal=",",
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo exportado com sucesso!")
print("Local: output/inventory_analysis.csv")