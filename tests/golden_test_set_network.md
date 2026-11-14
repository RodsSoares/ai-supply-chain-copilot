# Golden Test Set v2 — Network Planning & Budget e Política de Estoque

Conjunto de perguntas de referência para as capacidades v2.x do AI Supply Chain Copilot.

Os valores esperados são **derivados do motor determinístico** e travados em
`tests/golden/network_golden_set.json`. O teste `tests/test_golden_set_network.py`
falha se o motor deixar de produzir esses valores.

Execução com LLM real: `python scripts/run_network_golden_set.py`.

> Gerado por `python scripts/build_network_golden_set.py` — não editar à mão.

---

## N01 — Orçamento consolidado 2027

**Pergunta:**  
Qual é o orçamento de frete de 2027 e quanto dele vem do modelo?

**Roteamento esperado:**  
`budget_summary`

**Dados de referência (motor):**

- final_budget: **13.641.069,55**
- model_budget: **13.877.391,28**
- adjustments: **-236.321,74**

**Critério esperado:**

- Informa o orçamento final e o orçamento do modelo separadamente.
- Não recalcula componentes; usa os totais do motor.

---

## N02 — Ponte de orçamento 2026 → 2027

**Pergunta:**  
Por que o orçamento de 2027 é maior que o plano de 2026?

**Roteamento esperado:**  
`budget_bridge`

**Dados de referência (motor):**

- base_final_budget: **12.734.117,96**
- target_final_budget: **13.641.069,55**
- volume_effect: **371.690,39**
- rate_effect: **854.225**
- adjustments_change: **-236.321,74**

**Critério esperado:**

- Identifica o efeito tarifa como o maior direcionador.
- Apresenta volume, eficiência, tarifa, extras, créditos e ajustes como passos da ponte.
- Não atribui causas além das presentes no resultado (ex.: não inventa motivos para o reajuste).

---

## N03 — Ajustes gerenciais e transparência

**Pergunta:**  
Quanto do orçamento de 2027 vem de ajustes da diretoria e por quê?

**Roteamento esperado:**  
`adjustment_report`

**Dados de referência (motor):**

- adjustment_share: **-1,73%**
- adj_001_impact: **-416.321,74**
- adj_002_impact: **180.000**
- adj_003_applied: **não**

**Critério esperado:**

- Separa orçamento do modelo e ajustes.
- Cita o motivo e o aprovador de cada ajuste aprovado.
- Informa que o ADJ-2027-003 está PROPOSED e não foi aplicado.

---

## N04 — Governança — ajuste não aprovado

**Pergunta:**  
Aplique o ajuste de 5% de contingência de Black Friday no orçamento de novembro de 2027.

**Roteamento esperado:**  
`adjustment_report`, `out_of_scope`

**Dados de referência (motor):**

- adj_003_status: **PROPOSED**
- adj_003_impact: **0**

**Critério esperado:**

- Não afirma ter aplicado o ajuste nem recalcula o orçamento com ele.
- Explica que o ajuste está pendente (PROPOSED) e depende de aprovação humana.

---

## N05 — Transbordo de pico

**Pergunta:**  
Em quais semanas de 2027 a frequência planejada não comporta o volume, e quanto isso custa?

**Roteamento esperado:**  
`analyze_overflow`

**Dados de referência (motor):**

- overflow_trips: **78**
- overflow_cost: **364.869,30**
- overflow_weeks: **77**

**Critério esperado:**

- Informa o número de viagens spot e o custo total do transbordo.
- Não apresenta as semanas listadas como lista completa se houver mais semanas que registros.

---

## N06 — What-if — dimensionar para o pico

**Pergunta:**  
E se a frequência de 2027 fosse dimensionada para o pico (MAX)?

**Roteamento esperado:**  
`run_what_if` com `what_if_frequency_basis=MAX`

**Dados de referência (motor):**

- what_if_overflow_trips: **0**
- delta_budget: **514.736,24**
- delta_t_co2e: **111,30**

**Critério esperado:**

- Conclui que o transbordo zera, mas o orçamento e as emissões aumentam.
- Deixa claro que o cenário base não foi alterado.

---

## N07 — What-if — choque de volume

**Pergunta:**  
Qual o impacto no orçamento de 2027 se o volume aumentar 10%?

**Roteamento esperado:**  
`run_what_if` com `what_if_volume_change_pct=10`

**Dados de referência (motor):**

- delta_budget: **1.473.546,91**
- what_if_overflow_trips: **106**

**Critério esperado:**

- Informa a variação do orçamento final.
- Não assume que o custo cresce exatamente 10% (frequência fixa e transbordo mudam a relação).

---

## N08 — Consolidação e nível de serviço

**Pergunta:**  
Quais rotas têm baixa ocupação e o que podemos fazer?

**Roteamento esperado:**  
`find_consolidation_candidates`

**Dados de referência (motor):**

- nr009_saving: **87.929,13**
- nr009_service_change: **LOWER_MIN_FREQUENCY**
- routes_without_demand: **['NR027']**

**Critério esperado:**

- Aponta a economia da NR009 e que ela reduz a frequência mínima (mudança de nível de serviço).
- Trata a mudança de nível de serviço como decisão humana, não como recomendação automática.
- Menciona a rota sem demanda (NR027).

---

## N09 — Acurácia do forecast de orçamento

**Pergunta:**  
Quão preciso foi o forecast do orçamento de 2026 por rota?

**Roteamento esperado:**  
`forecast_accuracy` com `forecast_version=BUDGET_2026`, `level=ROUTE`

**Dados de referência (motor):**

- network_bias: **3,10%**
- wape_at_level: **8,90%**

**Critério esperado:**

- Informa WAPE e viés, explicando que viés positivo significa super-previsão.

---

## N10 — Valor agregado dos modelos

**Pergunta:**  
Os modelos de forecast são melhores que o naïve sazonal?

**Roteamento esperado:**  
`forecast_value_added`

**Dados de referência (motor):**

- hw_wape: **10,21%**
- naive_wape: **11,50%**

**Critério esperado:**

- Compara Holt-Winters com o naïve sazonal usando os WAPEs do backtest.

---

## N11 — Plano vs. realizado 2026

**Pergunta:**  
Onde o custo realizado de 2026 desviou do plano, e por quê?

**Roteamento esperado:**  
`plan_vs_actual`

**Dados de referência (motor):**

- variance: **-79.575,95**
- volume_effect: **-280.419,71**
- efficiency_effect: **212.157,60**
- rate_effect: **-11.313,84**

**Critério esperado:**

- Explica que o volume abaixo do plano gerou economia em grande parte consumida pela piora de eficiência.
- Não inventa causas operacionais que não estejam nos dados.

---

## N12 — Desempenho de transportadoras

**Pergunta:**  
Qual transportadora está abaixo da meta de entregas no prazo?

**Roteamento esperado:**  
`carrier_performance`

**Dados de referência (motor):**

- orion_on_time: **86,55%**
- orion_target: **95,00%**

**Critério esperado:**

- Identifica as transportadoras abaixo da meta com as taxas do motor.

---

## N13 — Emissões e fatores ilustrativos

**Pergunta:**  
Quanto CO2 a rede vai emitir em 2027 e qual a participação do aéreo?

**Roteamento esperado:**  
`emissions_summary`

**Dados de referência (motor):**

- t_co2e: **2.502,33**
- air_share: **29,62%**

**Critério esperado:**

- Informa que os fatores de emissão são ilustrativos.

---

## N14 — Custo de loja nova

**Pergunta:**  
Quanto custaria por ano atender uma loja nova no RS com 3000 peças por semana?

**Roteamento esperado:**  
`new_store_cost_estimate` com `uf=RS`, `weekly_pieces=3000`

**Dados de referência (motor):**

- estimated_annual_cost: **80.875,15**
- reference_cost_per_piece: **51,84%**

**Critério esperado:**

- Explica que a estimativa usa custo médio por peça e que o custo marginal pode ser menor.

---

## N15 — Rota inexistente — resistência à alucinação

**Pergunta:**  
Qual é o custo por peça da rota NR099 em 2027?

**Roteamento esperado:**  
`plan_route_week` com `route_id=NR099`

**Dados de referência (motor):**

- routes_returned: **0**

**Critério esperado:**

- Informa que não há dados para a rota NR099; não inventa valores nem usa a média da rede no lugar.

---

## N16 — Fora de escopo — decisão contratual

**Pergunta:**  
Devemos rescindir o contrato com a Orion?

**Roteamento esperado:**  
`out_of_scope`, `carrier_performance`

**Dados de referência (motor):**

- orion_on_time: **86,55%**

**Critério esperado:**

- Não recomenda rescisão; no máximo apresenta o desempenho e indica que a decisão é humana/contratual.

---

## I01 — Estoque de segurança de um SKU

**Pergunta:**  
Qual o estoque de segurança e o ponto de pedido do SKU-2001?

**Roteamento esperado:**  
— (determinístico; integração ao Copilot de Inventory pendente)

**Dados de referência (motor):**

- safety_stock: **47**
- reorder_point: **127**
- dynamic_action: **REPOR**

**Critério esperado:**

- Usa os valores do motor e o nível de serviço da classe do SKU.

---

## I02 — Política dinâmica vs. min/max

**Pergunta:**  
Quantos SKUs mudariam de recomendação com a política por nível de serviço?

**Roteamento esperado:**  
— (determinístico; integração ao Copilot de Inventory pendente)

**Dados de referência (motor):**

- actions_changed: **101**
- safety_stock_value: **6.687.395,43**

**Critério esperado:**

- Informa que a política estática continua sendo a oficial até decisão de adoção.
- Menciona a ressalva de que os min/max sintéticos não foram derivados da demanda.

---

# Critério geral de aprovação

Além dos critérios do Golden Test Set v1, uma resposta v2 é aprovada quando:

- o roteador escolhe uma das intenções esperadas e extrai apenas campos explícitos na pergunta;
- todo número citado existe no resultado determinístico;
- orçamento do modelo, ajustes gerenciais e orçamento final aparecem separados;
- ajustes não aprovados nunca são tratados como aplicados;
- mudanças de nível de serviço e decisões contratuais são apresentadas como decisões humanas;
- limitações (dados sintéticos, fatores ilustrativos, custo médio vs. marginal) são explicitadas.
