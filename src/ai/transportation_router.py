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
    "out_of_scope",
]


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


TRANSPORTATION_ROUTER_PROMPT = """
Você é o roteador de intenção do módulo Transportation
do AI Supply Chain Copilot.

Sua única responsabilidade é classificar a pergunta do usuário
em uma das capacidades analíticas autorizadas.

Capacidades disponíveis:

- network_overview:
  visão geral da operação e do forecast de transporte.

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
  resumo executivo da operação de transporte.

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