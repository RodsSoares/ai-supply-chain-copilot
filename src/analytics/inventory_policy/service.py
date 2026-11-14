"""Capacidades determinísticas da política dinâmica de estoque (v2.6).

Prontas para serem expostas ao Copilot de Inventory. O fluxo atual de IA de
Inventory (contexto + Golden Set 12/12) não é alterado nesta release.
"""

from __future__ import annotations

from functools import lru_cache

import pandas as pd

from src.analytics.inventory_policy import safety_stock as ss
from src.synthetic.inventory_demand_generator import CAMINHO_SAIDA, carregar_config, carregar_erp


@lru_cache(maxsize=1)
def _entradas() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    return carregar_erp(), pd.read_csv(CAMINHO_SAIDA), carregar_config()


def _registros(df: pd.DataFrame, limite: int = 15) -> list[dict]:
    return df.head(limite).round(4).astype(object).where(df.head(limite).notna(), None).to_dict("records")


def safety_stock(sku: str | None = None, service_level: float | None = None, **_) -> dict:
    """Q-INV-01 — estoque de segurança, ponto de pedido e máximo por SKU."""
    erp, demanda, config = _entradas()
    niveis = {c: service_level for c in "ABC"} if service_level else None
    pol = ss.calcular_politica(erp, demanda, config, niveis)
    if sku:
        pol = pol[pol["sku"] == sku]
        if pol.empty:
            raise ValueError(f"SKU não encontrado: {sku}")
    colunas = ["sku", "produto", "classe_abc", "service_level", "mean_weekly", "std_weekly", "lead_time_weeks",
               "safety_stock", "reorder_point", "order_up_to", "estoque_atual", "estoque_minimo", "estoque_maximo",
               "static_action", "dynamic_action"]
    return {"capability": "safety_stock", "skus": _registros(pol[colunas].sort_values("safety_stock", ascending=False))}


def reorder_alerts(**_) -> dict:
    """Q-INV-02 — SKUs abaixo do ponto de pedido dinâmico."""
    erp, demanda, config = _entradas()
    pol = ss.calcular_politica(erp, demanda, config)
    alertas = pol[pol["dynamic_action"] == "REPOR"].assign(order_value=lambda d: d["dynamic_order_qty"] * d["custo_unitario"])
    alertas = alertas.sort_values("order_value", ascending=False)
    return {"capability": "reorder_alerts", "alerts": int(len(alertas)),
            "order_value": float(alertas["order_value"].sum()),
            "skus": _registros(alertas[["sku", "produto", "classe_abc", "estoque_atual", "reorder_point",
                                        "order_up_to", "dynamic_order_qty", "order_value", "static_action"]])}


def policy_comparison(**_) -> dict:
    """Política estática (min/max do cadastro) vs. dinâmica (nível de serviço)."""
    erp, demanda, config = _entradas()
    pol = ss.calcular_politica(erp, demanda, config)
    resumo = ss.comparar_politicas(pol)
    cobertura = ss.cobertura_historica(pol, demanda)
    resumo["empirical_cycle_service_level_by_abc"] = (
        cobertura.groupby("classe_abc")[["service_level", "empirical_cycle_service_level"]].mean().round(4).reset_index().to_dict("records"))
    return {"capability": "policy_comparison", **resumo}


def service_capital_curve(**_) -> dict:
    """Trade-off nível de serviço × capital em estoque de segurança."""
    erp, demanda, config = _entradas()
    return {"capability": "service_capital_curve", "curve": _registros(ss.curva_servico_capital(erp, demanda, config))}


CAPACIDADES_INVENTORY_POLICY = {
    "safety_stock": safety_stock,
    "reorder_alerts": reorder_alerts,
    "policy_comparison": policy_comparison,
    "service_capital_curve": service_capital_curve,
}


def executar_capacidade(nome: str, **parametros) -> dict:
    if nome not in CAPACIDADES_INVENTORY_POLICY:
        raise ValueError(f"Capacidade de estoque não autorizada: {nome}")
    return CAPACIDADES_INVENTORY_POLICY[nome](**parametros)
