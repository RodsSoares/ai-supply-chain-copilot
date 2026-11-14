"""Testes do gerador do Power BI Project (scripts/build_powerbi_pbip.py)."""

import importlib.util
import json
import re
from pathlib import Path

import pytest


RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("build_powerbi_pbip", RAIZ / "scripts" / "build_powerbi_pbip.py")
gerador = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gerador)


@pytest.fixture(scope="module")
def modelo(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("pbip") / "Modelo.SemanticModel"
    gerador.gerar_modelo(pasta)
    return pasta / "definition"


def test_todas_as_medidas_do_dax_viram_medidas_tmdl(modelo):
    tmdl = (modelo / "tables" / "_Medidas.tmdl").read_text(encoding="utf-8")
    medidas = gerador.ler_medidas()
    assert len(medidas) >= 50
    for nome, _ in medidas:
        assert f"\tmeasure {gerador.nome_tmdl(nome)} =" in tmdl, nome


def test_expressoes_preservadas_sem_comentarios_soltos(modelo):
    medidas = dict(gerador.ler_medidas())
    assert medidas["Valor Estoque"] == "SUM ( fato_estoque[valor_estoque] )"
    assert medidas["Rank Custo Rota"].strip() == "RANKX ( ALL ( dim_rotas[rota] ), [Custo Planejado],, DESC )"
    # comentário que antecede a próxima medida não pode grudar na anterior
    assert not medidas["Rank Custo Rota"].rstrip().endswith("(Deneb)")
    assert medidas["HTML KPI Custo Unitario"].rstrip().endswith('km planejados</span></div></div>"')


def test_uma_tabela_por_csv_com_colunas_do_arquivo(modelo):
    for tabela in gerador.TABELAS:
        tmdl = (modelo / "tables" / f"{tabela}.tmdl").read_text(encoding="utf-8")
        colunas = re.findall(r"^\tcolumn (\S+)$", tmdl, re.M)
        assert colunas == [c for c, _ in gerador.tipos_das_colunas(tabela)]
        assert f'PastaDados & "{tabela}.csv"' in tmdl


def test_tipos_das_colunas():
    tipos = dict(gerador.tipos_das_colunas("fato_viagens"))
    assert tipos == {
        "viagem": "string",
        "semana_inicio": "dateTime",
        "rota": "string",
        "veiculo": "string",
        "pecas_planejadas": "int64",
        "capacidade_planejada": "int64",
        "custo_planejado": "double",
    }


def test_relacionamentos_do_guia(modelo):
    tmdl = (modelo / "relationships.tmdl").read_text(encoding="utf-8")
    pares = re.findall(r"fromColumn: (\S+)\n\ttoColumn: (\S+)", tmdl)
    assert pares == [(f"{f}.{cf}", f"{d}.{cd}") for f, cf, d, cd in gerador.RELACIONAMENTOS]


def test_formatos_das_medidas():
    assert gerador.formato_medida("Valor Estoque") == "\\R$ #,0"
    assert gerador.formato_medida("Custo Planejado") == "\\R$ #,0"
    assert gerador.formato_medida("Custo por Peca") == "\\R$ #,0.00"
    assert gerador.formato_medida("Custo Mil") == "#,0.0"
    assert gerador.formato_medida("Utilizacao") == "0.0%"
    assert gerador.formato_medida("% Excesso") == "0.0%"
    assert gerador.formato_medida("HTML KPI Estoque") is None
    assert gerador.formato_medida("Viagens") == "#,0"


def test_lineage_tags_estaveis(modelo, tmp_path):
    gerador.gerar_modelo(tmp_path / "Outro.SemanticModel")
    for arquivo in modelo.rglob("*.tmdl"):
        outro = tmp_path / "Outro.SemanticModel" / "definition" / arquivo.relative_to(modelo)
        assert arquivo.read_text(encoding="utf-8") == outro.read_text(encoding="utf-8"), arquivo.name


def test_relatorio_com_tres_paginas_full_hd(tmp_path):
    gerador.gerar_relatorio(tmp_path)
    relatorio = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    paginas = [(s["displayName"], s["width"], s["height"]) for s in relatorio["sections"]]
    assert paginas == [("Command Center", 1920, 1080), ("Inventory", 1920, 1080), ("Transportation", 1920, 1080)]
    pbir = json.loads((tmp_path / "definition.pbir").read_text(encoding="utf-8"))
    assert pbir["datasetReference"]["byPath"]["path"] == f"../{gerador.NOME}.SemanticModel"
