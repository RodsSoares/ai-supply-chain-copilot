"""Reconciliação da camada SQL da rede com o motor em Python.

Cada consulta de `sql/network/` é executada sobre a mesma rede sintética usada
pelo motor (carregada em um SQLite em memória) e comparada, linha a linha, com
a função pandas equivalente. Se as duas implementações divergirem, o teste falha.
"""

import sqlite3

import pandas as pd
import pytest

from src.analytics.network import forecasting, variance
from src.analytics.network.sql_queries import (
    CONSULTAS,
    DIRETORIO_SQL,
    carregar_consulta,
    executar_consulta,
)
from src.database.create_network_tables import DDL_NETWORK, ORDEM_CARGA


@pytest.fixture(scope="module")
def conexao(rede_gerada):
    """SQLite em memória com as tabelas tn_* da rede gerada para os testes."""
    c = sqlite3.connect(":memory:")
    for nome in ORDEM_CARGA:
        c.execute(DDL_NETWORK[nome])
        df = rede_gerada.tabelas[nome]
        df = df.astype(object).where(pd.notna(df), None)
        marcadores = ", ".join("?" for _ in df.columns)
        c.executemany(
            f"INSERT INTO {nome} ({', '.join(df.columns)}) VALUES ({marcadores})",
            df.itertuples(index=False, name=None),
        )
    c.commit()
    yield c
    c.close()


def _df(linhas: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(linhas)


def _comparar(sql: pd.DataFrame, motor: pd.DataFrame, chaves: list[str], colunas: list[str]) -> None:
    """Mesmas chaves nos dois lados e mesmos valores em cada coluna comparada."""
    a = sql.sort_values(chaves).reset_index(drop=True)
    b = motor.sort_values(chaves).reset_index(drop=True)
    assert len(a) == len(b)
    assert a[chaves].astype(str).values.tolist() == b[chaves].astype(str).values.tolist()
    for coluna in colunas:
        assert a[coluna].astype(float).tolist() == pytest.approx(b[coluna].astype(float).tolist(), rel=1e-9, abs=1e-9), coluna


# ---------------------------------------------------------------------------
# Catálogo
# ---------------------------------------------------------------------------

def test_toda_consulta_catalogada_tem_arquivo_e_pergunta():
    for nome, consulta in CONSULTAS.items():
        assert (DIRETORIO_SQL / consulta.arquivo).exists(), nome
        assert consulta.pergunta_id.startswith("Q-"), nome
        assert consulta.pergunta_id.split(" ")[0] in carregar_consulta(nome), nome


def test_todo_arquivo_sql_esta_no_catalogo():
    catalogados = {c.arquivo for c in CONSULTAS.values()}
    assert {p.name for p in DIRETORIO_SQL.glob("*.sql")} == catalogados


def test_consulta_nao_catalogada_e_recusada(conexao):
    with pytest.raises(ValueError):
        executar_consulta("drop_everything", conexao)


def test_parametro_desconhecido_e_recusado(conexao):
    with pytest.raises(ValueError):
        executar_consulta("extras_by_reason", conexao, semana_inicial="2026-01-05")


def test_nivel_de_forecast_invalido_e_recusado(conexao):
    with pytest.raises(ValueError):
        executar_consulta("forecast_accuracy", conexao, level="REGION")


# ---------------------------------------------------------------------------
# Q-PRF-01 (realizado) / Q-PRF-02 / Q-PRF-03
# ---------------------------------------------------------------------------

def test_realizado_semanal_reconcilia_com_o_motor(conexao, dados_rede):
    semanas = sorted(dados_rede["tn_trips_actual"]["week_start"].unique())
    inicio, fim = semanas[4], semanas[-5]
    sql = _df(executar_consulta("actual_weekly_by_route", conexao, start_week=inicio, end_week=fim))
    motor = variance.realizado_semanal(dados_rede, inicio, fim)
    _comparar(sql, motor, ["route_id", "week_start"], ["volume", "trips", "cost", "extra_cost", "overflow_trips"])


def test_realizado_semanal_sem_filtro_soma_todas_as_viagens(conexao, dados_rede):
    sql = _df(executar_consulta("actual_weekly_by_route", conexao))
    viagens = dados_rede["tn_trips_actual"]
    assert sql["trips"].sum() == len(viagens)
    assert sql["cost"].sum() == pytest.approx(viagens["freight_cost"].sum())


def test_extras_por_motivo_reconcilia_com_o_motor(conexao, dados_rede):
    sql = _df(executar_consulta("extras_by_reason", conexao))
    motor = variance.analise_extras(dados_rede)
    _comparar(sql, motor, ["extra_reason"], ["occurrences", "extra_cost", "share_of_freight"])
    assert "NONE" not in set(sql["extra_reason"])


def test_extras_por_motivo_respeita_o_periodo(conexao, dados_rede):
    semanas = sorted(dados_rede["tn_trips_actual"]["week_start"].unique())
    inicio, fim = semanas[10], semanas[20]
    sql = _df(executar_consulta("extras_by_reason", conexao, start_week=inicio, end_week=fim))
    motor = variance.analise_extras(dados_rede, inicio, fim)
    _comparar(sql, motor, ["extra_reason"], ["occurrences", "extra_cost", "share_of_freight"])


def test_pontualidade_por_transportadora_reconcilia_com_o_motor(conexao, dados_rede):
    sql = _df(executar_consulta("carrier_on_time", conexao))
    motor = variance.desempenho_transportadoras(dados_rede)
    _comparar(sql, motor, ["carrier_id"], ["trips", "on_time", "on_time_rate", "on_time_target", "gap_to_target"])


def test_pontualidade_mensal_reconcilia_com_o_motor(conexao, dados_rede):
    sql = _df(executar_consulta("carrier_on_time_by_month", conexao))
    motor = variance.desempenho_transportadoras(dados_rede, por_mes=True)
    _comparar(sql, motor, ["carrier_id", "month"], ["trips", "on_time", "on_time_rate", "gap_to_target"])
    assert (sql["below_target"] == (sql["gap_to_target"] < 0).astype(int)).all()


# ---------------------------------------------------------------------------
# Q-FCT-01 / Q-FCT-02 / Q-FCT-04
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("nivel, chave", [("STORE", "store_id"), ("ROUTE", "route_id"), ("DC", "dc_id")])
def test_acuracia_do_forecast_reconcilia_com_o_motor(conexao, dados_rede, nivel, chave):
    sql = _df(executar_consulta("forecast_accuracy", conexao, forecast_version="BUDGET_2026", level=nivel))
    motor = forecasting.acuracia_forecast(dados_rede, "BUDGET_2026", nivel).rename(columns={chave: "level_key"})
    com_volume = motor["actual"] > 0
    _comparar(sql, motor, ["level_key"], ["actual", "forecast", "abs_error", "error"])
    _comparar(sql[sql["actual"] > 0], motor[com_volume], ["level_key"], ["wape", "bias"])


def test_acuracia_do_forecast_na_rede_reconcilia_com_o_motor(conexao, dados_rede):
    sql = executar_consulta("forecast_accuracy", conexao, forecast_version="BUDGET_2026", level="NETWORK")
    motor = forecasting.acuracia_forecast(dados_rede, "BUDGET_2026", "NETWORK").iloc[0]
    assert len(sql) == 1
    for coluna in ("actual", "forecast", "abs_error", "error", "wape", "bias"):
        assert sql[0][coluna] == pytest.approx(float(motor[coluna])), coluna


def test_wape_da_rota_nao_soma_erros_que_se_compensam_entre_lojas(conexao):
    """O erro absoluto é medido no nível pedido: o WAPE da rota não pode superar o das lojas somadas."""
    loja = _df(executar_consulta("forecast_accuracy", conexao, level="STORE"))
    rota = _df(executar_consulta("forecast_accuracy", conexao, level="ROUTE"))
    assert rota["abs_error"].sum() <= loja["abs_error"].sum()
    assert rota["actual"].sum() == loja["actual"].sum()


def test_versao_de_forecast_inexistente_nao_devolve_linhas(conexao):
    assert executar_consulta("forecast_accuracy", conexao, forecast_version="NAO_EXISTE") == []


@pytest.mark.parametrize("semanas", [52, 26])
def test_variabilidade_de_demanda_reconcilia_com_o_motor(conexao, dados_rede, semanas):
    sql = _df(executar_consulta("demand_variability", conexao, last_weeks=semanas))
    motor = forecasting.variabilidade_demanda(dados_rede, semanas)
    _comparar(sql, motor, ["store_id"], ["cv"])
    assert (sql["weeks"] == semanas).all()


def test_variabilidade_conta_semanas_sem_expedicao_como_zero(conexao):
    """Loja com semana sem expedição precisa ter a média calculada sobre a grade completa."""
    linhas = conexao.execute(
        """
        WITH semanas AS (
            SELECT DISTINCT week_start FROM tn_demand_history ORDER BY week_start DESC LIMIT 52
        )
        SELECT h.store_id, SUM(h.pieces_shipped) AS total
        FROM tn_demand_history AS h
        JOIN semanas AS s ON s.week_start = h.week_start
        GROUP BY h.store_id
        """
    ).fetchall()
    totais = dict(linhas)
    for linha in executar_consulta("demand_variability", conexao, last_weeks=52):
        assert linha["mean_weekly_pieces"] == pytest.approx(totais[linha["store_id"]] / 52)
