"""Testes da v2.4 — orçamento, ajustes gerenciais, ponte e plano vs. realizado."""

import pytest

from src.analytics.network import budget as b
from src.analytics.network import planning as p
from src.analytics.network import variance as v


@pytest.fixture(scope="module")
def planos(dados_rede):
    return p.planejar_cenario(dados_rede, "PLAN_2026"), p.planejar_cenario(dados_rede, "BUDGET_2027")


@pytest.fixture(scope="module")
def orcamentos(dados_rede, planos):
    p26, p27 = planos
    return b.orcamento(dados_rede, "PLAN_2026", p26), b.orcamento(dados_rede, "BUDGET_2027", p27)


def test_decomposicao_soma_exata():
    e = b.decompor(1000, 10, 5000, 1200, 11, 6300)
    assert sum(e.values()) == pytest.approx(6300 - 5000)
    assert e["volume_effect"] == pytest.approx(200 * 0.01 * 500)


def test_decomposicao_entrada_de_rota():
    e = b.decompor(0, 0, 0, 100, 2, 900)
    assert e == {"volume_effect": 900, "efficiency_effect": 0.0, "rate_effect": 0.0}


def test_linhas_reconciliam_com_plano(planos, orcamentos):
    _, p27 = planos
    _, l27 = orcamentos
    modelo = l27[l27["source"] == "MODEL"]
    frete = modelo.loc[modelo["cost_component"].isin(["FREIGHT", "OVERFLOW"]), "amount_brl"].sum()
    assert frete == pytest.approx(p27["transport_cost"].sum())
    assert modelo["volume"].sum() == pytest.approx(p27["volume"].sum())


def test_componentes_seguem_parametros(orcamentos):
    _, l27 = orcamentos
    c = b.totais(l27)["by_component"]
    assert c["EXTRAS"] == pytest.approx(0.04 * (c["FREIGHT"] + c["OVERFLOW"]))
    assert c["TAX_CREDIT"] == pytest.approx(-0.0925 * (c["FREIGHT"] + c["OVERFLOW"] + c["EXTRAS"]))


def test_somente_ajustes_aprovados(dados_rede, orcamentos):
    _, l27 = orcamentos
    fontes = set(l27["source"])
    assert "ADJUSTMENT:ADJ-2027-001" in fontes and "ADJUSTMENT:ADJ-2027-002" in fontes
    assert "ADJUSTMENT:ADJ-2027-003" not in fontes  # PROPOSED


def test_valores_dos_ajustes(dados_rede, orcamentos):
    _, l27 = orcamentos
    modelo = l27.loc[l27["source"] == "MODEL", "amount_brl"].sum()
    impacto = l27.groupby("source")["amount_brl"].sum()
    assert impacto["ADJUSTMENT:ADJ-2027-001"] == pytest.approx(-0.03 * modelo)
    assert impacto["ADJUSTMENT:ADJ-2027-002"] == pytest.approx(180000)
    dc03 = l27[(l27["source"] == "ADJUSTMENT:ADJ-2027-002")]
    assert set(dc03["dc_id"]) == {"DC03"}


def test_sem_ajustes_final_igual_modelo(dados_rede, planos):
    _, p27 = planos
    import pandas as pd
    tabelas = dict(dados_rede.tabelas)
    tabelas["tn_management_adjustments"] = dados_rede["tn_management_adjustments"].iloc[0:0]
    from src.analytics.network.repository import carregar_de_memoria
    sem = b.orcamento(carregar_de_memoria(tabelas), "BUDGET_2027", p27)
    t = b.totais(sem)
    assert t["adjustments"] == 0 and t["final_budget"] == pytest.approx(t["model_budget"])


def test_relatorio_ajustes(dados_rede, orcamentos):
    _, l27 = orcamentos
    r = b.relatorio_ajustes(dados_rede, "BUDGET_2027", l27).set_index("adjustment_id")
    assert not r.loc["ADJ-2027-003", "applied"] and r.loc["ADJ-2027-003", "impact_brl"] == 0
    assert r["reason"].str.len().gt(0).all()


def test_ponte_soma_exata(planos, orcamentos):
    p26, p27 = planos
    l26, l27 = orcamentos
    ponte = b.ponte_orcamento(p26, l26, p27, l27)
    assert ponte["residual"] == pytest.approx(0, abs=1e-4)
    passos = {s["step"]: s["amount_brl"] for s in ponte["steps"]}
    assert passos["rate_effect"] > 0  # reajustes contratuais de 2027


def test_resumo_mensal(orcamentos):
    _, l27 = orcamentos
    r = b.resumo_orcamento(l27)
    assert r["FINAL_BUDGET"].sum() == pytest.approx(l27["amount_brl"].sum())
    assert {"2027-01", "2027-12"} <= set(r["civil_month"])


def test_plano_vs_realizado(dados_rede, planos):
    p26, _ = planos
    pv = v.plano_vs_realizado(dados_rede, "PLAN_2026", p26)
    t = pv["total"]
    assert t["volume_effect"] + t["efficiency_effect"] + t["rate_effect"] == pytest.approx(t["variance"])
    assert t["period"][1] <= dados_rede["tn_trips_actual"]["week_start"].max()
    aereas = pv["detail"][pv["detail"]["route_id"].isin(dados_rede["tn_routes"].query("route_type == 'AIR'")["route_id"])]
    assert (aereas["efficiency_effect"].abs() < 1e-6).all()


def test_extras_e_transportadoras(dados_rede):
    e = v.analise_extras(dados_rede)
    assert set(e["extra_reason"]) == {"RE_DELIVERY", "FISCAL_HOLD", "EXTRA_HELPER", "WAITING_TIME"}
    d = v.desempenho_transportadoras(dados_rede).set_index("carrier_id")
    assert d.loc["ORION", "on_time_rate"] < d.loc["ATLAS", "on_time_rate"]


def test_custo_loja_nova(dados_rede, planos):
    _, p27 = planos
    est = b.estimar_custo_loja_nova(dados_rede, p27, "RS", 3000)
    assert est["estimated_annual_cost"] == pytest.approx(3000 * 52 * est["reference_cost_per_piece"])
    with pytest.raises(ValueError):
        b.estimar_custo_loja_nova(dados_rede, p27, "XX", 1000)
