from __future__ import annotations

import ast
import sys
import tokenize
from collections import Counter
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
PASTA_SAIDA = RAIZ_PROJETO / "docs" / "project_audit"
ARQUIVO_SAIDA = PASTA_SAIDA / "PROJECT_AUDIT.md"

# CONFIGURAÇÕES DE USO
#
# False: opção desativada.
# True: opção ativada.
#
# Exemplos:
# INCLUIR_CODIGO_FONTE = True
#   Inclui todo o conteúdo dos arquivos .py no final do relatório.
#
# INCLUIR_FERRAMENTAS_AUDITORIA = True
#   Inclui o próprio project_audit.py nas métricas do projeto.
#
# Para o checkpoint normal, mantenha ambas como False.
INCLUIR_CODIGO_FONTE = False
INCLUIR_FERRAMENTAS_AUDITORIA = False

PASTAS_IGNORADAS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}

ARQUIVOS_IGNORADOS = {
    "__init__.py",
}

PIPELINE_PRINCIPAL = [
    "scripts/analyze_inventory.py",
    "scripts/inventory_validation.py",
    "scripts/inventory_metrics.py",
    "scripts/inventory_scoring.py",
    "scripts/inventory_decision.py",
    "scripts/inventory_reporting.py",
    "scripts/inventory_export.py",
]


ARTEFATOS_PROJETO = {
    "Banco SQLite": "database/inventory.db",
    "Arquivo analítico": "output/inventory_analysis.csv",
    "Relatório Excel": "reports/excel/indicadores_r1.xlsx",
    "Dashboard Power BI": (
        "reports/powerbi/AI_Supply_Chain_Copilot.pbix"
    ),
    "Screenshot do dashboard": (
        "reports/powerbi/screenshots/dashboard.png"
    ),
}


def deve_ignorar(caminho: Path) -> bool:
    """
    Verifica se um caminho pertence a uma pasta ou arquivo ignorado.
    """
    relativo = caminho.relative_to(RAIZ_PROJETO)

    if any(parte in PASTAS_IGNORADAS for parte in relativo.parts):
        return True

    return caminho.name in ARQUIVOS_IGNORADOS


def localizar_arquivos_python() -> list[Path]:
    """
    Localiza todos os arquivos Python válidos do projeto.

    O próprio auditor é excluído por padrão para não distorcer
    as métricas do produto. Para incluí-lo, altere
    INCLUIR_FERRAMENTAS_AUDITORIA para True.
    """
    arquivos = []

    for arquivo in RAIZ_PROJETO.rglob("*.py"):
        if not arquivo.is_file() or deve_ignorar(arquivo):
            continue

        if (
            not INCLUIR_FERRAMENTAS_AUDITORIA
            and arquivo.resolve() == Path(__file__).resolve()
        ):
            continue

        arquivos.append(arquivo)

    return sorted(arquivos)


def localizar_estrutura_projeto() -> list[Path]:
    """
    Localiza arquivos e diretórios relevantes para o mapa estrutural.
    """
    caminhos: list[Path] = []

    for caminho in RAIZ_PROJETO.rglob("*"):
        if deve_ignorar(caminho):
            continue

        relativo = caminho.relative_to(RAIZ_PROJETO)

        if len(relativo.parts) > 4:
            continue

        caminhos.append(caminho)

    return sorted(
        caminhos,
        key=lambda item: item.relative_to(RAIZ_PROJETO).as_posix(),
    )


def ler_codigo(arquivo: Path) -> str:
    """
    Lê um arquivo Python usando UTF-8.
    """
    return arquivo.read_text(encoding="utf-8")


def caminho_para_modulo(caminho_relativo: str) -> str:
    """
    Converte um caminho Python em nome de módulo.
    """
    caminho = Path(caminho_relativo)

    if caminho.name == "__init__.py":
        caminho = caminho.parent
    else:
        caminho = caminho.with_suffix("")

    return ".".join(caminho.parts)


def extrair_todos_de_comentarios(codigo: str) -> list[dict[str, Any]]:
    """
    Localiza TODOs e FIXMEs somente em comentários Python.
    """
    encontrados: list[dict[str, Any]] = []

    try:
        tokens = tokenize.generate_tokens(StringIO(codigo).readline)

        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue

            texto = token.string.strip()

            if "TODO" in texto.upper() or "FIXME" in texto.upper():
                encontrados.append(
                    {
                        "linha": token.start[0],
                        "texto": texto,
                    }
                )

    except (IndentationError, tokenize.TokenError):
        pass

    return encontrados


def analisar_arquivo(arquivo: Path) -> dict[str, Any]:
    """
    Analisa estrutura, imports, funções, classes e qualidade básica.
    """
    caminho_relativo = arquivo.relative_to(RAIZ_PROJETO).as_posix()
    modulo = caminho_para_modulo(caminho_relativo)
    codigo = ler_codigo(arquivo)
    linhas = codigo.splitlines()

    resultado: dict[str, Any] = {
        "arquivo": caminho_relativo,
        "modulo": modulo,
        "diretorio_raiz": Path(caminho_relativo).parts[0],
        "linhas": len(linhas),
        "linhas_codigo": sum(
            1
            for linha in linhas
            if linha.strip() and not linha.strip().startswith("#")
        ),
        "funcoes": [],
        "classes": [],
        "imports": [],
        "todos": extrair_todos_de_comentarios(codigo),
        "erro_sintaxe": "",
        "codigo": codigo,
    }

    try:
        arvore = ast.parse(codigo, filename=caminho_relativo)
    except SyntaxError as erro:
        resultado["erro_sintaxe"] = f"Linha {erro.lineno}: {erro.msg}"
        return resultado

    for no in ast.walk(arvore):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            argumentos = [
                argumento.arg
                for argumento in (
                    list(no.args.posonlyargs)
                    + list(no.args.args)
                    + list(no.args.kwonlyargs)
                )
            ]

            if no.args.vararg:
                argumentos.append(f"*{no.args.vararg.arg}")

            if no.args.kwarg:
                argumentos.append(f"**{no.args.kwarg.arg}")

            resultado["funcoes"].append(
                {
                    "nome": no.name,
                    "linha": no.lineno,
                    "linha_final": getattr(no, "end_lineno", no.lineno),
                    "assincrona": isinstance(no, ast.AsyncFunctionDef),
                    "docstring": bool(ast.get_docstring(no)),
                    "argumentos": argumentos,
                }
            )

        elif isinstance(no, ast.ClassDef):
            resultado["classes"].append(
                {
                    "nome": no.name,
                    "linha": no.lineno,
                    "linha_final": getattr(no, "end_lineno", no.lineno),
                    "docstring": bool(ast.get_docstring(no)),
                }
            )

        elif isinstance(no, ast.Import):
            for alias in no.names:
                resultado["imports"].append(
                    {
                        "tipo": "import",
                        "modulo": alias.name,
                        "nome": "",
                        "linha": no.lineno,
                        "nivel": 0,
                    }
                )

        elif isinstance(no, ast.ImportFrom):
            modulo_importado = no.module or ""

            for alias in no.names:
                resultado["imports"].append(
                    {
                        "tipo": "from",
                        "modulo": modulo_importado,
                        "nome": alias.name,
                        "linha": no.lineno,
                        "nivel": no.level,
                    }
                )

    resultado["funcoes"].sort(key=lambda item: item["linha"])
    resultado["classes"].sort(key=lambda item: item["linha"])
    resultado["imports"].sort(key=lambda item: item["linha"])

    return resultado


def construir_indice_modulos(
    resultados: list[dict[str, Any]],
) -> dict[str, str]:
    """
    Cria um índice nome_do_modulo -> caminho_do_arquivo.
    """
    return {
        resultado["modulo"]: resultado["arquivo"]
        for resultado in resultados
    }


def resolver_modulo_importado(
    resultado_origem: dict[str, Any],
    importacao: dict[str, Any],
    indice_modulos: dict[str, str],
) -> str:
    """
    Tenta resolver um import para um módulo interno do projeto.
    """
    modulo = importacao["modulo"]
    nome = importacao["nome"]
    nivel = importacao["nivel"]

    candidatos: list[str] = []

    if nivel > 0:
        partes_origem = resultado_origem["modulo"].split(".")[:-1]
        subir = max(nivel - 1, 0)

        if subir:
            partes_origem = partes_origem[:-subir]

        base = ".".join(partes_origem)

        if modulo:
            candidatos.append(f"{base}.{modulo}" if base else modulo)
        elif nome:
            candidatos.append(f"{base}.{nome}" if base else nome)

    if modulo:
        candidatos.append(modulo)

        if nome:
            candidatos.append(f"{modulo}.{nome}")

    elif nome:
        candidatos.append(nome)

    for candidato in candidatos:
        if candidato in indice_modulos:
            return candidato

    modulo_curto = modulo.split(".")[0] if modulo else ""

    for modulo_interno in indice_modulos:
        if modulo_interno.split(".")[-1] == modulo_curto:
            return modulo_interno

    return ""


def classificar_import(
    resultado_origem: dict[str, Any],
    importacao: dict[str, Any],
    indice_modulos: dict[str, str],
) -> tuple[str, str]:
    """
    Classifica um import como interno, biblioteca padrão ou externo.
    """
    modulo_interno = resolver_modulo_importado(
        resultado_origem,
        importacao,
        indice_modulos,
    )

    if modulo_interno:
        return "INTERNO", modulo_interno

    modulo_raiz = importacao["modulo"].split(".")[0]

    if modulo_raiz in sys.stdlib_module_names:
        return "BIBLIOTECA PADRÃO", ""

    return "EXTERNO", ""


def gerar_dependencias(
    resultados: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Gera a lista consolidada de dependências do projeto.
    """
    indice_modulos = construir_indice_modulos(resultados)
    dependencias: list[dict[str, Any]] = []

    for resultado in resultados:
        for importacao in resultado["imports"]:
            categoria, modulo_resolvido = classificar_import(
                resultado,
                importacao,
                indice_modulos,
            )

            dependencias.append(
                {
                    "arquivo_origem": resultado["arquivo"],
                    "modulo_origem": resultado["modulo"],
                    "linha": importacao["linha"],
                    "tipo_import": importacao["tipo"],
                    "modulo_importado": importacao["modulo"],
                    "nome_importado": importacao["nome"],
                    "categoria": categoria,
                    "modulo_interno_resolvido": modulo_resolvido,
                }
            )

    return dependencias


def nome_no_mermaid(modulo: str) -> str:
    """
    Converte um nome de módulo em identificador válido no Mermaid.
    """
    return (
        modulo.replace(".", "_")
        .replace("-", "_")
        .replace("/", "_")
    )


def gerar_arvore_diretorios(caminhos: list[Path]) -> list[str]:
    """
    Gera uma árvore visual com conectores ├── e └──.
    """
    arvore: dict[str, Any] = {}

    for caminho in caminhos:
        relativo = caminho.relative_to(RAIZ_PROJETO)
        cursor = arvore

        for parte in relativo.parts:
            cursor = cursor.setdefault(parte, {})

    linhas = [RAIZ_PROJETO.name + "/"]

    def percorrer(no: dict[str, Any], prefixo: str = "") -> None:
        itens = sorted(no.items(), key=lambda item: item[0].lower())

        for indice, (nome, filhos) in enumerate(itens):
            ultimo = indice == len(itens) - 1
            conector = "└── " if ultimo else "├── "
            sufixo = "/" if filhos else ""

            linhas.append(f"{prefixo}{conector}{nome}{sufixo}")

            if filhos:
                novo_prefixo = prefixo + ("    " if ultimo else "│   ")
                percorrer(filhos, novo_prefixo)

    percorrer(arvore)

    return linhas


def gerar_secao_resumo(
    resultados: list[dict[str, Any]],
    dependencias: list[dict[str, Any]],
) -> list[str]:
    """
    Gera a seção de resumo executivo.
    """
    total_linhas = sum(resultado["linhas"] for resultado in resultados)
    total_linhas_codigo = sum(
        resultado["linhas_codigo"]
        for resultado in resultados
    )
    total_funcoes = sum(
        len(resultado["funcoes"])
        for resultado in resultados
    )
    total_classes = sum(
        len(resultado["classes"])
        for resultado in resultados
    )
    total_todos = sum(
        len(resultado["todos"])
        for resultado in resultados
    )
    funcoes_sem_docstring = sum(
        1
        for resultado in resultados
        for funcao in resultado["funcoes"]
        if not funcao["docstring"]
    )
    erros = [
        resultado
        for resultado in resultados
        if resultado["erro_sintaxe"]
    ]
    contagem_imports = Counter(
        dependencia["categoria"]
        for dependencia in dependencias
    )

    return [
        "## 1. Resumo executivo",
        "",
        f"- Arquivos Python: **{len(resultados)}**",
        f"- Linhas totais: **{total_linhas}**",
        f"- Linhas efetivas de código: **{total_linhas_codigo}**",
        f"- Funções: **{total_funcoes}**",
        f"- Classes: **{total_classes}**",
        f"- Imports internos: **{contagem_imports['INTERNO']}**",
        f"- Imports externos: **{contagem_imports['EXTERNO']}**",
        f"- Imports da biblioteca padrão: **{contagem_imports['BIBLIOTECA PADRÃO']}**",
        f"- TODOs/FIXMEs em comentários: **{total_todos}**",
        f"- Funções sem docstring: **{funcoes_sem_docstring}**",
        f"- Arquivos com erro de sintaxe: **{len(erros)}**",
        "",
    ]


def gerar_secao_configuracao() -> list[str]:
    """
    Explica como ativar ou desativar as opções booleanas do auditor.
    """
    return [
        "## 2. Como usar as opções True e False",
        "",
        "As variáveis abaixo ficam no início de `project_audit.py`:",
        "",
        "```python",
        f"INCLUIR_CODIGO_FONTE = {INCLUIR_CODIGO_FONTE}",
        (
            "INCLUIR_FERRAMENTAS_AUDITORIA = "
            f"{INCLUIR_FERRAMENTAS_AUDITORIA}"
        ),
        "```",
        "",
        "- `False`: mantém a opção desativada.",
        "- `True`: ativa a opção.",
        "- Para o checkpoint normal, mantenha as duas como `False`.",
        "- Ative `INCLUIR_CODIGO_FONTE` somente quando precisar "
        "enviar todo o código para revisão.",
        "- Ative `INCLUIR_FERRAMENTAS_AUDITORIA` somente quando quiser "
        "auditar também o próprio auditor.",
        "",
    ]


def gerar_secao_pipeline() -> list[str]:
    """
    Gera a visão do pipeline principal.
    """
    linhas = [
        "## 3. Pipeline principal",
        "",
        "```text",
    ]

    for indice, arquivo in enumerate(PIPELINE_PRINCIPAL):
        linhas.append(Path(arquivo).name)

        if indice < len(PIPELINE_PRINCIPAL) - 1:
            linhas.append("↓")

    linhas.extend(["```", ""])

    return linhas



def gerar_secao_entregas() -> list[str]:
    """
    Exibe os principais artefatos entregues pelo projeto.
    """
    linhas = [
        "## 4. Entregas do projeto",
        "",
        "| Entrega | Caminho | Status |",
        "|---|---|:---:|",
    ]

    for nome, caminho_relativo in ARTEFATOS_PROJETO.items():
        caminho = RAIZ_PROJETO / caminho_relativo
        status = "✅" if caminho.exists() else "❌"

        linhas.append(
            f"| {nome} | `{caminho_relativo}` | {status} |"
        )

    linhas.append("")

    return linhas


def gerar_secao_saude(
    resultados: list[dict[str, Any]],
    dependencias: list[dict[str, Any]],
) -> list[str]:
    """
    Gera indicadores objetivos de saúde do projeto.

    As notas são heurísticas simples, não substituem revisão humana.
    """
    total_arquivos = max(len(resultados), 1)
    total_funcoes = max(
        sum(len(resultado["funcoes"]) for resultado in resultados),
        1,
    )
    funcoes_sem_docstring = sum(
        1
        for resultado in resultados
        for funcao in resultado["funcoes"]
        if not funcao["docstring"]
    )
    arquivos_grandes = sum(
        1
        for resultado in resultados
        if resultado["linhas"] > 300
    )
    erros_sintaxe = sum(
        1
        for resultado in resultados
        if resultado["erro_sintaxe"]
    )
    dependencias_internas = sum(
        1
        for dependencia in dependencias
        if dependencia["categoria"] == "INTERNO"
    )

    nota_documentacao = max(
        0.0,
        10.0 - (funcoes_sem_docstring / total_funcoes) * 10,
    )
    nota_complexidade = max(
        0.0,
        10.0 - (arquivos_grandes / total_arquivos) * 10,
    )
    nota_sintaxe = 10.0 if erros_sintaxe == 0 else 5.0
    nota_modularizacao = min(
        10.0,
        7.0 + min(dependencias_internas, 6) * 0.5,
    )
    nota_geral = (
        nota_documentacao
        + nota_complexidade
        + nota_sintaxe
        + nota_modularizacao
    ) / 4

    return [
        "## 5. Project Health",
        "",
        "> Notas heurísticas calculadas automaticamente.",
        "",
        "| Dimensão | Nota |",
        "|---|---:|",
        f"| Modularização | {nota_modularizacao:.1f}/10 |",
        f"| Cobertura de docstrings | {nota_documentacao:.1f}/10 |",
        f"| Complexidade estrutural | {nota_complexidade:.1f}/10 |",
        f"| Integridade sintática | {nota_sintaxe:.1f}/10 |",
        f"| Saúde geral | **{nota_geral:.1f}/10** |",
        "",
    ]


def gerar_secao_estrutura(caminhos: list[Path]) -> list[str]:
    """
    Gera a árvore visual do projeto.
    """
    linhas = [
        "## 6. Estrutura do projeto",
        "",
        "```text",
    ]

    linhas.extend(gerar_arvore_diretorios(caminhos))
    linhas.extend(["```", ""])

    return linhas


def gerar_secao_arquivos(resultados: list[dict[str, Any]]) -> list[str]:
    """
    Gera a tabela dos arquivos Python analisados.
    """
    linhas = [
        "## 7. Arquivos Python",
        "",
        "| Arquivo | Linhas | Funções | Classes | TODOs |",
        "|---|---:|---:|---:|---:|",
    ]

    for resultado in resultados:
        linhas.append(
            f"| `{resultado['arquivo']}` "
            f"| {resultado['linhas']} "
            f"| {len(resultado['funcoes'])} "
            f"| {len(resultado['classes'])} "
            f"| {len(resultado['todos'])} |"
        )

    linhas.append("")

    return linhas


def gerar_secao_funcoes(resultados: list[dict[str, Any]]) -> list[str]:
    """
    Gera a relação de funções, assinaturas e docstrings.
    """
    linhas = [
        "## 8. Funções e classes",
        "",
    ]

    for resultado in resultados:
        linhas.append(f"### `{resultado['arquivo']}`")
        linhas.append("")

        if not resultado["funcoes"] and not resultado["classes"]:
            linhas.append("- Nenhuma função ou classe encontrada.")
            linhas.append("")
            continue

        if resultado["funcoes"]:
            linhas.extend(
                [
                    "| Função | Linhas | Argumentos | Docstring |",
                    "|---|---:|---|---|",
                ]
            )

            for funcao in resultado["funcoes"]:
                argumentos = ", ".join(funcao["argumentos"]) or "—"
                intervalo = (
                    f"{funcao['linha']}–{funcao['linha_final']}"
                )

                linhas.append(
                    f"| `{funcao['nome']}` "
                    f"| {intervalo} "
                    f"| `{argumentos}` "
                    f"| {'SIM' if funcao['docstring'] else 'NÃO'} |"
                )

            linhas.append("")

        if resultado["classes"]:
            linhas.extend(
                [
                    "| Classe | Linhas | Docstring |",
                    "|---|---:|---|",
                ]
            )

            for classe in resultado["classes"]:
                intervalo = (
                    f"{classe['linha']}–{classe['linha_final']}"
                )

                linhas.append(
                    f"| `{classe['nome']}` "
                    f"| {intervalo} "
                    f"| {'SIM' if classe['docstring'] else 'NÃO'} |"
                )

            linhas.append("")

    return linhas


def gerar_secao_dependencias(
    dependencias: list[dict[str, Any]],
) -> list[str]:
    """
    Gera tabelas e grafo Mermaid das dependências.
    """
    internas = [
        dependencia
        for dependencia in dependencias
        if dependencia["categoria"] == "INTERNO"
    ]

    externas = sorted(
        {
            dependencia["modulo_importado"].split(".")[0]
            for dependencia in dependencias
            if dependencia["categoria"] == "EXTERNO"
        }
    )

    arestas: set[tuple[str, str]] = set()

    linhas = [
        "## 9. Dependências",
        "",
        "### Dependências internas",
        "",
        "| Origem | Destino |",
        "|---|---|",
    ]

    for dependencia in internas:
        aresta = (
            dependencia["modulo_origem"],
            dependencia["modulo_interno_resolvido"],
        )

        if aresta in arestas:
            continue

        arestas.add(aresta)

        linhas.append(
            f"| `{aresta[0]}` | `{aresta[1]}` |"
        )

    if not arestas:
        linhas.append("| — | Nenhuma dependência interna encontrada |")

    linhas.extend(
        [
            "",
            "### Dependências externas",
            "",
        ]
    )

    if externas:
        linhas.extend(f"- `{modulo}`" for modulo in externas)
    else:
        linhas.append("- Nenhuma dependência externa encontrada.")

    linhas.extend(
        [
            "",
            "### Grafo de dependências internas",
            "",
            "```mermaid",
            "flowchart LR",
        ]
    )

    if arestas:
        for origem, destino in sorted(arestas):
            origem_id = nome_no_mermaid(origem)
            destino_id = nome_no_mermaid(destino)

            linhas.append(
                f'    {origem_id}["{origem}"] --> '
                f'{destino_id}["{destino}"]'
            )
    else:
        linhas.append(
            '    sem_dependencias["Nenhuma dependência interna encontrada"]'
        )

    linhas.extend(["```", ""])

    return linhas


def gerar_secao_observacoes_repositorio() -> list[str]:
    """
    Identifica pequenos pontos de padronização na estrutura do repositório.
    """
    observacoes: list[str] = []

    readme_maiusculo = RAIZ_PROJETO / "README.MD"
    readme_padrao = RAIZ_PROJETO / "README.md"

    if readme_maiusculo.exists() and not readme_padrao.exists():
        observacoes.append(
            "- Padronização recomendada: renomear `README.MD` para "
            "`README.md`."
        )

    erros_gitkeep = [
        caminho.relative_to(RAIZ_PROJETO).as_posix()
        for caminho in RAIZ_PROJETO.rglob(".gitkkeep")
        if not deve_ignorar(caminho)
    ]

    for caminho in erros_gitkeep:
        observacoes.append(
            f"- Possível erro de digitação: `{caminho}`. "
            "O nome convencional é `.gitkeep`."
        )

    saida_raiz = RAIZ_PROJETO / "output" / "inventory_analysis.csv"
    saida_scripts = (
        RAIZ_PROJETO
        / "scripts"
        / "output"
        / "inventory_analysis.csv"
    )

    if saida_raiz.exists() and saida_scripts.exists():
        observacoes.append(
            "- Saída duplicada detectada em `output/` e "
            "`scripts/output/`. Recomenda-se manter apenas "
            "`output/` na raiz."
        )

    linhas = [
        "## 10. Observações automáticas do repositório",
        "",
    ]

    if observacoes:
        linhas.extend(observacoes)
    else:
        linhas.append("- Nenhuma observação de padronização encontrada.")

    linhas.append("")
    return linhas


def gerar_secao_pendencias(resultados: list[dict[str, Any]]) -> list[str]:
    """
    Gera a seção de TODOs, FIXMEs e erros de sintaxe.
    """
    linhas = [
        "## 11. Pendências e erros",
        "",
        "### TODOs e FIXMEs",
        "",
    ]

    encontrou_pendencia = False

    for resultado in resultados:
        for pendencia in resultado["todos"]:
            encontrou_pendencia = True
            linhas.append(
                f"- `{resultado['arquivo']}` — linha "
                f"{pendencia['linha']}: {pendencia['texto']}"
            )

    if not encontrou_pendencia:
        linhas.append("- Nenhum TODO ou FIXME encontrado em comentários.")

    linhas.extend(
        [
            "",
            "### Erros de sintaxe",
            "",
        ]
    )

    erros = [
        resultado
        for resultado in resultados
        if resultado["erro_sintaxe"]
    ]

    if erros:
        for resultado in erros:
            linhas.append(
                f"- `{resultado['arquivo']}`: "
                f"{resultado['erro_sintaxe']}"
            )
    else:
        linhas.append("- Nenhum erro de sintaxe encontrado.")

    linhas.append("")

    return linhas


def gerar_secao_codigo(resultados: list[dict[str, Any]]) -> list[str]:
    """
    Consolida todo o código Python ao final do relatório.
    """
    linhas = [
        "## 12. Código Python consolidado",
        "",
    ]

    for resultado in resultados:
        linhas.extend(
            [
                "---",
                "",
                f"### `{resultado['arquivo']}`",
                "",
                "```python",
                resultado["codigo"].rstrip(),
                "```",
                "",
            ]
        )

    return linhas


def gerar_relatorio_unico(
    resultados: list[dict[str, Any]],
    dependencias: list[dict[str, Any]],
    estrutura: list[Path],
) -> None:
    """
    Gera o arquivo único PROJECT_AUDIT.md.
    """
    linhas = [
        "# Project Audit",
        "",
        f"Gerado em: {datetime.now():%d/%m/%Y %H:%M:%S}",
        "",
        "> Este arquivo é gerado automaticamente. "
        "Não edite manualmente.",
        "",
    ]

    linhas.extend(gerar_secao_resumo(resultados, dependencias))
    linhas.extend(gerar_secao_configuracao())
    linhas.extend(gerar_secao_pipeline())
    linhas.extend(gerar_secao_entregas())
    linhas.extend(gerar_secao_saude(resultados, dependencias))
    linhas.extend(gerar_secao_estrutura(estrutura))
    linhas.extend(gerar_secao_arquivos(resultados))
    linhas.extend(gerar_secao_funcoes(resultados))
    linhas.extend(gerar_secao_dependencias(dependencias))
    linhas.extend(gerar_secao_observacoes_repositorio())
    linhas.extend(gerar_secao_pendencias(resultados))

    if INCLUIR_CODIGO_FONTE:
        linhas.extend(gerar_secao_codigo(resultados))

    ARQUIVO_SAIDA.write_text(
        "\n".join(linhas),
        encoding="utf-8",
    )


def main() -> None:
    """
    Executa a auditoria técnica e gera um único arquivo Markdown.
    """
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    arquivos = localizar_arquivos_python()
    resultados = [
        analisar_arquivo(arquivo)
        for arquivo in arquivos
    ]

    dependencias = gerar_dependencias(resultados)
    estrutura = localizar_estrutura_projeto()

    gerar_relatorio_unico(
        resultados,
        dependencias,
        estrutura,
    )

    print("\nAuditoria concluída com sucesso.")
    print(f"Arquivos Python analisados: {len(resultados)}")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    print(
        "Código-fonte consolidado: "
        f"{'ATIVADO' if INCLUIR_CODIGO_FONTE else 'DESATIVADO'}"
    )
    print(
        "Ferramentas de auditoria nas métricas: "
        f"{'ATIVADO' if INCLUIR_FERRAMENTAS_AUDITORIA else 'DESATIVADO'}"
    )


if __name__ == "__main__":
    main()
