from typing import Any, Callable

from src.ai.transportation_router import TransportationIntent
from src.analytics.network.service import CAPACIDADES_NETWORK, executar_capacidade
from src.analytics.transportation.sql_analysis import (
    analisar_concentracao_custo_rede,
    analisar_eficiencia_economica,
    analisar_evolucao_semanal,
    analisar_mudancas_operacionais,
    analisar_operacao_forecast,
    analisar_participacao_custo_rede,
    analisar_pressao_custo_rede,
    analisar_ranking_custo_semanal,
    analisar_resumo_executivo_semanal,
    analisar_tendencia_recente,
)


ANALISES_TRANSPORTATION: dict[str, Callable[[], Any]] = {
    "network_overview": analisar_operacao_forecast,
    "economic_efficiency": analisar_eficiencia_economica,
    "weekly_evolution": analisar_evolucao_semanal,
    "cost_share": analisar_participacao_custo_rede,
    "cost_ranking": analisar_ranking_custo_semanal,
    "cost_concentration": analisar_concentracao_custo_rede,
    "recent_trend": analisar_tendencia_recente,
    "operational_changes": analisar_mudancas_operacionais,
    "cost_pressure": analisar_pressao_custo_rede,
    "executive_summary": analisar_resumo_executivo_semanal,
}


def parametros_capacidade_network(
    intencao: TransportationIntent,
) -> dict[str, Any]:
    """
    Constrói deterministicamente os parâmetros de uma capacidade de rede
    a partir dos campos validados da intenção.

    O LLM nunca envia overrides livres: o what-if só aceita os campos
    tipados do contrato, convertidos aqui em overrides de cenário.
    """

    parametros: dict[str, Any] = {}

    for campo in ("route_id", "scenario_id", "forecast_version", "level", "uf", "weekly_pieces"):
        valor = getattr(intencao, campo)
        if valor is not None:
            parametros[campo] = valor

    if intencao.intent == "run_what_if":
        overrides = []
        if intencao.what_if_frequency_basis:
            overrides.append({"parameter_key": "frequency_basis", "value": intencao.what_if_frequency_basis})
        if intencao.what_if_volume_change_pct is not None:
            overrides.append({"parameter_key": "volume_multiplier", "value": 1 + intencao.what_if_volume_change_pct / 100})
        parametros["overrides"] = overrides
        parametros.pop("route_id", None)

    return parametros


def executar_intencao_transporte(
    intencao: TransportationIntent,
) -> Any:
    """
    Executa deterministicamente a análise autorizada
    correspondente à intenção de Transportation.

    O dispatcher não interpreta linguagem natural e não utiliza LLM.
    """

    if intencao.intent == "out_of_scope":
        raise ValueError(
            "A pergunta está fora do escopo analítico "
            "de Transportation."
        )

    if intencao.intent in CAPACIDADES_NETWORK:
        return executar_capacidade(
            intencao.intent,
            **parametros_capacidade_network(intencao),
        )

    funcao_analitica = ANALISES_TRANSPORTATION.get(
        intencao.intent
    )

    if funcao_analitica is None:
        raise ValueError(
            f"Intent de Transportation não suportada: "
            f"{intencao.intent}"
        )

    resultado = funcao_analitica()

    if intencao.route_id is None:
        return resultado

    if not isinstance(resultado, list):
        return resultado

    return [
        registro
        for registro in resultado
        if registro.get("route_id") == intencao.route_id
    ]