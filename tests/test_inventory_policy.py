"""Testes da v2.6 — política dinâmica de estoque (estoque de segurança e ponto de pedido)."""

import json
import math

import pandas as pd
import pytest

from src.analytics.inventory_policy import safety_stock as ss
from src.analytics.inventory_policy import service
from src.synthetic.inventory_demand_generator import carregar_config, carregar_erp, gerar_demanda_semanal


@pytest.fixture(scope="module")
def entradas():
    config = carregar_config()
    erp = carregar_erp()
    return erp, gerar_demanda_semanal(erp, config), config


@pytest.fixture(scope="module")
def politica(entradas):
    erp, demanda, config = entradas
    return ss.calcular_politica(erp, demanda, config)


def test_z_de_servico():
    assert ss.z_servico(0.95) == pytest.approx(1.6449, abs=1e-4)
    assert ss.z_servico(0.5) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        ss.z_servico(1.0)


def test_formula_estoque_seguranca():
    # sem variabilidade de lead time: z × σd × √LT
    assert ss.estoque_seguranca(1.65, 100, 20, 4, 0) == pytest.approx(1.65 * 20 * 2)
    com_lt = ss.estoque_seguranca(1.65, 100, 20, 4, 1)
    assert com_lt == pytest.approx(1.65 * math.sqrt(4 * 400 + 100 ** 2 * 1))


def test_gerador_reprodutivel_e_calibrado(entradas):
    erp, demanda, config = entradas
    assert demanda.equals(gerar_demanda_semanal(erp, config))
    media = demanda.groupby("sku")["demand_units"].mean() * config["weeks_per_month"]
    razao = media / erp.set_index("sku")["consumo_medio_mensal"]
    assert razao.mean() == pytest.approx(1.0, abs=0.03)
    zeros = demanda.merge(erp[["sku", "classe_abc"]], on="sku").groupby("classe_abc")["demand_units"].apply(lambda s: (s == 0).mean())
    assert zeros["C"] > zeros["B"] > zeros["A"]


def test_politica_consistente(politica):
    assert (politica["safety_stock"] >= 0).all()
    assert (politica["reorder_point"] >= politica["safety_stock"]).all()
    assert (politica["order_up_to"] >= politica["reorder_point"]).all()
    assert set(politica["dynamic_action"]) <= set(ss.ACOES)


def test_politica_estatica_preservada(politica):
    erp = carregar_erp()
    esperado = ss.acao_estatica(erp["estoque_atual"], erp["estoque_minimo"], erp["estoque_maximo"])
    assert politica["static_action"].tolist() == esperado.tolist()
    analise = pd.read_csv("output/inventory_analysis.csv", sep=";", encoding="utf-8-sig")
    assert politica["static_action"].tolist() == analise["acao_recomendada"].tolist()


def test_nivel_servico_maior_exige_mais_estoque(entradas):
    curva = ss.curva_servico_capital(*entradas)
    assert curva["safety_stock_value"].is_monotonic_increasing


def test_classe_a_tem_servico_maior(politica):
    niveis = politica.groupby("classe_abc")["service_level"].first()
    assert niveis["A"] > niveis["B"] > niveis["C"]


def test_cobertura_historica_atinge_meta(politica, entradas):
    _, demanda, _ = entradas
    cob = ss.cobertura_historica(politica, demanda).groupby("classe_abc")[["service_level", "empirical_cycle_service_level"]].mean()
    assert (cob["empirical_cycle_service_level"] >= cob["service_level"] - 0.02).all()


def test_comparacao_fecha(politica):
    c = ss.comparar_politicas(politica)
    total = sum(sum(linha.values()) for linha in c["transition_matrix"].values())
    assert total == c["skus"] == 300
    mudou = c["skus"] - sum(c["transition_matrix"][a][a] for a in ss.ACOES)
    assert mudou == c["actions_changed"]


def test_sku_sem_historico(entradas):
    erp, demanda, config = entradas
    with pytest.raises(ValueError):
        ss.calcular_politica(erp, demanda[demanda["sku"] != erp["sku"].iloc[0]], config)


@pytest.mark.parametrize("nome, parametros", [
    ("safety_stock", {"sku": "SKU-2001"}),
    ("reorder_alerts", {}),
    ("policy_comparison", {}),
    ("service_capital_curve", {}),
])
def test_capacidades_json(nome, parametros):
    r = service.executar_capacidade(nome, **parametros)
    assert r["capability"] == nome
    json.dumps(r, allow_nan=False, default=str)


def test_capacidade_nao_autorizada():
    with pytest.raises(ValueError):
        service.executar_capacidade("drop_table")
