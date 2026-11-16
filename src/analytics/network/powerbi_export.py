"""Tabelas da rede (tn_*) para o kit Power BI, alimentadas pela camada SQL.

Cada fato do Power BI sai de uma consulta de `sql/network/`, então o número
do dashboard é o mesmo que os testes reconciliam com o motor em Python.
Os nomes de coluna seguem a convenção do kit (português, snake_case).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.analytics.network.sql_queries import NIVEIS_FORECAST, executar_consulta
from src.database.create_network_tables import DDL_NETWORK, ORDEM_CARGA


VERSAO_FORECAST = "BUDGET_2026"
SEMANAS_VARIABILIDADE = 52

# tabela do kit -> (consulta, {coluna da consulta: coluna do kit})
FATOS = {
    "fato_rede_realizado": (
        "actual_weekly_by_route",
        {
            "route_id": "rota_rede",
            "week_start": "semana_inicio",
            "volume": "volume",
            "trips": "viagens",
            "cost": "custo",
            "extra_cost": "custo_extra",
            "overflow_trips": "viagens_overflow",
        },
    ),
    "fato_rede_extras": (
        "extras_by_reason",
        {
            "extra_reason": "motivo_extra",
            "occurrences": "ocorrencias",
            "extra_cost": "custo_extra",
            "share_of_freight": "participacao_frete",
        },
    ),
    "fato_rede_pontualidade": (
        "carrier_on_time_by_month",
        {
            "carrier_id": "transportadora",
            "month": "mes",
            "trips": "viagens",
            "on_time": "no_prazo",
            "on_time_rate": "taxa_no_prazo",
            "on_time_target": "meta_no_prazo",
            "gap_to_target": "desvio_meta",
            "below_target": "abaixo_da_meta",
        },
    ),
    "fato_rede_acuracia": (
        "forecast_accuracy",
        {
            "forecast_version": "versao_forecast",
            "level": "nivel",
            "level_key": "chave",
            "actual": "realizado",
            "forecast": "previsto",
            "abs_error": "erro_absoluto",
            "error": "erro",
            "wape": "wape",
            "bias": "bias",
        },
    ),
    "fato_rede_variabilidade": (
        "demand_variability",
        {
            "store_id": "loja",
            "cv": "cv",
            "cluster": "cluster",
            "uf": "uf",
            "mean_weekly_pieces": "media_semanal",
            "std_weekly_pieces": "desvio_semanal",
            "weeks": "semanas",
        },
    ),
}

SQL_DIM_ROTAS = """
    SELECT
        route_id      AS rota_rede,
        dc_id         AS cd,
        carrier_id    AS transportadora,
        route_type    AS tipo_rota,
        route_profile AS perfil_rota,
        uf            AS uf,
        distance_km   AS distancia_km,
        stops_count   AS paradas
    FROM tn_routes
    ORDER BY route_id
"""

# (muitos) -> (um)
RELACIONAMENTOS = [("fato_rede_realizado", "rota_rede", "dim_rede_rotas", "rota_rede")]


def conexao_em_memoria(tabelas: dict[str, pd.DataFrame]) -> sqlite3.Connection:
    """Carrega as tabelas tn_* em um SQLite em memória, com o DDL oficial."""
    conexao = sqlite3.connect(":memory:")
    for nome in ORDEM_CARGA:
        conexao.execute(DDL_NETWORK[nome])
        df = tabelas[nome]
        df = df.astype(object).where(pd.notna(df), None)
        marcadores = ", ".join("?" for _ in df.columns)
        conexao.executemany(
            f"INSERT INTO {nome} ({', '.join(df.columns)}) VALUES ({marcadores})",
            df.itertuples(index=False, name=None),
        )
    conexao.commit()
    return conexao


def _fato(conexao: sqlite3.Connection, consulta: str, colunas: dict[str, str], **parametros) -> pd.DataFrame:
    df = pd.DataFrame(executar_consulta(consulta, conexao, **parametros))
    return df[list(colunas)].rename(columns=colunas)


def montar_tabelas(conexao: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    """Todas as tabelas da rede para o kit, na convenção de nomes do Power BI."""
    tabelas: dict[str, pd.DataFrame] = {}
    for nome, (consulta, colunas) in FATOS.items():
        if consulta == "forecast_accuracy":
            # um bloco por nível: o WAPE não é somável entre níveis (ver a consulta)
            tabelas[nome] = pd.concat(
                [
                    _fato(conexao, consulta, colunas, forecast_version=VERSAO_FORECAST, level=nivel)
                    for nivel in NIVEIS_FORECAST
                ],
                ignore_index=True,
            )
        elif consulta == "demand_variability":
            tabelas[nome] = _fato(conexao, consulta, colunas, last_weeks=SEMANAS_VARIABILIDADE)
        else:
            tabelas[nome] = _fato(conexao, consulta, colunas)
    tabelas["dim_rede_rotas"] = pd.read_sql(SQL_DIM_ROTAS, conexao)
    return tabelas


def exportar(conexao: sqlite3.Connection, pasta: str | Path) -> dict[str, int]:
    """Grava os CSVs no formato do kit (';', decimal ',', UTF-8 com BOM)."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    linhas = {}
    for nome, df in montar_tabelas(conexao).items():
        df.to_csv(pasta / f"{nome}.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")
        linhas[nome] = len(df)
    return linhas
