"""Gerador de histórico semanal de demanda por SKU (v2.6), 100% sintético.

Calibrado pelo consumo médio mensal do dataset ERP sintético existente
(`sample_data/erp_inventory.csv`): a demanda média gerada é coerente com o
cadastro, e a variabilidade depende da classe ABC (A estável, C intermitente).
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


CAMINHO_CONFIG = Path("config/inventory_policy.json")
CAMINHO_ERP = Path("sample_data/erp_inventory.csv")
CAMINHO_SAIDA = Path("data/synthetic/inventory/sku_weekly_demand.csv")


def carregar_config(caminho: Path = CAMINHO_CONFIG) -> dict:
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def carregar_erp(caminho: Path = CAMINHO_ERP) -> pd.DataFrame:
    return pd.read_csv(caminho, sep=";", encoding="utf-8-sig")


def gerar_demanda_semanal(erp: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Demanda semanal por SKU: média do cadastro × sazonalidade × ruído (+ zeros para C)."""
    rng = np.random.default_rng(config["seed"])
    inicio = date.fromisoformat(config["history"]["first_week"])
    n = config["history"]["weeks"]
    semanas = [(inicio + timedelta(weeks=i)).isoformat() for i in range(n)]
    t = np.arange(n)
    blocos = []
    for item in erp.itertuples(index=False):
        media = item.consumo_medio_mensal / config["weeks_per_month"]
        cv = config["demand_cv_by_abc"][item.classe_abc]
        p_zero = config["zero_week_probability_by_abc"][item.classe_abc]
        fase = rng.uniform(0, 2 * np.pi)
        sazonal = 1 + config["seasonal_amplitude"] * np.sin(2 * np.pi * t / 52 + fase)
        ativo = rng.random(n) >= p_zero
        # compensa as semanas zeradas para manter a média do cadastro
        nivel = media / (1 - p_zero) if p_zero < 1 else media
        sigma = np.sqrt(np.log(1 + cv ** 2))
        ruido = rng.lognormal(-0.5 * sigma ** 2, sigma, n)
        demanda = np.where(ativo, np.round(nivel * sazonal * ruido), 0).astype(int)
        blocos.append(pd.DataFrame({"sku": item.sku, "week_start": semanas, "demand_units": demanda}))
    return pd.concat(blocos, ignore_index=True)


def gerar_e_salvar(saida: Path = CAMINHO_SAIDA) -> pd.DataFrame:
    df = gerar_demanda_semanal(carregar_erp(), carregar_config())
    saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(saida, index=False, lineterminator="\n")
    return df


if __name__ == "__main__":
    print(f"{len(gerar_e_salvar()):,} linhas -> {CAMINHO_SAIDA}")
