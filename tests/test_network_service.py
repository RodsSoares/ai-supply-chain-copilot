"""Testes da v2.5 — emissões e capacidades da rede expostas ao Copilot."""

import json

import pytest

from src.analytics.network import emissions as em
from src.analytics.network import planning as p
from src.analytics.network import service


@pytest.fixture(scope="module", autouse=True)
def dados_injetados(dados_rede):
    service.configurar_dados(dados_rede)
    yield
    service.configurar_dados(None)


@pytest.fixture(scope="module")
def plano(dados_rede):
    return p.planejar_cenario(dados_rede, "BUDGET_2027")


def test_emissao_rodoviaria_calculada_a_mao(dados_rede, plano):
    e = em.emissoes_plano(dados_rede, plano)
    linha = e[(e["mode"] == "ROAD") & (e["total_trips"] > 0)].iloc[0]
    kmpl = dados_rede.veiculos.loc[linha["vehicle_type_id"], "km_per_liter"]
    esperado = 2 * linha["distance_km"] * linha["total_trips"] / kmpl * 2.60
    assert linha["kg_co2e"] == pytest.approx(esperado)


def test_emissao_aerea_calculada_a_mao(dados_rede, plano):
    e = em.emissoes_plano(dados_rede, plano)
    linha = e[e["mode"] == "AIR"].iloc[0]
    assert linha["kg_co2e"] == pytest.approx(linha["volume"] * 0.25 / 1000 * linha["distance_km"] * 0.60)


def test_mais_viagens_mais_emissoes(dados_rede, plano):
    alt = p.planejar_cenario(dados_rede, "BUDGET_2027", [{"parameter_key": "frequency_basis", "value": "MAX"}])
    assert em.total_emissoes(em.emissoes_plano(dados_rede, alt))["t_co2e"] > em.total_emissoes(em.emissoes_plano(dados_rede, plano))["t_co2e"]


@pytest.mark.parametrize("nome, parametros", [
    ("plan_route_week", {}),
    ("analyze_overflow", {}),
    ("find_consolidation_candidates", {}),
    ("run_what_if", {"overrides": [{"parameter_key": "volume_multiplier", "value": 1.1}]}),
    ("analyze_dc_load", {}),
    ("forecast_accuracy", {"level": "STORE"}),
    ("forecast_value_added", {}),
    ("demand_variability", {}),
    ("budget_summary", {}),
    ("budget_bridge", {}),
    ("adjustment_report", {}),
    ("new_store_cost_estimate", {"uf": "SP", "weekly_pieces": 3000}),
    ("plan_vs_actual", {}),
    ("extras_analysis", {}),
    ("carrier_performance", {}),
    ("emissions_summary", {}),
])
def test_capacidades_retornam_json(nome, parametros):
    resultado = service.executar_capacidade(nome, **parametros)
    assert resultado["capability"] == nome
    json.dumps(resultado, allow_nan=False)  # serializável e sem NaN


def test_capacidade_nao_autorizada():
    with pytest.raises(ValueError):
        service.executar_capacidade("delete_everything")


def test_what_if_exige_override():
    with pytest.raises(ValueError):
        service.executar_capacidade("run_what_if")


def test_filtro_por_rota(dados_rede):
    rota = dados_rede["tn_routes"]["route_id"].iloc[0]
    r = service.executar_capacidade("plan_route_week", route_id=rota)
    assert {x["route_id"] for x in r["routes"]} == {rota}


def test_ajuste_pendente_aparece_mas_nao_aplica():
    r = service.executar_capacidade("adjustment_report")
    pendentes = [a for a in r["adjustments"] if a["status"] == "PROPOSED"]
    assert pendentes and all(not a["applied"] and a["impact_brl"] == 0 for a in pendentes)
