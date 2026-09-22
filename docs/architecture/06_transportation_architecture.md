Transportation Analytics Architecture

Document: 06_transportation_architecture.md Project: AI Supply Chain
Copilot Status: Phase 0 --- CLOSED / Bounded Transportation Extension Last
updated: 2026-09-20

Purpose

Transportation is a bounded analytics extension of the existing AI
Supply Chain Copilot.

Its purpose is to:

strengthen advanced SQL skills through realistic Supply Chain problems;

rebuild classes of transportation-planning problems previously
encountered professionally using 100% synthetic data;

demonstrate a strong deterministic analytics layer;

prove that the Copilot architecture can support a second Supply Chain
domain without breaking Inventory;

expose Transportation analytics through compatible API/tool contracts;

allow the LLM layer to interpret deterministic analytical results in
business language.

Transportation is not intended to become a standalone product.

Transportation is an analytics extensibility case, not a transportation
optimization product.

The target portfolio narrative is:

I took classes of transportation-planning problems I had solved
professionally and rebuilt them with a modern analytics architecture
using fully synthetic data, then integrated those capabilities into an
existing AI Supply Chain Copilot to demonstrate architectural
extensibility.

Clean-Room and Confidentiality Rules

This project must reconstruct the problem class, not any previous
proprietary implementation.

Allowed

generic transportation-planning concepts;

generic Supply Chain domain knowledge;

analytical reasoning;

synthetic planning rules;

synthetic entities and datasets;

independently designed formulas and schemas;

public/common KPIs and analytical techniques.

Prohibited

Do not expose or reproduce:

former employer names in the public project;

real operational data;

real routes;

real distribution centers or stores;

real carriers;

real tariffs or costs;

real volumes;

real identifiers;

proprietary commercial rules;

copied formulas or spreadsheet logic;

confidential operating constraints.

Core rule:

Rebuild the problem, not the spreadsheet.

The goal is not historical reproduction. It is to create a credible
synthetic analytical domain inspired by real classes of planning
problems.

Scope

The Transportation domain will cover a bounded planning and analytics
chain:

Forecast Demand ↓ Route Characteristics ↓ Planning Policy ↓ Vehicle /
Capacity Choice ↓ Required Trips ↓ Capacity Utilization ↓ Transportation
Cost ↓ R$/Piece ↓ Plan vs Actual ↓ Variance / Driver Analysis ↓
Prioritization

The emphasis is on analytics and decision support, not mathematical
optimization.

Architectural Position

Transportation becomes a second analytical domain inside the existing
Copilot.

Data / Synthetic ERP ↓ Canonical Data Layer ↓ Decision / Analytics Layer
├── Inventory └── Transportation ↓ API / Tool Contracts ↓ LLM / Copilot

For natural-language analytical questions:

User Question ↓ LLM Intent / Tool Selection ↓ Transportation Analytical
Tool ↓ SQL / Deterministic Analytics ↓ Structured Result ↓ LLM
Interpretation ↓ Business Answer

Core architectural rule

LLM ≠ Calculator.

Authoritative calculations belong to SQL and deterministic analytics.

The LLM may:

identify intent;

select tools;

synthesize results;

explain drivers;

translate analytical output into business language.

The LLM must not become the source of truth for KPI calculations.

Planning Policy v0

The Transportation planning model uses a deliberately simplified,
synthetic policy.

It captures enough business realism to generate meaningful analytical
problems without attempting to reproduce a historical operation.

5.1 Service Frequency

The planning preference is to serve each destination:

at least 2 times per week whenever economically reasonable.

This is a target, not an absolute hard constraint.

If maintaining two deliveries per week is economically unjustifiable for
a specific demand/route configuration, a lower frequency may be
accepted.

5.2 Short Routes

For short routes, the policy generally favors smaller vehicles.

Business rationale:

increase delivery frequency;

improve replenishment flexibility;

support more frequent destination service;

accept that this may produce a somewhat higher transportation cost per
piece.

Therefore:

Short route → frequency/flexibility receives greater weight.

5.3 Long Routes

For long routes, the policy generally favors larger vehicles.

Business rationale:

exploit vehicle capacity;

spread trip cost across more units;

reduce transportation cost per piece;

capture scale benefits on longer movements.

Therefore:

Long route → scale/unit economics receives greater weight.

5.4 Economic Exception

The target service frequency may be relaxed when the incremental
transportation cost is not economically justified.

For the MVP, this exception will be implemented using a simple,
explicit, synthetic and testable rule.

The project does not attempt to discover or recreate the exact
historical decision rule.

5.5 Non-Linear Vehicle Economics

Vehicle capacity and trip cost do not increase proportionally.

A larger vehicle may carry substantially more volume without costing
proportionally more because transportation contains cost components that
do not scale linearly with vehicle capacity.

Therefore, vehicle selection cannot be modeled as:

cost ∝ capacity

Instead, each route/vehicle combination has its own synthetic tariff.

5.6 Trips Are Derived

planned_trips is not an arbitrary primary planning input.

It is derived from:

forecast demand;

vehicle capacity;

route characteristics;

target frequency;

vehicle selection;

economic feasibility rules.

A simplified conceptual relationship is:

Forecast + Route + Vehicle Capacity + Service Policy + Route/Vehicle
Tariff ↓ Vehicle Configuration ↓ Planned Trips

planned_trips may be materialized in the plan for analytics, but it
remains a derived planning output.

Planning Policy vs Optimization

The MVP must not evolve into a vehicle-routing or fleet-optimization
engine.

The Planning Policy exists primarily to produce a realistic and
explainable planning scenario.

Conceptually:

Forecast ↓ Route Characteristics ↓ Eligible / Preferred Vehicle Logic ↓
Target Service Frequency ↓ Economic Feasibility ↓ Vehicle + Trips ↓
Capacity Utilization ↓ Planned Cost ↓ R$/Piece

The analytical system can compare valid alternatives, but the objective
is not to build a globally optimal mathematical transportation plan.

A lower-cost configuration is not automatically the correct
configuration if it violates the synthetic service policy.

PLAN and ACTUAL

The model explicitly separates planned and realized operations.

PLAN

Generated from:

demand forecast;

route characteristics;

vehicle capacities;

route/vehicle tariffs;

Planning Policy v0.

Produces analytical outputs such as:

selected vehicle;

planned trips;

planned capacity;

planned utilization;

planned transportation cost;

planned R$/piece.

ACTUAL

Represents synthetic realized operations:

actual transported pieces;

actual trips;

actual transportation cost;

potentially actual vehicle configuration where required.

This separation enables:

Plan vs Actual analytics

including volume, trip, utilization and cost variances.

Current Synthetic Data Model

The implemented model remains deliberately small and uses the grain
required by each business process.

routes

route_id origin_id destination_id distance_km

route_profile is NOT persisted. It is deterministically derived from
distance_km by Planning Policy v0:

SHORT: distance < 300 km

MEDIUM: 300 <= distance <= 800 km

LONG: distance > 800 km

vehicle_types

vehicle_type_id vehicle_name capacity_pieces

route_vehicle_options

route_id vehicle_type_id

This table represents valid route/vehicle combinations. Eligibility is
separate from pricing.

route_vehicle_rates

route_id vehicle_type_id effective_from effective_to rate_per_trip

The temporal fields allow synthetic tariff changes without redesigning
the schema. The current synthetic dataset has one active rate per
route/vehicle combination; temporal rate selection must be enforced
before historical rate versions are introduced.

forecast_raw

year week route_id forecast_pieces

Grain: ISO year x week x route.

demand_forecast

week_start route_id forecast_pieces

Grain: route x week. week_start is the ISO-week Monday produced by ETL.

planned_trips

trip_id week_start route_id vehicle_type_id planned_pieces
planned_capacity planned_cost

Grain: one row = one planned trip. Frequency is derived with
COUNT(trip_id) rather than stored redundantly. Weekly capacity and cost
are reconstructed with aggregation.

Current deterministic trip materialization rules:

trip_id is deterministic, e.g. 20260824-R001-01;

forecast pieces are distributed as evenly as possible across trips;

the difference between trip piece counts is at most one piece;

SUM(planned_pieces) = forecast_pieces;

planned_capacity and planned_cost are stored at individual-trip grain.

A separate physical transport_plan table is not required at this stage.
Weekly plan outputs can be reconstructed from planned_trips through
SQL/views.

transport_actual has not yet been implemented. It belongs to the later
bounded Plan-vs-Actual step and should only be introduced when required
by that business question.

Core Planning Calculations

For a candidate vehicle configuration:

Capacity-Driven Trips

[ Trips_{capacity} = \left{=tex}{=tex}\lceil{=tex}{=tex}
\frac{ForecastPieces}{VehicleCapacity}{=tex}{=tex}
\right{=tex}{=tex}\rceil{=tex}{=tex} ]

Offered Capacity

[ OfferedCapacity = PlannedTrips \times {=tex}{=tex}VehicleCapacity
]

Capacity Utilization

[ Utilization = \frac{ForecastPieces}{OfferedCapacity}{=tex}{=tex} ]

Planned Transportation Cost

[ PlannedCost = PlannedTrips \times {=tex}{=tex}RatePerTrip ]

Cost per Piece

[ R$/Piece =
\frac{TransportationCost}{TransportedPieces}{=tex}{=tex} ]

These formulas are deterministic and must be tested independently of the
LLM.

The final number of planned trips may also reflect the target service
frequency and economic-exception rule.

Why R$/Piece Is a Core KPI

R$/Piece is not a cosmetic metric.

It normalizes transportation spending by transported volume and answers
an important executive question:

Did transportation cost increase because we moved more volume, or
because transporting each unit became more expensive?

For example:

cost +15%, pieces +20% → R$/piece decreases → unit economics improved;

cost +15%, pieces +5% → R$/piece increases → unit economics
deteriorated;

cost +15%, pieces +15% → R$/piece approximately stable → increase is
largely volume-driven.

R$/piece is therefore a protagonist of the Transportation analytical
layer.

Cost Variance Decomposition

Let:

[ C = V \times {=tex}{=tex}U ]

where:

C = transportation cost;

V = transported pieces;

U = transportation cost per piece.

Between period 0 and period 1:

Volume Effect

[ VolumeEffect = (V_1 - V_0) \times {=tex}{=tex}U_0 ]

Unit Cost Effect

[ UnitCostEffect = V_1 \times {=tex}{=tex}(U_1 - U_0) ]

Reconciliation

[ \Delta {=tex}{=tex}Cost = VolumeEffect + UnitCostEffect ]

Example:

January 1,000,000 pieces × R$0.50 = R$500,000

February 1,200,000 pieces × R$0.55 = R$660,000

Cost change = +R$160,000 Volume effect = +R$100,000 Unit-cost effect =
+R$60,000

Interpretation:

R$100k of the increase came from additional transported volume;

R$60k came from deterioration in transportation cost per piece.

This decomposition should remain simple, transparent and explainable.

Driver Hierarchy

The analytical hierarchy should distinguish detection from diagnosis.

BQ-00 --- What operation is required for the forecast?

Forecast → Vehicle / Capacity → Trips → Utilization → Cost → R$/Piece

BQ-01 --- Why did transportation cost change?

Primary decomposition:

Cost Change ├── Volume Effect └── Unit-Cost Effect

BQ-02 --- Why did R$/Piece change?

Potential diagnostic drivers:

R$/Piece ├── route/vehicle tariff ├── capacity utilization ├── trips /
service frequency ├── vehicle mix ├── route mix └── volume crossing a
capacity threshold

The MVP should avoid claiming causal precision beyond what the
deterministic data supports.

The objective is explainable driver analysis, not an unnecessarily
complex causal model.

Capacity Threshold Effect

Transportation cost can behave discontinuously.

Example:

Vehicle capacity: 10,000 pieces Rate per trip: R$3,000

For 9,900 pieces:

1 trip Cost = R$3,000
R$/piece ≈ R$0.303

For 10,100 pieces:

2 trips Cost = R$6,000
R$/piece ≈ R$0.594

A small increase in volume can therefore create a large cost increase
when demand crosses a capacity threshold.

This illustrates why:

volume change alone does not explain transportation cost behavior.

The analytical layer should be able to distinguish volume growth from
operational effects such as additional trips and lower utilization.

Canonical Business Questions

The dataset and SQL exercises should be driven by business questions
rather than isolated syntax drills.

Demand and Capacity

What is the forecast volume by route and period?

How many trips are required to serve forecast demand?

What capacity will be offered?

What is expected capacity utilization by route?

Which routes are approaching capacity thresholds?

Which routes are persistently underutilized?

Which routes require additional trips after relatively small demand
changes?

Is route demand increasing or decreasing?

Service Policy

Which destinations achieve the target service frequency?

Where does maintaining target frequency materially increase R$/piece?

Which routes operate below target frequency because of economic rules?

Are short routes achieving the intended higher-frequency profile?

Are long routes capturing expected scale benefits?

Cost and Budget

What is projected transportation spend?

Which routes account for the largest share of transportation cost?

Which routes have the fastest cost growth?

Which routes show deteriorating R$/piece?

How much of cost growth comes from volume versus unit-cost
deterioration?

Which routes drive the largest share of total cost variance?

Did a tariff change materially affect a route?

Where is low utilization increasing unit cost?

Plan vs Actual

Where is actual volume diverging from forecast?

Where are actual trips above plan?

Where is actual utilization worse than planned?

Which routes generate unfavorable cost variance?

Are deviations isolated or persistent?

Prioritization

Capstone question:

Which routes should be prioritized for operational review in the next
period, and why?

Candidate analytical output:

route_id forecast_volume planned_trips capacity_utilization planned_cost
cost_per_piece cost_change_pct cost_per_piece_change_pct
utilization_change network_cost_share priority_rank

Prioritization logic must remain transparent and explainable.

Advanced SQL Learning Objectives

Phase 0 uses Transportation as a vehicle for learning SQL through
realistic analytical problems.

Target concepts:

JOIN;

GROUP BY;

SUM, AVG, COUNT;

conditional aggregation;

CASE WHEN;

subqueries where useful;

CTEs;

chained CTEs;

ROW_NUMBER();

RANK() / DENSE_RANK();

LAG() / LEAD();

SUM() OVER(...);

AVG() OVER(...);

rolling averages;

temporal comparisons;

cumulative calculations;

network-share calculations;

plan-vs-actual variance analysis;

basic index reasoning;

query-plan awareness;

avoiding unnecessary scans.

Core learning principle:

Business Question → Analytical Reasoning → SQL Technique

Not:

SQL Technique → Artificial Exercise

The target is approximately 10--15 high-quality business queries, not a
large collection of generic exercises.

SQL Learning Progression

A single business problem may evolve through increasingly advanced SQL.

Level 1 --- Aggregation

Question:

What is forecast volume by route and period?

Concepts:

JOIN GROUP BY SUM

Level 2 --- Capacity

Question:

How many trips does each candidate vehicle require?

Concepts:

JOIN division rounding / ceiling logic business rules

Level 3 --- Utilization and Cost

Question:

What utilization, planned cost and R$/piece result from each
configuration?

Concepts:

derived metrics CASE multiple joins

Level 4 --- Temporal Comparison

Question:

How did cost and R$/piece change versus the previous period?

Concept:

LAG()

Level 5 --- Trend

Question:

Is deterioration temporary or persistent?

Concepts:

AVG() OVER(...) rolling windows

Level 6 --- Contribution and Prioritization

Question:

Which routes explain the network variance and deserve attention first?

Concepts:

chained CTEs CASE SUM() OVER(...) RANK() multiple KPIs

The capstone should combine several of these concepts in one explainable
analytical flow.

SQL Exit Criterion

Phase 0 SQL is considered sufficient when the user can independently
reason through:

Business Problem ↓ Required Grain ↓ Required Tables ↓ Joins ↓
Aggregation ↓ Window / Temporal Comparison ↓ Business Rule ↓ Analytical
Result ↓ Business Interpretation

The objective is not memorizing syntax.

The user should be able to explain:

why the query has its chosen grain;

why each join exists;

why a window function is needed;

how the business rule is represented;

what the output means operationally;

what the query does not prove.

Candidate Transportation Analytical Tools

Names are provisional and should only be implemented when supported by
completed deterministic analytics.

Potential tools:

analyze_transport_cost_variance(...) rank_transport_cost_drivers(...)
analyze_capacity_utilization(...) forecast_route_capacity(...)
rank_cost_per_piece_deterioration(...) analyze_plan_vs_actual(...)

Example structured output:

{ "cost_change_pct": 18.4, "volume_change_pct": 12.1,
"cost_per_piece_change_pct": 5.6, "volume_effect": 420000,
"unit_cost_effect": 190000 }

The LLM receives structured analytical results and produces a business
explanation.

Tool contracts should remain stable, explicit and testable.

Testing Strategy

Testing precedes trust in LLM interpretation.

Deterministic Analytics

Test:

trip calculations;

capacity calculations;

utilization;

transportation cost;

R$/piece;

cost variance decomposition;

plan-vs-actual calculations;

ranking/prioritization rules.

Edge Cases

Include cases such as:

zero volume;

missing tariff;

unavailable vehicle for route;

capacity threshold crossing;

low utilization;

frequency-policy exception;

tariff effective-date boundary;

first period with no previous-period comparison.

Tool Contracts

Test:

expected schema;

required fields;

types;

deterministic values;

error behavior.

Regression

Transportation integration must not silently alter Inventory behavior.

Preferred workflow:

python -m pytest <target>{=html} -q python -m pytest -q

A plausible LLM explanation is not evidence that the analytical
calculation is correct.

Optional GHG Extension

Environmental impact existed as a dimension in the broader class of
transportation-planning problems.

A future bounded extension may use synthetic data such as:

distance;

vehicle category;

fuel consumption;

emission factor;

estimated emissions.

This could enable a question such as:

How do candidate transportation decisions compare on cost and estimated
environmental impact?

However:

GHG is not part of the Phase 0 minimum exit criterion.

It must not delay:

advanced SQL completion;

deterministic Transportation analytics;

Copilot integration;

transition to the next roadmap phase.

Explicit Non-Goals

Transportation must not become:

a standalone SaaS;

a full TMS;

a route optimizer;

a vehicle-routing optimization engine;

a carrier marketplace;

a real-time tracking platform;

a digital twin;

a new agentic product;

a large frontend project;

a reason to refactor the entire Copilot;

a separate repository without a strong technical reason;

an exhaustive logistics KPI research project;

a reconstruction of a previous employer's proprietary planning model.

Interesting adjacent ideas go to the backlog.

Scope-Control Rule

The development path is:

Synthetic Transportation Problem ↓ Advanced SQL ↓ Deterministic
Analytics + Tests ↓ Copilot Integration ↓ LLM / Tool Calling ↓
Extensibility Demonstrated ↓ STOP

Any adjacent idea that is not necessary for this chain:

Good Idea ↓ BACKLOG ↓ Continue Current Scope

The word STOP is intentional.

Transportation exists to complete Phase 0, not to delay the broader
career roadmap.

Relationship to Career Roadmap

Transportation is Phase 0.

After its bounded completion:

Phase 1

Bounded refactor of My LinkedIn Agentic AI System to consolidate:

agentic architecture;

LangGraph;

state;

contracts;

structured outputs;

tool calling;

routing;

human-in-the-loop;

testing.

Phase 2

Practical RAG:

ingestion;

parsing;

chunking;

metadata;

embeddings;

vector store;

retrieval;

grounding;

hybrid retrieval / reranking when justified.

Phase 3

Evals + Observability:

golden dataset;

retrieval evaluation;

generation evaluation;

regression;

tracing;

latency;

token usage;

cost;

one observability platform.

Active job applications should not wait for mastery of every later
topic.

Portfolio Value

The value of this extension is not the number of features.

It demonstrates a combination of:

Business Reasoning + Supply Chain Domain Knowledge + Data Modeling +
Advanced SQL + Deterministic Analytics + Testing + API / Tool
Contracts + LLM Interpretation + Software Extensibility

The desired architectural story is:

Historical approach Business Problem → Planning Model → Advanced
Spreadsheet → Analytical Decision Support

Modern reconstruction Business Problem → Synthetic Canonical Data → SQL
Analytics → Deterministic Decision Support → API / Tool → LLM
Interpretation

The technology changes.

The underlying ability to structure and solve complex business problems
remains central.

Design Principles

Business question before SQL syntax.

Rebuild the problem, not the spreadsheet.

Synthetic data only.

LLM ≠ Calculator.

Deterministic analytics before natural-language interpretation.

Context ≠ Policy.

PLAN and ACTUAL are distinct.

R$/Piece is a core normalization KPI.

Explain cost variance; do not merely report it.

Vehicle economics are non-linear.

Trips are derived from planning decisions.

Service frequency is a business trade-off, not merely a capacity
calculation.

Short routes favor frequency/flexibility; long routes favor scale/unit
economics.

Planning Policy exists to support analytics, not to become an
optimization product.

Prove extensibility by adding Transportation without breaking Inventory.

Tests before trusting AI interpretation.

Concept before code.

Finish bounded scope before adjacent capabilities.

Portfolio value = business reasoning + architecture, not feature count.

First Development Sequence

With architecture and scope frozen, implementation should proceed in
this order:

Create minimal synthetic schema

Create small deterministic synthetic dataset

Validate planning-policy calculations

Start business-question-driven SQL exercises

Progress from aggregation to advanced analytical SQL

Implement deterministic Transportation analytics

Add tests

Expose selected analytics through Copilot-compatible contracts

Integrate LLM/tool calling

Run Inventory + Transportation regression

Document demonstrated extensibility

STOP

Documentation should not become the work itself.

After this architecture document is accepted, the emphasis moves to
implementation and learning.

Current Implementation Checkpoint --- 2026-09-20

This section is the authoritative handoff point for resuming development.
Earlier sections preserve the target architecture, learning rationale and
historical design space. This section records what is actually implemented
now and the bounded sequence that remains.

Repository and environment

Repository: ai-supply-chain-copilot

Default environment: Windows + PowerShell + project-local .venv

Test command convention: always python -m pytest; never bare pytest.

Database: database/supply_chain.db

Inventory ETL lives under src/etl/inventory/.

Transportation ETL lives under src/etl/transportation/.

Transportation deterministic analytics live under
src/analytics/transportation/.

Preferred development workflow:

concept -> implementation -> targeted test -> full regression at meaningful
cross-cutting checkpoints

Productivity rule:

Do not reopen completed SQL exercises or expand Transportation with adjacent
capabilities unless a concrete requirement is necessary to complete the
bounded Copilot integration and Phase 0 exit.

Implemented Transportation data

The synthetic master-data and forecast pipeline are implemented and loaded.

Current Transportation tables:

routes

vehicle_types

route_vehicle_options

route_vehicle_rates

forecast_raw

demand_forecast

planned_trips

Current synthetic dataset:

12 routes;

5 vehicle types;

32 valid route/vehicle combinations;

32 synthetic route/vehicle rates;

96 weekly forecast rows = 12 routes x 8 weeks;

forecast window: 2026-08-24 through 2026-10-12.

SQLite foreign-key enforcement is enabled centrally by the application
connection with:

PRAGMA foreign_keys = ON

transport_actual has not been implemented at this checkpoint.

Implemented planning flow

Weekly Route Forecast
-> Route Context
-> Eligible Vehicles + Synthetic Rates
-> Planning Alternatives
-> Capacity Requirement + Service Target
-> Economic Scenario + Service Scenario
-> Service Premium
-> Economic Baseline Selection
-> Selected Weekly Plan
-> Individual Planned Trips
-> SQLite Persistence

Implemented policy/decision functions include:

classificar_perfil_rota(...)

obter_frequencia_alvo(...)

calcular_viagens_necessarias(...)

calcular_viagens_por_capacidade(...)

calcular_metricas_alternativa(...)

calcular_cenarios_planejamento(...)

selecionar_alternativa(...)

gerar_viagens_planejadas(...)

Implemented planning analytics/orchestration functions include:

buscar_alternativas_veiculo(...)

analisar_alternativas_planejamento(...)

analisar_cenarios_planejamento(...)

selecionar_plano(...)

gerar_plano_planejado(...)

salvar_viagens_planejadas(...)

materializar_plano_completo()

The current selection baseline chooses the lowest cost_per_piece, with
explicit deterministic tie-breaks. It remains an ECONOMIC BASELINE.

The economic-vs-service analysis remains intentionally parallel to the
existing selection flow and does not silently change the selected weekly
plan.

Resolved semantic issue: Capacity Requirement != Service Target

Capacity Requirement answers:

How many trips are physically required for the forecast and vehicle
capacity?

Service Target answers:

How many trips would the service policy prefer?

calcular_viagens_por_capacidade(...) represents the physical minimum.

calcular_cenarios_planejamento(...) exposes two deterministic scenarios for
each candidate vehicle.

Economic scenario:

trips = minimum required by capacity;

offered capacity;

utilization;

planned cost;

R$/Piece.

Service scenario:

trips = max(capacity-required trips, target service frequency);

offered capacity;

utilization;

planned cost;

R$/Piece.

The explicit service premium is:

service_premium = (service_cost_per_piece / economic_cost_per_piece) - 1

The service premium quantifies the incremental unit cost required to buy the
preferred service frequency instead of operating only at the physical
capacity minimum.

The current architecture deliberately does not convert this metric into an
arbitrary tolerance rule.

Plan materialization

The complete synthetic weekly plan is materialized through:

materializar_plano_completo()

The materialization reads all route-week forecast combinations, generates the
selected individual trips, clears the previous derived plan and persists the
regenerated plan.

planned_trips remains a derived planning output.

Current materialized checkpoint:

192 planned trips;

96 route-week plans;

1,997,400 planned pieces;

2,718,000 pieces of offered capacity;

R$778,000 planned transportation cost;

zero forecast-versus-plan reconciliation divergences.

Materialization is intentionally idempotent for this derived planning layer.

Running the same materialization again must reproduce the same final state
rather than accumulate duplicate trips.

This DELETE + rebuild behavior is appropriate for the current derived
planning output. It must not be generalized to historical ACTUAL data.

Advanced SQL checkpoint: COMPLETE for current Phase 0 scope

The implemented analytical module is:

src/analytics/transportation/sql_analysis.py

It contains ten deterministic analytical capabilities covering BQ-00 through
BQ-09:

BQ-00 -> analisar_operacao_forecast()

BQ-01 -> analisar_eficiencia_economica()

BQ-02 -> analisar_evolucao_semanal()

BQ-03 -> analisar_participacao_custo_rede()

BQ-04 -> analisar_ranking_custo_semanal()

BQ-05 -> analisar_concentracao_custo_rede()

BQ-06 -> analisar_tendencia_recente()

BQ-07 -> analisar_mudancas_operacionais()

BQ-08 -> analisar_pressao_custo_rede()

BQ-09 -> analisar_resumo_executivo_semanal()

The Advanced SQL learning block is considered COMPLETE for the current
bounded Transportation scope.

No BQ-10 or additional SQL exercise should be added merely to increase query
count. New SQL should only be introduced if a concrete integration
requirement makes it necessary.

Golden analytical case: R001 capacity-threshold transition

Week 2026-10-05:

forecast: 9,700 pieces;

selected configuration: 2 x LIGHT_TRUCK;

vehicle capacity: 5,000 pieces each;

offered capacity: 10,000 pieces;

planned cost: R$1,700;

utilization: 97%;

cost per piece: approximately R$0.1753.

Week 2026-10-12:

forecast: 10,300 pieces;

selected configuration: 2 x MEDIUM_TRUCK;

vehicle capacity: 10,000 pieces each;

offered capacity: 20,000 pieces;

planned cost: R$2,300;

utilization: 51.5%;

cost per piece: approximately R$0.2233.

Deterministic causal chain supported by the planning data:

Forecast: 9,700 -> 10,300 (+600)
-> previous 10,000-piece offered capacity is no longer sufficient
-> selected plan changes from 2 LIGHT_TRUCKS to 2 MEDIUM_TRUCKS
-> offered capacity: 10,000 -> 20,000
-> utilization: 97% -> 51.5%
-> planned cost: R$1,700 -> R$2,300
-> R$/Piece: ~0.1753 -> ~0.2233

The LLM must not independently recalculate these authoritative values.

AI / Copilot multidomain integration: IMPLEMENTED

The Copilot now supports Inventory and Transportation as separate analytical
domains without asking the LLM to choose between them.

Domain-selection rule

The domain is selected explicitly by the calling layer / frontend.

The LLM must NOT decide whether a question belongs to Inventory or
Transportation when the user interface already provides that information.

This preserves deterministic application behavior, avoids unnecessary token
usage and prevents an LLM call from solving a routing problem already solved
by the UI.

Compact rule:

UI defines the domain.
LLM interprets the intent inside the selected domain.
Dispatcher selects the authorized deterministic capability.
SQL calculates.
Analytics detects.
AI explains.
Human decides.

This extends, rather than replaces, the core rule:

LLM != Calculator.

Current AI structure

src/
ai/
client.py
inventory_context.py
prompts.py
service.py
tools.py
transportation_context.py
transportation_dispatcher.py
transportation_router.py

The previous src/ai/context.py has been renamed to:

src/ai/inventory_context.py

This makes the Inventory-specific responsibility explicit and leaves the AI
layer structurally ready for multiple domains.

Prompts

src/ai/prompts.py now separates:

SYSTEM_PROMPT

INVENTORY_PROMPT

TRANSPORTATION_PROMPT

SYSTEM_PROMPT contains global Copilot behavior and the rule that deterministic
engines remain authoritative for calculations and classifications.

INVENTORY_PROMPT contains Inventory-specific interpretation rules.

TRANSPORTATION_PROMPT contains Transportation planning scope and requires the
LLM to interpret deterministic analytical results without recalculating trips,
capacity, cost or detected operational events.

Structured Output capability

src/ai/client.py now supports structured LLM responses using Pydantic models.

The Transportation router uses this capability to transform an open-ended
natural-language question into a constrained analytical intent.

Structured Output is intentionally not simulated with heuristic fake routing.
In fake mode, the structured-output client raises an explicit RuntimeError;
router behavior is tested by monkeypatching the structured response at the
router boundary.

Transportation Router

Implemented in:

src/ai/transportation_router.py

The router is the probabilistic interpretation boundary.

It receives the original Transportation question and maps potentially
unbounded natural-language phrasing into one of a finite set of configured
analytical capabilities.

Current intent contract:

network_overview

economic_efficiency

weekly_evolution

cost_share

cost_ranking

cost_concentration

recent_trend

operational_changes

cost_pressure

executive_summary

out_of_scope

The structured model also supports:

route_id: str | None

The ten analytical intents correspond to the completed deterministic
Transportation capabilities. They are the configured analytical questions /
capabilities available to the Copilot; they are not calculations performed by
the LLM.

out_of_scope is a mandatory guardrail.

If a question cannot be answered by one of the available Transportation
capabilities, the router must return out_of_scope rather than force the
question into a valid analytical intent.

When intent == out_of_scope:

route_id must be null;

no Transportation analytical BQ is executed;

the explanatory LLM call is not executed.

Calibration example:

"Qual é o chocolate mais gostoso?"

when submitted inside the Transportation domain must be classified as
out_of_scope rather than coerced into a Transportation analysis.

Transportation Dispatcher

Implemented in:

src/ai/transportation_dispatcher.py

The dispatcher is deterministic.

It does not interpret natural language and does not call an LLM.

Its responsibility is to map an already validated Transportation intent to
the corresponding authorized deterministic analytical function.

Current mapping:

network_overview -> analisar_operacao_forecast

economic_efficiency -> analisar_eficiencia_economica

weekly_evolution -> analisar_evolucao_semanal

cost_share -> analisar_participacao_custo_rede

cost_ranking -> analisar_ranking_custo_semanal

cost_concentration -> analisar_concentracao_custo_rede

recent_trend -> analisar_tendencia_recente

operational_changes -> analisar_mudancas_operacionais

cost_pressure -> analisar_pressao_custo_rede

executive_summary -> analisar_resumo_executivo_semanal

out_of_scope is deliberately NOT part of the dispatcher analytical mapping.

If route_id is present and the analytical result is a list, the dispatcher
filters the deterministic result to that route.

Important boundary:

Router answers:
"What analytical capability does this Transportation question require?"

Dispatcher answers:
"Which authorized deterministic function executes that capability?"

Analytics / SQL answers:
"What is the authoritative result?"

Transportation Context

Implemented in:

src/ai/transportation_context.py

preparar_contexto_transporte(...) does not recalculate metrics and does not
create conclusions.

It structures the official deterministic analytical output for downstream LLM
interpretation.

The context records:

dominio = transportation;

tipo_analise;

summary metadata such as total_registros and route_ids;

the original deterministic resultado.

Service orchestration

src/ai/service.py is now multidomain.

Public orchestration contract:

responder(pergunta, dominio="inventory")

Supported domains:

inventory

transportation

Inventory remains the default to preserve backward compatibility.

Inventory flow:

explicit domain = inventory
-> Inventory tool/data
-> Inventory context
-> SYSTEM_PROMPT + INVENTORY_PROMPT
-> explanatory LLM response

Transportation flow:

explicit domain = transportation
-> Transportation router / structured LLM intent
-> out_of_scope guardrail OR valid intent
-> deterministic dispatcher
-> deterministic SQL / analytics
-> Transportation context
-> SYSTEM_PROMPT + TRANSPORTATION_PROMPT
-> explanatory LLM response using the ORIGINAL user question

The second LLM call receives the original question so that the business
explanation remains aligned with what the user actually asked.

API / Tool integration

Transportation has a bounded API/tool integration for operational changes.

The existing integration includes a route-level Transportation changes
endpoint and the corresponding AI tool contract.

The architecture deliberately does NOT create ten HTTP endpoints merely
because ten deterministic SQL analytical functions exist.

The dispatcher may invoke the completed deterministic analytics directly
inside the application boundary.

This avoids infrastructure scope creep while preserving explicit,
testable analytical capabilities.

Architectural responsibility boundary

The implemented end-to-end responsibility model is:

Frontend / calling layer
-> selects Inventory or Transportation explicitly

Transportation Router / LLM
-> interprets the question inside the already-selected Transportation domain

Pydantic Structured Output
-> constrains the probabilistic interpretation to an explicit intent contract

Transportation Dispatcher
-> selects the authorized deterministic capability

SQL / Deterministic Analytics
-> calculates authoritative values and detects measurable changes

Transportation Context
-> structures the official result without recalculation

LLM / Copilot
-> explains the deterministic result in business language

Human
-> evaluates context and makes the decision

Canonical compact principle:

UI defines the domain.
LLM interprets the intent.
Dispatcher selects the capability.
SQL calculates.
Analytics detects.
AI explains.
Human decides.

Testing checkpoint --- 2026-09-20

The multidomain increment has targeted tests covering:

Inventory backward compatibility;

prompt forwarding;

Structured Output client behavior;

Transportation router contract and behavior;

out_of_scope routing;

deterministic dispatcher mapping;

route_id filtering;

out_of_scope blocking before analytics;

Transportation context construction;

multidomain service orchestration;

invalid domain rejection;

Transportation API/tool integration.

Current full project regression checkpoint:

105 passed

Canonical regression command:

python -m pytest -q

This 105-passed checkpoint validates that the multidomain Transportation AI
integration did not break the existing project behavior covered by the
regression suite.

The testing workflow remains:

localized change
-> localized tests
-> continue

meaningful feature / cross-cutting checkpoint
-> full regression

A plausible LLM explanation is not evidence that the analytical calculation
is correct.

The deterministic layer remains the source of truth.

Known bounded follow-up items

The following items remain known but must not distract from Phase 0 closure.

Tariff effective-date enforcement

The rate schema supports effective_from / effective_to, but the current
vehicle-alternative query does not yet need multiple historical rate versions.

Temporal rate selection should be enforced before multiple historical rates
per route/vehicle are introduced.

Zero forecast

Zero forecast is allowed by the current forecast schema.

Metric logic involving cost_per_piece requires an explicit zero-volume policy
before that edge case becomes part of a relied-upon analytical path.

ETL idempotency

Master/forecast ETLs currently use append semantics and are not intended to be
blindly rerun against already-loaded primary keys.

Do not use pandas if_exists="replace", because that would destroy schema
constraints.

Define explicit idempotency/upsert behavior only when a concrete requirement
makes it necessary.

Plan vs Actual

transport_actual is not implemented.

Plan-vs-Actual remains a valid future Transportation capability, but it is not
required for the current bounded Phase 0 exit unless a concrete portfolio or
integration requirement makes it necessary.

Service-premium calibration

Do not reopen service-premium calibration unless a concrete business
requirement makes it necessary.

GHG / sustainability extension

Remains optional and outside the current minimum exit path.

Remaining bounded sequence from this checkpoint

Planning + Materialization
DONE
->
Advanced SQL BQ-00 -> BQ-09
DONE
->
Deterministic Analytics + Tests
DONE
->
Transportation API / Tool Contract
DONE for current bounded integration
->
Multidomain AI Layer
DONE
->
Structured Transportation Intent Routing
DONE
->
Deterministic Transportation Dispatcher
DONE
->
out_of_scope Guardrail
DONE
->
Inventory + Transportation Full Regression
DONE - 105 passed
->
Selected real-LLM Transportation validation
DONE for the current portfolio milestone
->
Document demonstrated extensibility / Phase 0 exit
DONE
->
STOP Transportation expansion

Phase 0 Closure --- 2026-09-22

Transportation Phase 0 is CLOSED for the current portfolio milestone.

Transportation successfully demonstrates:

advanced SQL applied to a realistic synthetic Supply Chain problem;

deterministic Transportation planning and analytics;

explicit separation between authoritative calculations and LLM interpretation;

structured LLM intent routing through Pydantic;

deterministic capability dispatch;

domain-specific context preparation;

multidomain AI orchestration;

explicit Inventory / Transportation domain selection;

Inventory backward compatibility;

bounded API/tool integration;

end-to-end frontend/API/Copilot integration;

architectural extensibility across two distinct Supply Chain domains.

Final full regression checkpoint:

python -m pytest -q

105 passed

Portfolio conclusion

Transportation fulfilled its intended role as an architectural extensibility case for the AI Supply Chain Copilot.

No further Transportation expansion is required for the current portfolio milestone.

The following remain valid optional future extensions, not blockers or open Phase 0 requirements:

Plan vs Actual;

historical tariff-version enforcement;

explicit zero-volume policy;

ETL idempotency/upsert behavior where required;

GHG / sustainability analytics;

deeper Transportation optimization;

additional analytical capabilities only when justified by a concrete business or integration requirement.

Canonical architectural principle

UI defines the domain.
LLM interprets the intent.
Dispatcher selects the capability.
SQL calculates.
Analytics detects.
AI explains.
Human decides.

Resume instruction

If Transportation is revisited in a future development session, this document remains the source of truth.

Do not reopen completed Phase 0 work without a concrete new requirement.

The next roadmap phase should proceed outside Transportation.