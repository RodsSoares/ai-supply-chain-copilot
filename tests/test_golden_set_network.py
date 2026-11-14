"""Proteção contra drift do Golden Set v2 e coerência com o contrato do roteador."""

import json
import math
from pathlib import Path
from typing import get_args

import pytest

from src.evaluation import golden_network as g


GOLDEN = json.loads(Path("tests/golden/network_golden_set.json").read_text(encoding="utf-8"))


def _iguais(a, b):
    if isinstance(a, (int, float)) and not isinstance(a, bool):
        return math.isclose(float(a), float(b), rel_tol=1e-6, abs_tol=1e-6)
    return a == b


def test_arquivo_sincronizado_com_definicoes():
    assert [c["id"] for c in GOLDEN["cases"]] == [c["id"] for c in g.CASOS]
    for salvo, definido in zip(GOLDEN["cases"], g.CASOS):
        assert salvo["question"] == definido["question"]
        assert salvo["facts"] == definido["facts"]


@pytest.mark.parametrize("caso", GOLDEN["cases"], ids=lambda c: c["id"])
def test_motor_reproduz_fatos_esperados(caso):
    obtidos = g.calcular_fatos(caso)
    for nome, esperado in caso["expected_facts"].items():
        assert _iguais(esperado, obtidos[nome]), f"{caso['id']}.{nome}: {esperado} != {obtidos[nome]}"


def test_intencoes_e_campos_existem_no_contrato():
    rota = pytest.importorskip("src.ai.transportation_router")  # requer openai instalado
    intents = set(get_args(rota.TransportationIntentName))
    campos = set(rota.TransportationIntent.model_fields)
    for caso in GOLDEN["cases"]:
        assert set(caso["expected_intent"]) <= intents, caso["id"]
        assert set(caso["expected_fields"]) <= campos, caso["id"]


def test_extrator_de_caminhos():
    r = {"a": {"b": 1}, "l": [{"k": "x", "v": 2}, {"k": "y", "v": 3}]}
    assert g.extrair(r, "a.b") == 1
    assert g.extrair(r, "l[k=y].v") == 3
    assert g.extrair(r, "len(l)") == 2
    with pytest.raises(KeyError):
        g.extrair(r, "l[k=z].v")


@pytest.mark.parametrize("texto, valor, esperado", [
    ("O orçamento final é R$ 13.641.070.", 13641069.5455, True),
    ("Final budget of R$ 13,641,070", 13641069.5455, True),
    ("cerca de R$ 13,6 milhões", 13641069.5455, True),
    ("viés de 3,1%", 0.031, True),
    ("o custo foi R$ 12 milhões", 13641069.5455, False),
    ("viés de 3,1% e WAPE de 12%", 0.089, False),        # não casa '0' nem '1'
    ("on-time de 86,6% (meta 95%)", 0.8655, True),        # arredondamento para 1 casa
    ("on-time de 87% (meta 95%)", 0.8655, False),         # 0 casas não é aceito para percentuais
    ("total de 113.641.070 peças", 13641069.5455, False),  # fronteira numérica
    ("nenhuma viagem", 0, True),                           # inteiro pequeno: qualitativo
])
def test_fidelidade_numerica(texto, valor, esperado):
    assert g.fato_presente(texto, valor) is esperado


def test_markdown_sincronizado_com_json():
    esperado = g.escrever_markdown(GOLDEN)
    assert Path("tests/golden_test_set_network.md").read_text(encoding="utf-8") == esperado
