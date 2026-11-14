"""Acesso aos dados da rede sintética (tn_*) como DataFrames.

As camadas de analytics recebem um objeto `DadosRede`, o que permite
testá-las sem banco (a partir dos CSVs ou de uma geração em memória).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import pandas as pd

from src.database.connection import conectar_banco
from src.database.create_network_tables import ORDEM_CARGA


@dataclass
class DadosRede:
    """Tabelas tn_* em memória, com algumas visões derivadas."""

    tabelas: dict[str, pd.DataFrame]

    def __getitem__(self, nome: str) -> pd.DataFrame:
        return self.tabelas[nome]

    @cached_property
    def calendario(self) -> pd.DataFrame:
        return self.tabelas["tn_calendar"].set_index("week_start")

    @cached_property
    def rotas(self) -> pd.DataFrame:
        return self.tabelas["tn_routes"].set_index("route_id")

    @cached_property
    def veiculos(self) -> pd.DataFrame:
        return self.tabelas["tn_vehicles"].set_index("vehicle_type_id")

    @cached_property
    def veiculo_default(self) -> pd.Series:
        op = self.tabelas["tn_route_vehicle_options"]
        return op[op["is_default"] == 1].set_index("route_id")["vehicle_type_id"]

    @cached_property
    def loja_rota(self) -> pd.DataFrame:
        """Atribuição loja -> rota (uma rota por loja na rede v1)."""
        return self.tabelas["tn_route_stops"][["route_id", "store_id"]].drop_duplicates()

    @cached_property
    def participacao_mes_civil(self) -> pd.DataFrame:
        """week_start × civil_month × share (para alocar semanas em meses civis)."""
        linhas = []
        for ws, js in self.tabelas["tn_calendar"][["week_start", "civil_month_share_json"]].itertuples(index=False):
            for mes, share in json.loads(js).items():
                linhas.append({"week_start": ws, "civil_month": mes, "share": share})
        return pd.DataFrame(linhas)

    def parametros(self, scenario_id: str) -> pd.DataFrame:
        p = self.tabelas["tn_parameters"]
        return p[p["scenario_id"] == scenario_id]

    def cenario(self, scenario_id: str) -> pd.Series:
        c = self.tabelas["tn_scenarios"].set_index("scenario_id")
        if scenario_id not in c.index:
            raise ValueError(f"Cenário não encontrado: {scenario_id}")
        return c.loc[scenario_id]


def _normalizar(tabelas: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    saida = {}
    for nome, df in tabelas.items():
        df = df.copy()
        for coluna in ("week_start", "effective_from", "effective_to", "valid_from", "valid_to", "opening_date", "closing_date"):
            if coluna in df.columns:
                df[coluna] = df[coluna].astype("string").astype(object).where(df[coluna].notna(), None)
        saida[nome] = df
    return saida


def carregar_de_csv(diretorio: Path) -> DadosRede:
    return DadosRede(_normalizar({n: pd.read_csv(Path(diretorio) / f"{n}.csv") for n in ORDEM_CARGA}))


def carregar_de_banco() -> DadosRede:
    with conectar_banco() as conexao:
        tabelas = {n: pd.read_sql_query(f"SELECT * FROM {n}", conexao) for n in ORDEM_CARGA}
    return DadosRede(_normalizar(tabelas))


def carregar_de_memoria(tabelas: dict[str, pd.DataFrame]) -> DadosRede:
    return DadosRede(_normalizar(tabelas))
