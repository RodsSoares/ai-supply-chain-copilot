"""
Validações estáticas do kit Power BI HUD V6 (reports/powerbi/kit).

Não abrem o Power BI: conferem que o que o guia de montagem manda fazer
é consistente com os arquivos do kit (dados, DAX, Deneb e layout) e que
os números do checklist batem com os CSVs exportados.
"""

import json
import re
from pathlib import Path

import pandas as pd
import pytest


KIT = Path(__file__).resolve().parents[1] / "reports" / "powerbi" / "kit"
GUIA = (KIT / "GUIA_MONTAGEM.md").read_text(encoding="utf-8")
DAX = re.sub(r"//[^\n]*", "", (KIT / "dax" / "medidas.dax").read_text(encoding="utf-8"))
SPECS_DENEB = sorted((KIT / "deneb").glob("*.json"))


def ler_csv(nome: str) -> pd.DataFrame:
    return pd.read_csv(KIT / "data" / nome, sep=";", decimal=",", encoding="utf-8-sig")


TABELAS = {caminho.stem: ler_csv(caminho.name) for caminho in (KIT / "data").glob("*.csv")}
NOMES_MEDIDAS = [
    nome for nome in re.findall(r"^((?:% )?[A-Za-z][A-Za-z0-9 ]*?) =", DAX, re.M) if not nome.startswith("VAR ")
]
MEDIDAS = set(NOMES_MEDIDAS)
COLUNAS = {coluna for tabela in TABELAS.values() for coluna in tabela.columns}


def linhas_do_guia(secao: str) -> list[tuple[str, str, list[int], str]]:
    """Linhas `| painel | visual | X | Y | L | A | campos |` de uma seção do guia."""
    inicio = GUIA.index(secao)
    fim = GUIA.find("\n## ", inicio + 1)
    fim_sub = GUIA.find("\n### ", inicio + len(secao))
    limites = [f for f in (fim, fim_sub) if f != -1]
    trecho = GUIA[inicio : min(limites) if limites else len(GUIA)]
    padrao = r"^\| `(\w+)` \| ([^|]+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| ([^\n]+) \|$"
    return [
        (painel, visual.strip(), [int(x), int(y), int(w), int(h)], campos)
        for painel, visual, x, y, w, h, campos in re.findall(padrao, trecho, re.M)
    ]


PAGINAS = {
    "command_center": "## 3. Montagem",
    "inventory": "### 4.1",
    "transportation": "### 4.2",
}


@pytest.mark.parametrize("caminho", SPECS_DENEB + [KIT / "theme" / "ai_supply_chain_hud_v6.json", KIT / "backgrounds" / "layout.json"], ids=lambda p: p.name)
def test_json_valido(caminho):
    json.loads(caminho.read_text(encoding="utf-8"))


def test_dax_usa_apenas_colunas_existentes():
    referencias = set(re.findall(r"\b([a-z_]+)\[([a-z_]+)\]", DAX))
    faltando = {f"{t}[{c}]" for t, c in referencias if t not in TABELAS or c not in TABELAS[t].columns}
    assert not faltando


def test_dax_referencia_apenas_medidas_definidas():
    referencias = set(re.findall(r"(?<![a-z_])\[([^\]]+)\]", DAX))
    assert not {r for r in referencias if r not in MEDIDAS and r not in COLUNAS}


def test_dax_sem_medidas_duplicadas():
    assert len(NOMES_MEDIDAS) == len(MEDIDAS)


@pytest.mark.parametrize("caminho", SPECS_DENEB, ids=lambda p: p.name)
def test_deneb_le_dataset_e_documenta_campos(caminho):
    spec = json.loads(caminho.read_text(encoding="utf-8"))
    assert spec["data"] == {"name": "dataset"}
    assert caminho.name in GUIA, "spec Deneb sem instrução no guia"


@pytest.mark.parametrize("pagina", PAGINAS)
def test_visuais_do_guia_seguem_o_layout(pagina):
    layout = {p["id"]: p for p in json.loads((KIT / "backgrounds" / "layout.json").read_text(encoding="utf-8"))[pagina]}
    linhas = linhas_do_guia(PAGINAS[pagina])

    assert {painel for painel, *_ in linhas} == set(layout), "guia e layout.json com painéis diferentes"

    for painel, _, (x, y, w, h), _ in linhas:
        p = layout[painel]
        if painel.startswith("kpi_"):
            esperado = [p["x"] + 4, p["y"] + 4, p["largura"] - 8, p["altura"] - 8]
        else:
            esperado = [p["x"] + 12, p["y"] + 44, p["largura"] - 24, p["altura"] - 56]
        assert [x, y, w, h] == esperado, painel


@pytest.mark.parametrize("pagina", PAGINAS)
def test_campos_do_guia_existem(pagina):
    for painel, _, _, campos in linhas_do_guia(PAGINAS[pagina]):
        for nome in re.findall(r"`([^`]+)`", campos):
            if nome.endswith(".json"):
                continue
            assert nome in MEDIDAS or nome in COLUNAS, f"{painel}: campo {nome!r} não existe"


@pytest.mark.parametrize(
    ("relacao", "dimensao"),
    [
        (("fato_viagens", "rota"), "dim_rotas"),
        (("fato_viagens", "semana_inicio"), "dim_semana"),
        (("fato_viagens", "veiculo"), "dim_veiculos"),
        (("fato_demanda", "rota"), "dim_rotas"),
        (("fato_demanda", "semana_inicio"), "dim_semana"),
    ],
)
def test_relacionamentos_sem_orfaos(relacao, dimensao):
    fato, coluna = relacao
    assert TABELAS[dimensao][coluna].is_unique
    assert set(TABELAS[fato][coluna]) <= set(TABELAS[dimensao][coluna])


def test_kpis_do_checklist_batem_com_os_dados():
    e = TABELAS["fato_estoque"]
    v = TABELAS["fato_viagens"].merge(TABELAS["dim_rotas"], on="rota")
    semana = TABELAS["dim_semana"].sort_values("semana_ordem").semana_inicio.iloc[-1]
    ultima = v[v.semana_inicio == semana]

    # Command Center
    assert round(e.valor_estoque.sum() / 1e6, 2) == 34.59
    assert round(e.valor_reposicao.sum() / 1e6, 2) == 3.28
    assert round(e.valor_excesso.sum() / 1e6, 2) == 11.65
    assert round(e.valor_acao.sum() / 1e6, 2) == 14.93
    assert round(ultima.custo_planejado.sum() / 1e3, 1) == 99.6
    assert round(ultima.pecas_planejadas.sum() / ultima.capacidade_planejada.sum() * 100, 1) == 76.6
    custo_rota = v.groupby("rota").custo_planejado.sum()
    assert set(custo_rota.nlargest(2).index) == {"R011", "R012"}

    # Inventory
    cobertura = e.valor_estoque.sum() / (e.consumo_medio_mensal * e.custo_unitario).sum()
    assert round(cobertura, 1) == 2.1
    assert round(e.cobertura_meses.median(), 1) == 1.8
    assert round(e[e.classe_abc == "A"].valor_estoque.sum() / e.valor_estoque.sum() * 100) == 69
    assert round((e.risco_ruptura == "SIM").mean() * 100) == 19
    assert round(e[e.deposito == "CD Campinas"].valor_acao.sum() / 1e6, 2) == 5.92
    acumulado = e.valor_estoque.sort_values(ascending=False).cumsum() / e.valor_estoque.sum()
    assert int((acumulado < 0.8).sum()) + 1 == 73  # rótulo da curva de Pareto

    # Transportation
    assert len(v) == 192 and v.semana_inicio.nunique() == 8
    assert round(v.pecas_planejadas.sum() / 1e6, 2) == 2.00
    assert v.pecas_planejadas.sum() == TABELAS["fato_demanda"].pecas_previstas.sum()
    assert round(v.custo_planejado.sum() / v.pecas_planejadas.sum(), 2) == 0.39
    assert round(v.custo_planejado.sum() / v.distancia_km.sum(), 2) == 5.29
    assert v.distancia_km.sum() == 147_200
