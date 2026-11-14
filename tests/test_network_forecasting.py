"""Testes da v2.2 — forecast e acurácia."""

import numpy as np
import pandas as pd
import pytest

from src.analytics.network import forecasting as f


def test_metricas_calculadas_a_mao():
    real, previsto = [100, 200, 0], [110, 180, 10]
    assert f.wape(real, previsto) == pytest.approx(40 / 300)
    assert f.vies(real, previsto) == pytest.approx(0 / 300)
    assert f.vies([100], [120]) == pytest.approx(0.2)
    assert f.tracking_signal([100, 100], [110, 110]) == pytest.approx(2.0)


def test_seasonal_naive_repete_ano_anterior():
    y = np.arange(104, dtype=float)
    previsto = f.prever_seasonal_naive(y, 3)
    assert previsto.tolist() == [52.0, 53.0, 54.0]


def test_media_movel():
    assert f.prever_media_movel(np.array([1, 2, 3, 4], float), 2, k=2).tolist() == [3.5, 3.5]


def test_holt_winters_aprende_sazonalidade():
    semanas = np.arange(156)
    y = 1000 * (1 + 0.3 * np.sin(2 * np.pi * semanas / 52)) * (1 + 0.002 * semanas)
    previsto = f.prever_holt_winters(y[:130], 26)
    assert f.wape(y[130:], previsto) < 0.03


def test_modelo_desconhecido():
    with pytest.raises(ValueError):
        f.prever("XYZ", np.ones(60), 1)


@pytest.fixture(scope="module")
def backtest(dados_rede):
    return f.backtest(dados_rede)


def test_backtest_cobre_rotas_e_modelos(backtest, dados_rede):
    assert set(backtest["model"]) == set(f.MODELOS)
    assert backtest["route_id"].nunique() == len(dados_rede["tn_routes"])
    assert (backtest["abs_error"] >= backtest["error"].abs() - 1e-6).all()


def test_holt_winters_supera_naive_na_rede(backtest):
    rede = f.resumo_rede_backtest(backtest).set_index("model")
    assert rede.loc["HOLT_WINTERS", "wape"] < rede.loc["SEASONAL_NAIVE", "wape"]


def test_resumo_backtest_fva(backtest):
    resumo = f.resumir_backtest(backtest)
    assert (resumo["fva_vs_naive"] >= -1e-12).all()  # melhor modelo nunca pior que o naïve
    assert set(resumo["best_model"]) <= set(f.MODELOS)


def test_acuracia_budget_tem_vies_otimista(dados_rede):
    rede = f.acuracia_forecast(dados_rede, "BUDGET_2026", "NETWORK").iloc[0]
    assert rede["bias"] > 0  # premissa de crescimento acima da tendência real


def test_erro_aumenta_com_granularidade(dados_rede):
    wapes = [f.acuracia_forecast(dados_rede, "BUDGET_2026", n).pipe(lambda a: a["abs_error"].sum() / a["actual"].sum())
             for n in ("NETWORK", "ROUTE", "STORE")]
    assert wapes[0] < wapes[1] < wapes[2]


def test_acuracia_versao_inexistente(dados_rede):
    with pytest.raises(ValueError):
        f.acuracia_forecast(dados_rede, "NAO_EXISTE")


def test_forecast_modelo_desagrega_e_respeita_lojas(dados_rede):
    fc = f.gerar_forecast_modelo(dados_rede, "MODEL_2027", "2027-01-04", "2027-12-27", versao_lojas_novas="BUDGET_2027")
    assert fc["week_start"].min() == "2027-01-04" and fc["week_start"].max() == "2027-12-27"
    fechadas = set(dados_rede["tn_stores"].query("status == 'CLOSED'")["store_id"])
    assert fechadas.isdisjoint(set(fc["store_id"]))
    sem_historico = set(dados_rede["tn_stores"]["store_id"]) - set(dados_rede["tn_demand_history"]["store_id"])
    copiadas = set(fc[fc["model_name"].str.startswith("COPIED_FROM")]["store_id"])
    assert copiadas == sem_historico
    assert (fc["forecast_pieces"] >= 0).all()


def test_forecast_modelo_com_corte_historico(dados_rede):
    fc = f.gerar_forecast_modelo(dados_rede, "MODEL_2026", "2026-01-05", "2026-03-30", ultima_semana_historico="2025-10-06")
    assert fc["created_at"].iloc[0] == "2025-10-06"
    assert len(fc) > 0
