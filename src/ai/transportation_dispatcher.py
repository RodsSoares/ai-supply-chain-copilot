from typing import Any, Callable

from src.ai.transportation_router import TransportationIntent
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