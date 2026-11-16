"""
Gera o Power BI Project (.pbip) do HUD V6 a partir do kit em reports/powerbi/kit.

Etapa 1 (este script): modelo semântico completo em TMDL
    - 13 tabelas importadas dos CSVs do kit (parâmetro PastaDados):
      7 do HUD V6 e 6 da rede v2.x (fato_rede_* e dim_rede_rotas)
    - 6 relacionamentos do guia de montagem
    - tabela _Medidas com todas as medidas de kit/dax/medidas.dax
e um relatório com as 3 páginas vazias em 1920 × 1080.

Fonte única: tipos vêm dos CSVs e medidas vêm do medidas.dax,
então basta rodar de novo depois de alterar o kit.

Uso:
    python scripts/build_powerbi_pbip.py
Depois: abrir reports/powerbi/pbip/AI_Supply_Chain_Copilot_HUD.pbip no Power BI Desktop.
"""

import json
import re
import shutil
import uuid
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[1]
KIT = RAIZ / "reports" / "powerbi" / "kit"
PASTA_DADOS = KIT / "data"
ARQUIVO_DAX = KIT / "dax" / "medidas.dax"
SAIDA = RAIZ / "reports" / "powerbi" / "pbip"
NOME = "AI_Supply_Chain_Copilot_HUD"

TABELAS = [
    "fato_estoque",
    "fato_viagens",
    "fato_demanda",
    "dim_rotas",
    "dim_veiculos",
    "dim_semana",
    "copilot_insights",
    # rede v2.x: geradas pelas consultas de sql/network
    "fato_rede_realizado",
    "fato_rede_extras",
    "fato_rede_pontualidade",
    "fato_rede_acuracia",
    "fato_rede_variabilidade",
    "dim_rede_rotas",
]
COLUNAS_DATA = {"semana_inicio", "data_ultima_movimentacao"}

# (muitos) -> (um), igual à seção 2 do guia
RELACIONAMENTOS = [
    ("fato_viagens", "rota", "dim_rotas", "rota"),
    ("fato_viagens", "semana_inicio", "dim_semana", "semana_inicio"),
    ("fato_viagens", "veiculo", "dim_veiculos", "veiculo"),
    ("fato_demanda", "rota", "dim_rotas", "rota"),
    ("fato_demanda", "semana_inicio", "dim_semana", "semana_inicio"),
    ("fato_rede_realizado", "rota_rede", "dim_rede_rotas", "rota_rede"),
]

PAGINAS = [
    ("command_center", "Command Center"),
    ("inventory", "Inventory"),
    ("transportation", "Transportation"),
]

TABELA_MEDIDAS = "_Medidas"
PADRAO_MEDIDA = re.compile(r"^((?:% )?[A-Za-z][A-Za-z0-9 ]*?) =(.*)$")


# ---------------------------------------------------------------------------
# utilitários
# ---------------------------------------------------------------------------

def tag(*partes: str) -> str:
    """lineageTag determinístico: gerar de novo não muda os arquivos."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "ai-supply-chain-copilot/hud/" + "/".join(partes)))


def nome_tmdl(nome: str) -> str:
    """Nomes com espaço ou símbolo vão entre aspas simples no TMDL."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
        return nome
    return "'" + nome.replace("'", "''") + "'"


def escrever(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def escrever_json(caminho: Path, dados: dict) -> None:
    escrever(caminho, json.dumps(dados, ensure_ascii=False, indent=2) + "\n")


# ---------------------------------------------------------------------------
# leitura do kit
# ---------------------------------------------------------------------------

def tipos_das_colunas(tabela: str) -> list[tuple[str, str]]:
    """[(coluna, tipo)] com tipo em {'string', 'int64', 'double', 'dateTime'}."""
    df = pd.read_csv(PASTA_DADOS / f"{tabela}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    tipos = []
    for coluna, dtype in df.dtypes.items():
        if coluna in COLUNAS_DATA:
            tipo = "dateTime"
        elif pd.api.types.is_integer_dtype(dtype):
            tipo = "int64"
        elif pd.api.types.is_float_dtype(dtype):
            tipo = "double"
        else:
            tipo = "string"
        tipos.append((coluna, tipo))
    return tipos


def ler_medidas() -> list[tuple[str, str]]:
    """[(nome, expressão)] na ordem de medidas.dax."""
    medidas: list[list] = []
    for linha in ARQUIVO_DAX.read_text(encoding="utf-8").splitlines():
        achou = PADRAO_MEDIDA.match(linha)
        if achou and not achou.group(1).startswith("VAR "):
            medidas.append([achou.group(1), [achou.group(2).strip()] if achou.group(2).strip() else []])
        elif medidas:
            medidas[-1][1].append(linha)

    resultado = []
    for nome, linhas in medidas:
        # comentários e linhas vazias entre uma medida e a próxima não fazem parte dela
        while linhas and (not linhas[-1].strip() or linhas[-1].lstrip().startswith("//")):
            linhas.pop()
        resultado.append((nome, "\n".join(linhas)))
    return resultado


def formato_medida(nome: str) -> str | None:
    if nome.startswith(("HTML", "Cor ")):
        return None
    if nome.startswith("%") or nome.startswith("Utilizacao") or nome in {"Var Custo vs S1", "Atendimento Demanda"}:
        return "0.0%"
    if nome in {"Custo por Peca", "Custo por Km", "Custo por Peca Rede"}:
        return "\\R$ #,0.00"
    if nome.startswith("Valor") or nome.startswith("Custo") and nome != "Custo Mil" or nome == "Consumo Mensal Valor":
        return "\\R$ #,0"
    if nome in {"Custo Mil", "Var Utilizacao pp"} or nome.startswith("Cobertura"):
        return "#,0.0"
    return "#,0"


# ---------------------------------------------------------------------------
# modelo semântico (TMDL)
# ---------------------------------------------------------------------------

TIPO_M = {"string": "type text", "int64": "Int64.Type", "double": "type number", "dateTime": "type date"}


def tmdl_tabela(tabela: str) -> str:
    colunas = tipos_das_colunas(tabela)
    linhas = [f"table {tabela}", f"\tlineageTag: {tag(tabela)}", ""]

    for coluna, tipo in colunas:
        linhas += [
            f"\tcolumn {nome_tmdl(coluna)}",
            f"\t\tdataType: {tipo}",
        ]
        if tipo == "dateTime":
            linhas.append("\t\tformatString: Short Date")
        linhas += [
            f"\t\tlineageTag: {tag(tabela, coluna)}",
            "\t\tsummarizeBy: none",
            f"\t\tsourceColumn: {coluna}",
            "",
            "\t\tannotation SummarizationSetBy = User",
        ]
        if tipo == "dateTime":
            linhas.append("\t\tannotation UnderlyingDateTimeDataType = Date")
        linhas.append("")

    tipos_m = ", ".join(f'{{"{c}", {TIPO_M[t]}}}' for c, t in colunas)
    linhas += [
        f"\tpartition {tabela} = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\t\tlet",
        f'\t\t\t\t    Fonte = Csv.Document(File.Contents(PastaDados & "{tabela}.csv"), [Delimiter = ";", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),',
        "\t\t\t\t    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),",
        f'\t\t\t\t    Tipos = Table.TransformColumnTypes(Cabecalhos, {{{tipos_m}}}, "pt-BR")',
        "\t\t\t\tin",
        "\t\t\t\t    Tipos",
        "",
        "\tannotation PBI_ResultType = Table",
        "",
    ]
    return "\n".join(linhas)


def tmdl_medidas() -> str:
    linhas = [f"table {TABELA_MEDIDAS}", f"\tlineageTag: {tag(TABELA_MEDIDAS)}", ""]

    for nome, expressao in ler_medidas():
        partes = expressao.split("\n")
        if len(partes) == 1:
            linhas.append(f"\tmeasure {nome_tmdl(nome)} = {partes[0]}")
        else:
            linhas.append(f"\tmeasure {nome_tmdl(nome)} =")
            linhas += [("\t\t\t" + p) if p.strip() else "" for p in partes]
        formato = formato_medida(nome)
        if formato:
            linhas.append(f"\t\tformatString: {formato}")
        if nome.startswith("HTML"):
            linhas.append("\t\tdisplayFolder: HTML")
        elif nome.startswith("Cor "):
            linhas.append("\t\tdisplayFolder: Cores")
        linhas += [f"\t\tlineageTag: {tag(TABELA_MEDIDAS, nome)}", ""]

    linhas += [
        "\tcolumn Coluna",
        "\t\tdataType: string",
        "\t\tisHidden",
        f"\t\tlineageTag: {tag(TABELA_MEDIDAS, 'Coluna')}",
        "\t\tsummarizeBy: none",
        "\t\tsourceColumn: Coluna",
        "",
        "\t\tannotation SummarizationSetBy = Automatic",
        "",
        f"\tpartition {TABELA_MEDIDAS} = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\t\tlet",
        "\t\t\t\t    Fonte = #table(type table [Coluna = text], {})",
        "\t\t\t\tin",
        "\t\t\t\t    Fonte",
        "",
        "\tannotation PBI_ResultType = Table",
        "",
    ]
    return "\n".join(linhas)


def gerar_modelo(pasta: Path) -> None:
    definicao = pasta / "definition"
    escrever_json(
        pasta / "definition.pbism",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
            "version": "4.2",
            "settings": {},
        },
    )
    escrever(definicao / "database.tmdl", "database\n\tcompatibilityLevel: 1567\n\n")

    ordem = ["PastaDados", *TABELAS, TABELA_MEDIDAS]
    escrever(
        definicao / "model.tmdl",
        "\n".join(
            [
                "model Model",
                "\tculture: pt-BR",
                "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
                "\tsourceQueryCulture: pt-BR",
                "\tdataAccessOptions",
                "\t\tlegacyRedirects",
                "\t\treturnErrorValuesAsNull",
                "",
                f"\tannotation PBI_QueryOrder = {json.dumps(ordem)}",
                "",
                "\tannotation __PBI_TimeIntelligenceEnabled = 0",
                "",
                *[f"ref table {nome_tmdl(t)}" for t in [*TABELAS, TABELA_MEDIDAS]],
                "",
            ]
        ),
    )

    caminho_dados = str(PASTA_DADOS) + "\\"
    escrever(
        definicao / "expressions.tmdl",
        "\n".join(
            [
                f'expression PastaDados = "{caminho_dados}" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]',
                f"\tlineageTag: {tag('PastaDados')}",
                "",
                "\tannotation PBI_ResultType = Text",
                "",
            ]
        ),
    )

    escrever(
        definicao / "relationships.tmdl",
        "\n".join(
            f"relationship {tag('rel', f, cf, d)}\n\tfromColumn: {f}.{cf}\n\ttoColumn: {d}.{cd}\n"
            for f, cf, d, cd in RELACIONAMENTOS
        ),
    )

    for tabela in TABELAS:
        escrever(definicao / "tables" / f"{tabela}.tmdl", tmdl_tabela(tabela))
    escrever(definicao / "tables" / f"{TABELA_MEDIDAS}.tmdl", tmdl_medidas())


# ---------------------------------------------------------------------------
# relatório (PBIR-Legacy: definition.pbir + report.json)
# ---------------------------------------------------------------------------

def gerar_relatorio(pasta: Path) -> None:
    escrever_json(
        pasta / "definition.pbir",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/1.0.0/schema.json",
            "version": "1.0",
            "datasetReference": {"byPath": {"path": f"../{NOME}.SemanticModel"}},
        },
    )
    secoes = [
        {
            "config": "{}",
            "displayName": titulo,
            "displayOption": 1,
            "filters": "[]",
            "height": 1080.0,
            "name": f"ReportSection_{pagina}",
            "ordinal": i,
            "visualContainers": [],
            "width": 1920.0,
        }
        for i, (pagina, titulo) in enumerate(PAGINAS)
    ]
    escrever_json(
        pasta / "report.json",
        {
            "config": json.dumps({"version": "5.43", "themeCollection": {}, "activeSectionIndex": 0}),
            "layoutOptimization": 0,
            "resourcePackages": [],
            "sections": secoes,
        },
    )


def main() -> None:
    # Só apaga o que este script gera; .pbi/ (cache local do Desktop) fica fora do controle.
    for pasta in (SAIDA / f"{NOME}.SemanticModel" / "definition", SAIDA / f"{NOME}.Report"):
        if pasta.exists():
            shutil.rmtree(pasta)

    gerar_modelo(SAIDA / f"{NOME}.SemanticModel")
    gerar_relatorio(SAIDA / f"{NOME}.Report")
    escrever_json(
        SAIDA / f"{NOME}.pbip",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
            "version": "1.0",
            "artifacts": [{"report": {"path": f"{NOME}.Report"}}],
            "settings": {"enableAutoRecovery": True},
        },
    )
    escrever(SAIDA / ".gitignore", "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")

    medidas = ler_medidas()
    print(f"{SAIDA / (NOME + '.pbip')}")
    print(f"  {len(TABELAS)} tabelas · {len(RELACIONAMENTOS)} relacionamentos · {len(medidas)} medidas · {len(PAGINAS)} páginas")


if __name__ == "__main__":
    main()
