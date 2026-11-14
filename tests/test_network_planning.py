"""Testes da v2.3 — política de frequência, transbordo e what-if."""

import pandas as pd
import pytest

from src.analytics.network import planning as p
from src.decision.network import planning_policy as pol
from src.decision.network.parameters import ParametrosCenario


# -- Política ---------------------------------------------------------------

def test_viagens_necessarias():
    assert pol.viagens_necessarias(0, 100) == 0
    assert pol.viagens_necessarias(100, 100) == 1
    assert pol.viagens_necessarias(101, 100) == 2
    with pytest.raises(ValueError):
        pol.viagens_necessarias(10, 0)


@pytest.mark.parametrize(
    "necessidades, base, minima, esperado",
    [
        ([2, 3], "MEAN", 1, 3),          # 2.5 arredonda para cima (não bancário)
        ([2, 2, 2, 3], "MEAN", 1, 2),
        ([2, 2, 2, 3], "MAX", 1, 3),
        ([1, 2, 3, 4], "P75", 1, 3),     # q75 = 3.25
        ([1, 1, 1, 1], "MEAN", 3, 3),    # frequência mínima
        ([0, 0, 0, 0], "MEAN", 3, 0),    # sem demanda => sem frequência
    ],
)
def test_frequencia_mensal(necessidades, base, minima, esperado):
    assert pol.frequencia_mensal(necessidades, base, minima) == esperado


def test_base_invalida():
    with pytest.raises(ValueError):
        pol.frequencia_mensal([1], "P99", 1)


def test_transbordo_tem_custo_spot():
    plano = pol.planejar_semana(volume=25000, capacidade=6000, frequencia=3, tarifa=1000, premio_spot=1.35)
    assert plano["required_trips"] == 5 and plano["overflow_trips"] == 2
    assert plano["transport_cost"] == pytest.approx(3 * 1000 + 2 * 1000 * 1.35)
    assert plano["utilization"] == pytest.approx(25000 / 30000)


# -- Parâmetros -------------------------------------------------------------

@pytest.fixture
def params():
    linhas = pd.DataFrame([
        {"scenario_id": "S", "parameter_key": "frequency_min.SHORT", "scope": "NETWORK", "value": "3", "valid_from": "2027-01-01", "valid_to": None, "source_note": ""},
        {"scenario_id": "S", "parameter_key": "rate_adjustment", "scope": "CARRIER:ATLAS", "value": "0.06", "valid_from": "2027-03-01", "valid_to": None, "source_note": ""},
        {"scenario_id": "S", "parameter_key": "rate_adjustment", "scope": "CARRIER:ATLAS", "value": "0.02", "valid_from": "2027-09-01", "valid_to": None, "source_note": ""},
    ])
    return linhas


def test_precedencia_de_escopo_e_override(params):
    pc = ParametrosCenario("S", params, [{"parameter_key": "frequency_min", "scope": "ROUTE:R1", "value": 1}])
    assert pc.frequencia_minima("SHORT") == 3
    assert pc.frequencia_minima("SHORT", route_id="R1") == 1
    pc2 = ParametrosCenario("S", params, [{"parameter_key": "frequency_min.SHORT", "value": 2}])
    assert pc2.frequencia_minima("SHORT") == 2


def test_reajustes_acumulam_por_vigencia(params):
    pc = ParametrosCenario("S", params)
    assert pc.fator_reajuste("ATLAS", "2027-02-01") == 1.0
    assert pc.fator_reajuste("ATLAS", "2027-03-01") == pytest.approx(1.06)
    assert pc.fator_reajuste("ATLAS", "2027-12-01") == pytest.approx(1.06 * 1.02)
    assert pc.fator_reajuste("NOVA", "2027-12-01") == 1.0


# -- Motor ------------------------------------------------------------------

@pytest.fixture(scope="module")
def plano_2027(dados_rede):
    return p.planejar_cenario(dados_rede, "BUDGET_2027")


def test_plano_conserva_volume(dados_rede, plano_2027):
    fc = dados_rede["tn_forecast"]
    fc = fc[(fc["forecast_version"] == "BUDGET_2027") & fc["week_start"].str.startswith("2027")]
    assert plano_2027["volume"].sum() == pytest.approx(fc["forecast_pieces"].sum())


def test_semanas_por_tipo_de_rota(dados_rede, plano_2027):
    semanas = plano_2027.groupby(["route_id", "route_type"])["week_start"].nunique().reset_index()
    padrao = semanas[semanas["route_type"].isin(["STANDARD", "TWO_DRIVERS", "AIR"])]
    assert (padrao["week_start"] == 52).all()
    alternadas = semanas[semanas["route_type"] == "ALTERNATING_WEEK"]
    assert (alternadas["week_start"] <= 27).all()


def test_nenhum_transbordo_oculto(plano_2027):
    rod = plano_2027[plano_2027["route_type"] != "AIR"]
    assert (rod["planned_capacity"] >= rod["volume"]).all()
    assert (rod.loc[rod["overflow_trips"] > 0, "overflow_cost"] > 0).all()


def test_explicacao_estruturada(plano_2027):
    import json
    exp = json.loads(plano_2027.iloc[0]["explanation_json"])
    assert {"frequency_basis", "frequency_min", "vehicle_type_id", "reasons"} <= exp.keys()


def test_reajuste_do_cenario_aplicado(dados_rede, plano_2027):
    rota = dados_rede["tn_routes"].query("carrier_id == 'ATLAS' and route_type == 'STANDARD'")["route_id"].iloc[0]
    r = plano_2027[plano_2027["route_id"] == rota].set_index("week_start")["rate"]
    assert r["2027-03-01"] / r["2027-02-22"] == pytest.approx(1.06)


def test_rota_sem_demanda_nao_gera_viagens(plano_2027):
    for rota in p.rotas_sem_demanda(plano_2027):
        assert plano_2027.loc[plano_2027["route_id"] == rota, "total_trips"].sum() == 0


def test_what_if_nao_altera_base(dados_rede, plano_2027):
    resultado = p.rodar_what_if(dados_rede, "BUDGET_2027", [{"parameter_key": "frequency_basis", "value": "MAX"}])
    assert resultado["what_if"]["overflow_trips"] == 0
    assert resultado["delta"]["volume"] == 0
    novamente = p.planejar_cenario(dados_rede, "BUDGET_2027")
    pd.testing.assert_frame_equal(novamente, plano_2027)


def test_choque_de_volume_respeita_janela(dados_rede, plano_2027):
    alt = p.planejar_cenario(dados_rede, "BUDGET_2027", [
        {"parameter_key": "volume_multiplier", "value": 1.10, "valid_from": "2027-10-04", "valid_to": "2027-12-31"}])
    padrao = ~alt["route_type"].eq("ALTERNATING_WEEK")
    antes = alt[padrao & (alt["week_start"] < "2027-10-04")]["volume"].sum()
    assert antes == pytest.approx(plano_2027[padrao & (plano_2027["week_start"] < "2027-10-04")]["volume"].sum())
    depois = alt[padrao & (alt["week_start"] >= "2027-10-04")]["volume"].sum()
    base = plano_2027[padrao & (plano_2027["week_start"] >= "2027-10-04")]["volume"].sum()
    assert depois == pytest.approx(base * 1.10)


def test_veiculo_nao_elegivel(dados_rede):
    rota = dados_rede["tn_routes"].query("route_profile == 'SHORT'")["route_id"].iloc[0]
    with pytest.raises(ValueError):
        p.planejar_cenario(dados_rede, "BUDGET_2027", [{"parameter_key": "vehicle", "scope": f"ROUTE:{rota}", "value": "NV05"}], rotas=[rota])


def test_candidatos_consolidacao(dados_rede, plano_2027):
    c = p.candidatos_consolidacao(dados_rede, "BUDGET_2027", plano_2027)
    assert not c.empty
    assert (c["current_utilization"] < c["utilization_threshold"]).all()
    assert (c["annual_saving"] >= 0).all()


def test_carga_cd(dados_rede, plano_2027):
    carga = p.carga_cds(dados_rede, plano_2027)
    assert set(carga["dc_id"]) == {"DC01", "DC02", "DC03"}
    assert (carga["load_factor"] > 0).all()
