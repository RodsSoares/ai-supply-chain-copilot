from typing import Literal

from pydantic import BaseModel

from src.ai.client import gerar_resposta_estruturada


TransportationIntentName = Literal[
    "network_overview",
    "economic_efficiency",
    "weekly_evolution",
    "cost_share",
    "cost_ranking",
    "cost_concentration",
    "recent_trend",
    "operational_changes",
    "cost_pressure",
    "executive_summary",
    # Network Planning & Budget (v2.x)
    "plan_route_week",
    "analyze_overflow",
    "find_consolidation_candidates",
    "run_what_if",
    "analyze_dc_load",
    "forecast_accuracy",
    "forecast_value_added",
    "demand_variability",
    "budget_summary",
    "budget_bridge",
    "adjustment_report",
    "new_store_cost_estimate",
    "plan_vs_actual",
    "extras_analysis",
    "carrier_performance",
    "emissions_summary",
    "out_of_scope",
]

NetworkScenarioName = Literal["PLAN_2026", "BUDGET_2027"]


class TransportationIntent(BaseModel):
    """
    Contrato estruturado para representar a intenção
    de uma pergunta dentro do domínio Transportation.

    O modelo não calcula métricas nem executa análises.
    Ele apenas descreve qual capacidade determinística
    deve ser utilizada posteriormente pela orquestração.
    """

    intent: TransportationIntentName
    route_id: str | None = None

    # Campos opcionais das capacidades de rede (v2.x). O LLM apenas extrai
    # valores explícitos da pergunta; o dispatcher constrói os parâmetros.
    scenario_id: NetworkScenarioName | None = None
    forecast_version: Literal["BUDGET_2026", "BUDGET_2027"] | None = None
    level: Literal["NETWORK", "DC", "ROUTE", "STORE"] | None = None
    uf: str | None = None
    weekly_pieces: float | None = None
    what_if_frequency_basis: Literal["MEAN", "P75", "MAX"] | None = None
    what_if_volume_change_pct: float | None = None


TRANSPORTATION_ROUTER_PROMPT = """
Você é o roteador de intenção do módulo Transportation
do AI Supply Chain Copilot.

Sua única responsabilidade é classificar a pergunta do usuário
em uma das capacidades analíticas autorizadas.

Capacidades disponíveis:

- network_overview:
  detalhamento da operação planejada e do forecast de transporte
  por rota e período. Use quando a pergunta exigir visão operacional
  detalhada, e não apenas um resumo consolidado da rede.

- economic_efficiency:
  eficiência econômica, utilização de capacidade, ociosidade
  e relação entre volume planejado, capacidade e custo.

- weekly_evolution:
  evolução da operação ao longo das semanas.

- cost_share:
  participação de rotas no custo total da rede.

- cost_ranking:
  ranking de custos e identificação das rotas mais caras.

- cost_concentration:
  concentração do custo da rede.

- recent_trend:
  tendência recente das métricas de transporte.

- operational_changes:
  mudanças operacionais entre períodos, incluindo alterações
  de veículo, viagens ou capacidade.

- cost_pressure:
  pressão ou crescimento de custos na rede.

- executive_summary:
  visão executiva consolidada da rede de transporte.
  Use para perguntas gerais sobre como está a operação da rede,
  desempenho consolidado, situação atual ou evolução executiva.

Capacidades da rede (Network Planning & Budget — cenários PLAN_2026 e BUDGET_2027):

- plan_route_week: viagens por rota, veículo, ocupação e custo por peça no plano.
- analyze_overflow: semanas em que a frequência planejada não comporta o volume e custo spot.
- find_consolidation_candidates: rotas com baixa ocupação e alternativas de veículo/frequência.
- run_what_if: simulação. Preencha what_if_frequency_basis (MEAN, P75, MAX) e/ou
  what_if_volume_change_pct (ex.: 10 para +10%) somente se a pergunta trouxer esses valores.
- analyze_dc_load: carga dos centros de distribuição.
- forecast_accuracy: acurácia (WAPE) e viés de uma versão de forecast; level opcional.
- forecast_value_added: comparação dos modelos de forecast contra o naïve sazonal.
- demand_variability: lojas com demanda mais volátil.
- budget_summary: orçamento por mês e componente.
- budget_bridge: explicação da variação entre o plano 2026 e o orçamento 2027.
- adjustment_report: ajustes gerenciais, motivos, aprovação e impacto.
- new_store_cost_estimate: custo para servir uma loja nova; preencha uf e weekly_pieces.
- plan_vs_actual: plano vs. realizado e seus direcionadores.
- extras_analysis: custos extras por motivo.
- carrier_performance: entregas no prazo por transportadora vs. meta.
- emissions_summary: emissões estimadas de GEE por rota e por peça.

- out_of_scope:
  pergunta que não pode ser respondida por nenhuma das
  capacidades analíticas disponíveis no módulo Transportation.

Regras:

1. Escolha somente uma das capacidades autorizadas.
2. Não calcule métricas.
3. Não responda à pergunta do usuário.
4. Não invente dados.
5. Extraia route_id somente quando uma rota específica estiver
   explicitamente identificada na pergunta.
6. Se nenhuma rota específica estiver identificada,
   route_id deve ser null.
7. Se a pergunta não puder ser respondida por nenhuma das
   capacidades disponíveis, retorne out_of_scope.
8. Nunca force uma pergunta fora do escopo para uma capacidade
   analítica existente.
9. Quando intent for out_of_scope, route_id deve ser null.
10. Para capacidades da rede, preencha scenario_id, forecast_version, level,
    uf, weekly_pieces e campos what_if_* somente com valores explícitos
    na pergunta; caso contrário, deixe null.
"""


def rotear_pergunta_transporte(
    pergunta: str,
) -> TransportationIntent:
    """
    Interpreta a pergunta do usuário e retorna uma intenção
    estruturada e validada para o domínio Transportation.
    """

    resultado = gerar_resposta_estruturada(
        pergunta=pergunta,
        instrucoes=TRANSPORTATION_ROUTER_PROMPT,
        modelo_saida=TransportationIntent,
    )

    if not isinstance(resultado, TransportationIntent):
        raise RuntimeError(
            "O roteador não retornou uma intenção "
            "de Transportation válida."
        )

    return resultado