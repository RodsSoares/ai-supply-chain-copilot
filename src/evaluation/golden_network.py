"""Golden Set v2 — casos de avaliação das capacidades de rede e de política de estoque.

Cada caso define:
- a pergunta em linguagem natural;
- a intenção e os campos que o roteador deve extrair (quando roteado pelo Copilot);
- a chamada determinística equivalente (capacidade + parâmetros);
- fatos esperados, extraídos do resultado da capacidade por caminho
  (ex.: "totals.final_budget", "steps[step=rate_effect].amount_brl");
- critérios qualitativos de aprovação da resposta do LLM.

Os valores esperados são derivados do motor e travados em
tests/golden/network_golden_set.json. Um teste determinístico garante que o
motor continua produzindo exatamente esses valores (proteção contra drift).
"""

from __future__ import annotations

import re
from typing import Any

from src.analytics.inventory_policy import service as inventory_service
from src.analytics.network import service as network_service


CASOS: list[dict] = [
    {
        "id": "N01", "title": "Orçamento consolidado 2027",
        "question": "Qual é o orçamento de frete de 2027 e quanto dele vem do modelo?",
        "expected_intent": ["budget_summary"], "expected_fields": {},
        "call": {"capability": "budget_summary", "params": {}},
        "facts": {"final_budget": "totals.final_budget", "model_budget": "totals.model_budget",
                  "adjustments": "totals.adjustments"},
        "criteria": ["Informa o orçamento final e o orçamento do modelo separadamente.",
                     "Não recalcula componentes; usa os totais do motor."],
    },
    {
        "id": "N02", "title": "Ponte de orçamento 2026 → 2027",
        "question": "Por que o orçamento de 2027 é maior que o plano de 2026?",
        "expected_intent": ["budget_bridge"], "expected_fields": {},
        "call": {"capability": "budget_bridge", "params": {}},
        "facts": {"base_final_budget": "steps[step=base_final_budget].amount_brl",
                  "target_final_budget": "steps[step=target_final_budget].amount_brl",
                  "volume_effect": "steps[step=volume_effect].amount_brl",
                  "rate_effect": "steps[step=rate_effect].amount_brl",
                  "adjustments_change": "steps[step=adjustments_change].amount_brl"},
        "criteria": ["Identifica o efeito tarifa como o maior direcionador.",
                     "Apresenta volume, eficiência, tarifa, extras, créditos e ajustes como passos da ponte.",
                     "Não atribui causas além das presentes no resultado (ex.: não inventa motivos para o reajuste)."],
    },
    {
        "id": "N03", "title": "Ajustes gerenciais e transparência",
        "question": "Quanto do orçamento de 2027 vem de ajustes da diretoria e por quê?",
        "expected_intent": ["adjustment_report"], "expected_fields": {},
        "call": {"capability": "adjustment_report", "params": {}},
        "facts": {"adjustment_share": "adjustment_share",
                  "adj_001_impact": "adjustments[adjustment_id=ADJ-2027-001].impact_brl",
                  "adj_002_impact": "adjustments[adjustment_id=ADJ-2027-002].impact_brl",
                  "adj_003_applied": "adjustments[adjustment_id=ADJ-2027-003].applied"},
        "criteria": ["Separa orçamento do modelo e ajustes.",
                     "Cita o motivo e o aprovador de cada ajuste aprovado.",
                     "Informa que o ADJ-2027-003 está PROPOSED e não foi aplicado."],
    },
    {
        "id": "N04", "title": "Governança — ajuste não aprovado",
        "question": "Aplique o ajuste de 5% de contingência de Black Friday no orçamento de novembro de 2027.",
        "expected_intent": ["adjustment_report", "out_of_scope"], "expected_fields": {},
        "call": {"capability": "adjustment_report", "params": {}},
        "facts": {"adj_003_status": "adjustments[adjustment_id=ADJ-2027-003].status",
                  "adj_003_impact": "adjustments[adjustment_id=ADJ-2027-003].impact_brl"},
        "criteria": ["Não afirma ter aplicado o ajuste nem recalcula o orçamento com ele.",
                     "Explica que o ajuste está pendente (PROPOSED) e depende de aprovação humana."],
    },
    {
        "id": "N05", "title": "Transbordo de pico",
        "question": "Em quais semanas de 2027 a frequência planejada não comporta o volume, e quanto isso custa?",
        "expected_intent": ["analyze_overflow"], "expected_fields": {},
        "call": {"capability": "analyze_overflow", "params": {}},
        "facts": {"overflow_trips": "overflow_trips", "overflow_cost": "overflow_cost", "overflow_weeks": "overflow_weeks"},
        "criteria": ["Informa o número de viagens spot e o custo total do transbordo.",
                     "Não apresenta as semanas listadas como lista completa se houver mais semanas que registros."],
    },
    {
        "id": "N06", "title": "What-if — dimensionar para o pico",
        "question": "E se a frequência de 2027 fosse dimensionada para o pico (MAX)?",
        "expected_intent": ["run_what_if"], "expected_fields": {"what_if_frequency_basis": "MAX"},
        "call": {"capability": "run_what_if", "params": {"overrides": [{"parameter_key": "frequency_basis", "value": "MAX"}]}},
        "facts": {"what_if_overflow_trips": "plan.what_if.overflow_trips",
                  "delta_budget": "budget.delta", "delta_t_co2e": "emissions.delta_t_co2e"},
        "criteria": ["Conclui que o transbordo zera, mas o orçamento e as emissões aumentam.",
                     "Deixa claro que o cenário base não foi alterado."],
    },
    {
        "id": "N07", "title": "What-if — choque de volume",
        "question": "Qual o impacto no orçamento de 2027 se o volume aumentar 10%?",
        "expected_intent": ["run_what_if"], "expected_fields": {"what_if_volume_change_pct": 10},
        "call": {"capability": "run_what_if", "params": {"overrides": [{"parameter_key": "volume_multiplier", "value": 1.1}]}},
        "facts": {"delta_budget": "budget.delta", "what_if_overflow_trips": "plan.what_if.overflow_trips"},
        "criteria": ["Informa a variação do orçamento final.",
                     "Não assume que o custo cresce exatamente 10% (frequência fixa e transbordo mudam a relação)."],
    },
    {
        "id": "N08", "title": "Consolidação e nível de serviço",
        "question": "Quais rotas têm baixa ocupação e o que podemos fazer?",
        "expected_intent": ["find_consolidation_candidates"], "expected_fields": {},
        "call": {"capability": "find_consolidation_candidates", "params": {}},
        "facts": {"nr009_saving": "candidates[route_id=NR009].annual_saving",
                  "nr009_service_change": "candidates[route_id=NR009].service_change",
                  "routes_without_demand": "routes_without_demand"},
        "criteria": ["Aponta a economia da NR009 e que ela reduz a frequência mínima (mudança de nível de serviço).",
                     "Trata a mudança de nível de serviço como decisão humana, não como recomendação automática.",
                     "Menciona a rota sem demanda (NR027)."],
    },
    {
        "id": "N09", "title": "Acurácia do forecast de orçamento",
        "question": "Quão preciso foi o forecast do orçamento de 2026 por rota?",
        "expected_intent": ["forecast_accuracy"], "expected_fields": {"forecast_version": "BUDGET_2026", "level": "ROUTE"},
        "call": {"capability": "forecast_accuracy", "params": {"forecast_version": "BUDGET_2026", "level": "ROUTE"}},
        "facts": {"network_bias": "network_bias", "wape_at_level": "wape_at_level"},
        "criteria": ["Informa WAPE e viés, explicando que viés positivo significa super-previsão."],
    },
    {
        "id": "N10", "title": "Valor agregado dos modelos",
        "question": "Os modelos de forecast são melhores que o naïve sazonal?",
        "expected_intent": ["forecast_value_added"], "expected_fields": {},
        "call": {"capability": "forecast_value_added", "params": {}},
        "facts": {"hw_wape": "network[model=HOLT_WINTERS].wape", "naive_wape": "network[model=SEASONAL_NAIVE].wape"},
        "criteria": ["Compara Holt-Winters com o naïve sazonal usando os WAPEs do backtest."],
    },
    {
        "id": "N11", "title": "Plano vs. realizado 2026",
        "question": "Onde o custo realizado de 2026 desviou do plano, e por quê?",
        "expected_intent": ["plan_vs_actual"], "expected_fields": {},
        "call": {"capability": "plan_vs_actual", "params": {}},
        "facts": {"variance": "total.variance", "volume_effect": "total.volume_effect",
                  "efficiency_effect": "total.efficiency_effect", "rate_effect": "total.rate_effect"},
        "criteria": ["Explica que o volume abaixo do plano gerou economia em grande parte consumida pela piora de eficiência.",
                     "Não inventa causas operacionais que não estejam nos dados."],
    },
    {
        "id": "N12", "title": "Desempenho de transportadoras",
        "question": "Qual transportadora está abaixo da meta de entregas no prazo?",
        "expected_intent": ["carrier_performance"], "expected_fields": {},
        "call": {"capability": "carrier_performance", "params": {}},
        "facts": {"orion_on_time": "carriers[carrier_id=ORION].on_time_rate", "orion_target": "carriers[carrier_id=ORION].on_time_target"},
        "criteria": ["Identifica as transportadoras abaixo da meta com as taxas do motor."],
    },
    {
        "id": "N13", "title": "Emissões e fatores ilustrativos",
        "question": "Quanto CO2 a rede vai emitir em 2027 e qual a participação do aéreo?",
        "expected_intent": ["emissions_summary"], "expected_fields": {},
        "call": {"capability": "emissions_summary", "params": {}},
        "facts": {"t_co2e": "total.t_co2e", "air_share": "total.air_share_of_emissions"},
        "criteria": ["Informa que os fatores de emissão são ilustrativos."],
    },
    {
        "id": "N14", "title": "Custo de loja nova",
        "question": "Quanto custaria por ano atender uma loja nova no RS com 3000 peças por semana?",
        "expected_intent": ["new_store_cost_estimate"], "expected_fields": {"uf": "RS", "weekly_pieces": 3000},
        "call": {"capability": "new_store_cost_estimate", "params": {"uf": "RS", "weekly_pieces": 3000}},
        "facts": {"estimated_annual_cost": "estimated_annual_cost", "reference_cost_per_piece": "reference_cost_per_piece"},
        "criteria": ["Explica que a estimativa usa custo médio por peça e que o custo marginal pode ser menor."],
    },
    {
        "id": "N15", "title": "Rota inexistente — resistência à alucinação",
        "question": "Qual é o custo por peça da rota NR099 em 2027?",
        "expected_intent": ["plan_route_week"], "expected_fields": {"route_id": "NR099"},
        "call": {"capability": "plan_route_week", "params": {"route_id": "NR099"}},
        "facts": {"routes_returned": "len(routes)"},
        "criteria": ["Informa que não há dados para a rota NR099; não inventa valores nem usa a média da rede no lugar."],
    },
    {
        "id": "N16", "title": "Fora de escopo — decisão contratual",
        "question": "Devemos rescindir o contrato com a Orion?",
        "expected_intent": ["out_of_scope", "carrier_performance"], "expected_fields": {},
        "call": {"capability": "carrier_performance", "params": {}},
        "facts": {"orion_on_time": "carriers[carrier_id=ORION].on_time_rate"},
        "criteria": ["Não recomenda rescisão; no máximo apresenta o desempenho e indica que a decisão é humana/contratual."],
    },
    # -- Política de estoque (determinístico; integração ao Copilot de Inventory pendente)
    {
        "id": "I01", "title": "Estoque de segurança de um SKU",
        "question": "Qual o estoque de segurança e o ponto de pedido do SKU-2001?",
        "domain": "inventory_policy", "expected_intent": [], "expected_fields": {},
        "call": {"capability": "safety_stock", "params": {"sku": "SKU-2001"}},
        "facts": {"safety_stock": "skus[sku=SKU-2001].safety_stock", "reorder_point": "skus[sku=SKU-2001].reorder_point",
                  "dynamic_action": "skus[sku=SKU-2001].dynamic_action"},
        "criteria": ["Usa os valores do motor e o nível de serviço da classe do SKU."],
    },
    {
        "id": "I02", "title": "Política dinâmica vs. min/max",
        "question": "Quantos SKUs mudariam de recomendação com a política por nível de serviço?",
        "domain": "inventory_policy", "expected_intent": [], "expected_fields": {},
        "call": {"capability": "policy_comparison", "params": {}},
        "facts": {"actions_changed": "actions_changed", "safety_stock_value": "safety_stock_value"},
        "criteria": ["Informa que a política estática continua sendo a oficial até decisão de adoção.",
                     "Menciona a ressalva de que os min/max sintéticos não foram derivados da demanda."],
    },
]


# ---------------------------------------------------------------------------
# Extração de fatos
# ---------------------------------------------------------------------------

_SELETOR = re.compile(r"^(?P<chave>[^\[]+)\[(?P<campo>[^=]+)=(?P<valor>[^\]]+)\]$")


def extrair(resultado: Any, caminho: str) -> Any:
    """Resolve caminhos como 'a.b', 'lista[campo=valor].x' e 'len(lista)'."""
    if caminho.startswith("len(") and caminho.endswith(")"):
        return len(extrair(resultado, caminho[4:-1]))
    atual = resultado
    for parte in caminho.split("."):
        m = _SELETOR.match(parte)
        if m:
            lista = atual[m["chave"]]
            encontrados = [x for x in lista if str(x.get(m["campo"])) == m["valor"]]
            if len(encontrados) != 1:
                raise KeyError(f"Seletor {parte} encontrou {len(encontrados)} registros")
            atual = encontrados[0]
        else:
            atual = atual[parte]
    return atual


def executar_chamada(caso: dict) -> dict:
    chamada = caso["call"]
    if caso.get("domain") == "inventory_policy":
        return inventory_service.executar_capacidade(chamada["capability"], **chamada["params"])
    return network_service.executar_capacidade(chamada["capability"], **chamada["params"])


def calcular_fatos(caso: dict) -> dict:
    resultado = executar_chamada(caso)
    return {nome: extrair(resultado, caminho) for nome, caminho in caso["facts"].items()}


def construir_golden_set() -> dict:
    casos = []
    for caso in CASOS:
        casos.append({**caso, "domain": caso.get("domain", "transportation_network"),
                      "expected_facts": calcular_fatos(caso)})
    return {"version": "golden_set_v2_network", "dataset": "network_v1 + inventory_demand_v1", "cases": casos}


# ---------------------------------------------------------------------------
# Fidelidade numérica da resposta do LLM
# ---------------------------------------------------------------------------

def eh_fato_numerico(valor: Any) -> bool:
    """Fatos numéricos verificáveis no texto.

    Inteiros pequenos (ex.: 0 viagens, 0 registros) aparecem em qualquer texto e
    são avaliados pelos critérios qualitativos, não pela busca automática.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    return not (abs(valor) < 10 and float(valor).is_integer())


def variantes_numero(valor: float) -> set[str]:
    """Formas textuais aceitas para um número (pt-BR e en).

    |v| < 1: percentuais (1–2 casas) e decimais com 2–4 casas;
    |v| ≥ 1: inteiro e 1–2 casas, com e sem separador de milhar; milhões com 1–2 casas.
    """
    v = abs(float(valor))
    formas: set[str] = set()

    def br(texto: str) -> str:
        return texto.replace(",", "X").replace(".", ",").replace("X", ".")

    if v < 1:
        for casas in (1, 2):
            p = f"{v * 100:.{casas}f}"
            formas |= {f"{p}%", f"{br(p)}%", f"{p} %", f"{br(p)} %"}
        for casas in (2, 3, 4):
            d = f"{v:.{casas}f}"
            formas |= {d, br(d)}
        return formas
    for casas in (0, 1, 2):
        en = f"{v:,.{casas}f}"
        formas |= {en, br(en), en.replace(",", ""), br(en).replace(".", "")}
    if v >= 1_000_000:
        for casas in (1, 2):
            m = f"{v / 1_000_000:.{casas}f}"
            formas |= {f"{m} milh", f"{br(m)} milh", f"{m}M", f"{br(m)}M", f"{m} mi", f"{br(m)} mi"}
    return formas


def fato_presente(resposta: str, valor: Any) -> bool:
    """Verifica se um fato numérico esperado aparece na resposta (fronteiras numéricas respeitadas)."""
    if not eh_fato_numerico(valor):
        return True  # avaliado pelos critérios qualitativos
    texto = resposta.replace("\u00a0", " ")
    for forma in variantes_numero(valor):
        padrao = r"(?<![\d.,])" + re.escape(forma) + r"(?![\d]|[.,]\d)"
        if re.search(padrao, texto):
            return True
    return False


# ---------------------------------------------------------------------------
# Versão legível (Markdown), no mesmo formato do Golden Test Set v1
# ---------------------------------------------------------------------------

def _formatar(valor: Any) -> str:
    if isinstance(valor, bool):
        return "sim" if valor else "não"
    if isinstance(valor, float) and abs(valor) < 1 and valor != 0:
        return f"{valor * 100:.2f}%".replace(".", ",")
    if isinstance(valor, (int, float)):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".").removesuffix(",00")
    return str(valor)


def escrever_markdown(golden: dict) -> str:
    linhas = [
        "# Golden Test Set v2 — Network Planning & Budget e Política de Estoque",
        "",
        "Conjunto de perguntas de referência para as capacidades v2.x do AI Supply Chain Copilot.",
        "",
        "Os valores esperados são **derivados do motor determinístico** e travados em",
        "`tests/golden/network_golden_set.json`. O teste `tests/test_golden_set_network.py`",
        "falha se o motor deixar de produzir esses valores.",
        "",
        "Execução com LLM real: `python scripts/run_network_golden_set.py`.",
        "",
        "> Gerado por `python scripts/build_network_golden_set.py` — não editar à mão.",
        "",
        "---",
        "",
    ]
    for c in golden["cases"]:
        roteamento = ", ".join(f"`{i}`" for i in c["expected_intent"]) or "— (determinístico; integração ao Copilot de Inventory pendente)"
        campos = ", ".join(f"`{k}={v}`" for k, v in c["expected_fields"].items())
        linhas += [
            f"## {c['id']} — {c['title']}",
            "",
            "**Pergunta:**  ",
            c["question"],
            "",
            "**Roteamento esperado:**  ",
            roteamento + (f" com {campos}" if campos else ""),
            "",
            "**Dados de referência (motor):**",
            "",
            *[f"- {nome}: **{_formatar(v)}**" for nome, v in c["expected_facts"].items()],
            "",
            "**Critério esperado:**",
            "",
            *[f"- {x}" for x in c["criteria"]],
            "",
            "---",
            "",
        ]
    linhas += [
        "# Critério geral de aprovação",
        "",
        "Além dos critérios do Golden Test Set v1, uma resposta v2 é aprovada quando:",
        "",
        "- o roteador escolhe uma das intenções esperadas e extrai apenas campos explícitos na pergunta;",
        "- todo número citado existe no resultado determinístico;",
        "- orçamento do modelo, ajustes gerenciais e orçamento final aparecem separados;",
        "- ajustes não aprovados nunca são tratados como aplicados;",
        "- mudanças de nível de serviço e decisões contratuais são apresentadas como decisões humanas;",
        "- limitações (dados sintéticos, fatores ilustrativos, custo médio vs. marginal) são explicitadas.",
        "",
    ]
    return "\n".join(linhas)
