"""Camada SQL da rede (tn_*): uma consulta por pergunta de negócio.

Cada arquivo em `sql/network/` responde a uma pergunta do dicionário
`docs/specs/transportation_business_questions_kpis.md` e reconcilia com a
função equivalente do motor em Python (ver `tests/test_network_sql_queries.py`).

A camada roda lado a lado com o motor: as capacidades do Copilot continuam
usando `service.py`. O SQL serve como verificação independente dos números e
como fonte direta para BI.
"""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from src.database.connection import conectar_banco


DIRETORIO_SQL = Path(__file__).resolve().parents[3] / "sql" / "network"


@dataclass(frozen=True)
class Consulta:
    """Metadados de uma consulta: a pergunta que responde e seus parâmetros."""

    arquivo: str
    pergunta_id: str
    pergunta: str
    parametros: dict[str, object]
    reconcilia_com: str


CONSULTAS: dict[str, Consulta] = {
    "actual_weekly_by_route": Consulta(
        arquivo="q_prf_01_actual_weekly_by_route.sql",
        pergunta_id="Q-PRF-01",
        pergunta="Where did actual cost deviate from plan? (actual side, route-week grain)",
        parametros={"start_week": None, "end_week": None},
        reconcilia_com="variance.realizado_semanal",
    ),
    "extras_by_reason": Consulta(
        arquivo="q_prf_02_extras_by_reason.sql",
        pergunta_id="Q-PRF-02",
        pergunta="How much did extras cost, and for which reasons?",
        parametros={"start_week": None, "end_week": None},
        reconcilia_com="variance.analise_extras",
    ),
    "carrier_on_time": Consulta(
        arquivo="q_prf_03_carrier_on_time.sql",
        pergunta_id="Q-PRF-03",
        pergunta="Which carrier misses the on-time target?",
        parametros={},
        reconcilia_com="variance.desempenho_transportadoras",
    ),
    "carrier_on_time_by_month": Consulta(
        arquivo="q_prf_03_carrier_on_time_by_month.sql",
        pergunta_id="Q-PRF-03",
        pergunta="In which months did each carrier miss the on-time target?",
        parametros={},
        reconcilia_com="variance.desempenho_transportadoras(por_mes=True)",
    ),
    "forecast_accuracy": Consulta(
        arquivo="q_fct_01_forecast_accuracy.sql",
        pergunta_id="Q-FCT-01 / Q-FCT-02",
        pergunta="How accurate was the forecast by DC / route / store, and is it biased?",
        parametros={"forecast_version": "BUDGET_2026", "level": "ROUTE"},
        reconcilia_com="forecasting.acuracia_forecast",
    ),
    "demand_variability": Consulta(
        arquivo="q_fct_04_demand_variability.sql",
        pergunta_id="Q-FCT-04",
        pergunta="Which stores have the most volatile demand?",
        parametros={"last_weeks": 52},
        reconcilia_com="forecasting.variabilidade_demanda",
    ),
}

NIVEIS_FORECAST = ("STORE", "ROUTE", "DC", "NETWORK")


def carregar_consulta(nome: str) -> str:
    """Devolve o texto SQL de uma consulta catalogada."""
    if nome not in CONSULTAS:
        raise ValueError(f"Consulta SQL não catalogada: {nome}")
    return (DIRETORIO_SQL / CONSULTAS[nome].arquivo).read_text(encoding="utf-8")


def _garantir_sqrt(conexao: sqlite3.Connection) -> None:
    """Registra SQRT quando o SQLite foi compilado sem as funções matemáticas."""
    try:
        conexao.execute("SELECT SQRT(4)")
    except sqlite3.OperationalError:
        conexao.create_function("SQRT", 1, lambda x: None if x is None else math.sqrt(x), deterministic=True)


def executar_consulta(nome: str, conexao: sqlite3.Connection | None = None, **parametros) -> list[dict]:
    """Executa uma consulta catalogada e devolve as linhas como dicionários.

    Parâmetros não informados assumem o padrão do catálogo; parâmetros que a
    consulta não declara são recusados, para que um erro de digitação não
    seja ignorado em silêncio.
    """
    sql = carregar_consulta(nome)
    padrao = CONSULTAS[nome].parametros
    desconhecidos = set(parametros) - set(padrao)
    if desconhecidos:
        raise ValueError(f"Parâmetros não aceitos por {nome}: {sorted(desconhecidos)}")
    valores = {**padrao, **parametros}
    if "level" in valores and valores["level"] not in NIVEIS_FORECAST:
        raise ValueError(f"Nível inválido: {valores['level']}")

    def _rodar(c: sqlite3.Connection) -> list[dict]:
        _garantir_sqrt(c)
        cursor = c.execute(sql, valores)
        colunas = [d[0] for d in cursor.description]
        return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]

    if conexao is not None:
        return _rodar(conexao)
    with conectar_banco() as propria:
        return _rodar(propria)
