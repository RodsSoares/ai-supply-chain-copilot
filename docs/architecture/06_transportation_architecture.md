Transportation Analytics Architecture

Document: 06_transportation_architecture.md Project: AI Supply Chain
Copilot Status: Phase 0 --- Bounded Transportation Extension Last
updated: 2026-09-19

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

Current Implementation Checkpoint --- 2026-09-19

This section is the authoritative handoff point for resuming
development. Earlier sections describe the target architecture and
design space; this section records what is actually implemented now and
the bounded sequence that remains.

Repository and environment

Repository: ai-supply-chain-copilot

Default environment: Windows + PowerShell + project-local .venv

Test command convention: always python -m pytest; never bare pytest.

Database: database/supply_chain.db

Inventory ETL lives under src/etl/inventory/.

Transportation ETL lives under src/etl/transportation/.

Transportation deterministic analytics live under
src/analytics/transportation/.

Prefer complete files for meaningful edits and incremental development:

concept -> implementation -> targeted test -> full regression

Productivity rule for the remaining Phase 0 work:

Do not reopen completed SQL exercises or expand Transportation with
adjacent capabilities unless a concrete requirement is necessary to
complete Copilot integration.

Implemented Transportation data

The synthetic master-data and forecast pipeline are implemented and
loaded.

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

calcular_cenarios_planejamento(...) exposes two deterministic
scenarios for each candidate vehicle.

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

The service premium quantifies the incremental unit cost required to buy
the preferred service frequency instead of operating only at the
physical capacity minimum.

The current architecture deliberately does not convert this metric into
an arbitrary tolerance rule.

Plan materialization

The complete synthetic weekly plan is now materialized through:

materializar_plano_completo()

The materialization reads all route-week forecast combinations,
generates the selected individual trips, clears the previous derived
plan and persists the regenerated plan.

planned_trips remains a derived planning output.

Current materialized checkpoint:

192 planned trips;

96 route-week plans;

1,997,400 planned pieces;

2,718,000 pieces of offered capacity;

R$778,000 planned transportation cost;

zero forecast-versus-plan reconciliation divergences.

Materialization is intentionally idempotent for this derived planning
layer.

Running the same materialization again must reproduce the same final
state rather than accumulate duplicate trips.

This DELETE + rebuild behavior is appropriate for the current derived
planning output. It must not be generalized to historical ACTUAL data.

Advanced SQL checkpoint: COMPLETE for current Phase 0 scope

Transportation SQL development was driven by business questions rather
than isolated syntax drills.

The implemented analytical module is:

src/analytics/transportation/sql_analysis.py

It currently contains ten deterministic analytical functions covering
BQ-00 through BQ-09.

BQ-00 --- Operation required for forecast

Implemented by:

analisar_operacao_forecast()

Core concepts:

JOIN;

GROUP BY;

SUM;

COUNT;

route-week analytical grain.

Purpose:

Reconstruct the weekly transportation operation from forecast, planned
trips and vehicle capacity/cost data.

BQ-01 --- Economic efficiency

Implemented by:

analisar_eficiencia_economica()

Core concepts:

CTE;

derived metrics;

utilization;

cost per piece;

analytical ordering.

Purpose:

Compare route-week economic efficiency using deterministic
transportation KPIs.

BQ-02 --- Weekly evolution

Implemented by:

analisar_evolucao_semanal()

Core concepts:

chained CTEs;

LAG();

PARTITION BY route_id;

temporal deltas.

Purpose:

Compare each route with its own previous weekly observation.

BQ-03 --- Network cost share

Implemented by:

analisar_participacao_custo_rede()

Core concepts:

SUM() OVER();

network total;

route-week cost share.

Purpose:

Measure how much each route-week contributes to total network
transportation cost.

BQ-04 --- Weekly cost ranking

Implemented by:

analisar_ranking_custo_semanal()

Core concept:

RANK().

Purpose:

Rank route cost within each weekly operating context.

BQ-05 --- Cumulative network cost concentration

Implemented by:

analisar_concentracao_custo_rede()

Core concepts:

ordered window;

cumulative SUM() OVER(...).

Purpose:

Show how transportation cost becomes concentrated as the largest
contributors are accumulated.

BQ-06 --- Recent trend

Implemented by:

analisar_tendencia_recente()

Core concepts:

rolling AVG();

ordered window frame;

recent temporal context.

Purpose:

Distinguish isolated weekly movement from a more persistent recent
pattern.

BQ-07 --- Relevant operational changes

Implemented by:

analisar_mudancas_operacionais()

Core concepts:

LAG();

CASE;

temporal comparison;

deterministic change detection.

Purpose:

Identify operational changes that can explain KPI movement without
asking the LLM to infer facts from raw rows.

BQ-08 --- Cost pressure / network relevance

Implemented by:

analisar_pressao_custo_rede()

Core concepts:

multiple analytical windows;

ranking;

network share;

combined deterministic indicators.

Purpose:

Combine cost pressure and network relevance into an explainable
analytical view.

BQ-09 --- Weekly executive network summary

Implemented by:

analisar_resumo_executivo_semanal()

Core concepts:

CTEs;

aggregation;

windows;

temporal comparison;

executive analytical grain.

Purpose:

Produce a deterministic weekly network-level summary suitable for
downstream decision support.

SQL exit decision

The Advanced SQL learning block is considered COMPLETE for the current
bounded Transportation scope.

The objective was never syntax memorization.

The demonstrated target is the ability to reason through:

Business Problem
-> Required Grain
-> Required Tables
-> Joins
-> Aggregation
-> Window / Temporal Comparison
-> Business Rule
-> Analytical Result
-> Business Interpretation

No BQ-10 or additional SQL exercise should be added merely to increase
query count.

New SQL should only be introduced if required by the remaining Copilot
integration.

Excel -> SQL mental model consolidated

The Transportation work established the following transferable mapping:

Analytical problem      Excel mental model      SQL mental model

Combine related data    XLOOKUP / PROCV         JOIN

Consolidate many rows   Pivot / SUMIFS          GROUP BY + aggregation

Intermediate analytical Helper sheet            CTE
stage

Compare with previous   Previous physical row   LAG() over a logical
period                                          window

Share of total          Row value / absolute    SUM() OVER()
total cell

Ranking                 ORDEM / ORDEM.EQ        RANK()

Cumulative value        Progressive range       Running SUM() OVER()

Rolling average         Moving cell range       AVG() OVER(...)

Detect operational      IF + previous row       LAG() + CASE
change

Core paradigm shift:

Excel tends to encourage cell/position-oriented reasoning.

SQL encourages set/relation/grain/transformation-oriented reasoning.

The analytical reasoning remains transferable; the expression mechanism
changes.

Golden analytical case: R001 capacity-threshold transition

The R001 weekly evolution provides a strong calibration example for
future Copilot integration.

Week 2026-10-05

forecast: 9,700 pieces;

selected configuration: 2 x LIGHT_TRUCK;

vehicle capacity: 5,000 pieces each;

offered capacity: 10,000 pieces;

planned cost: R$1,700;

utilization: 97%;

cost per piece: approximately R$0.1753.

Week 2026-10-12

forecast: 10,300 pieces;

selected configuration: 2 x MEDIUM_TRUCK;

vehicle capacity: 10,000 pieces each;

offered capacity: 20,000 pieces;

planned cost: R$2,300;

utilization: 51.5%;

cost per piece: approximately R$0.2233.

Deterministic causal chain supported by the planning data

Forecast: 9,700 -> 10,300 (+600)
-> previous 10,000-piece offered capacity is no longer sufficient
-> selected plan changes from 2 LIGHT_TRUCKS to 2 MEDIUM_TRUCKS
-> offered capacity: 10,000 -> 20,000
-> utilization: 97% -> 51.5%
-> planned cost: R$1,700 -> R$2,300
-> R$/Piece: ~0.1753 -> ~0.2233

This is a useful example of a capacity-threshold effect: a relatively
small increase in demand can trigger a discrete operational
configuration change and a non-linear KPI response.

Golden / calibration answer for the Copilot

A utilização da R001 caiu de 97% para 51,5% porque o forecast
ultrapassou a capacidade semanal de 10.000 peças do plano anterior,
provocando a mudança de 2 LIGHT_TRUCKS para 2 MEDIUM_TRUCKS. A
capacidade oferecida dobrou para 20.000 peças, enquanto a demanda
cresceu apenas 600 peças.

This example should be used as a behavioral reference for the next
integration step.

The LLM must not independently recalculate these authoritative values.

Decision-support contract for the next layer

The architecture now has a clear responsibility boundary:

SQL / Deterministic Analytics
-> establishes facts and detects measurable changes

LLM / Copilot
-> interprets structured facts and explains them in business language

Human
-> evaluates context and makes the decision

Compact principle:

SQL calculates. Analytics detects. AI explains. Human decides.

This does not replace the existing rule:

LLM != Calculator.

It operationalizes it.

The next Copilot integration should therefore pass structured
deterministic results to the LLM rather than raw operational data
whenever the required analytical fact is already available.

Expected explanation flow:

User Question
-> Intent / Tool Selection
-> Transportation Analytical Tool
-> Deterministic SQL / Analytics
-> Structured Result
-> LLM Interpretation
-> Business Explanation
-> Human Decision

A strong answer should:

state the relevant deterministic facts;

identify the observed operational change;

connect that change to the KPI movement only when supported by the
deterministic data;

explain the result in business language;

avoid inventing unsupported causes or recommendations.

Testing checkpoint

Planning-policy and planning-materialization tests are implemented.

Advanced SQL deterministic tests are implemented in:

tests/test_transportation_sql_analysis.py

Current SQL analytical checkpoint:

BQ-00 through BQ-09 implemented;

10 core SQL business-question tests passing.

Current full project regression checkpoint:

77 passed

Canonical regression command:

python -m pytest -q

Transportation integration must continue to preserve existing Inventory
behavior.

A plausible LLM explanation is not evidence that the analytical
calculation is correct.

The deterministic layer remains the source of truth.

Project audit checkpoint --- 2026-09-19

The current project audit reports:

37 Python files;

6,399 total lines;

4,983 effective code lines;

211 functions;

5 classes;

0 TODO/FIXME comments;

0 syntax-error files;

heuristic overall project health: 9.2/10.

Relevant current Transportation structure:

src/
  analytics/
    transportation/
      planning.py
      sql_analysis.py
  decision/
    transportation/
      planning_policy.py
  etl/
    transportation/
      load_forecast.py
      load_master_data.py
  database/
    create_transportation_tables.py

scripts/
  materialize_transportation_plan.py

tests/
  test_transportation_planning.py
  test_transportation_planning_policy.py
  test_transportation_sql_analysis.py
  test_transportation_tables.py

Relevant existing Copilot layer:

src/
  ai/
    client.py
    context.py
    prompts.py
    service.py
    tools.py
  api/
    main.py

Architectural observation:

Transportation deterministic logic exists as a bounded domain, while the
current AI/Copilot layer still needs to expose and consume selected
Transportation capabilities.

That is the next meaningful architectural increment.

No broad refactor is justified before that integration.

Known bounded follow-up items

The following items remain known but must not distract from the
immediate integration path.

Tariff effective-date enforcement

The rate schema supports effective_from / effective_to, but the
current vehicle-alternative query does not yet need multiple historical
rate versions.

The current single-rate synthetic dataset is safe.

Temporal rate selection should be enforced before multiple historical
rates per route/vehicle are introduced.

Zero forecast

Zero forecast is allowed by the current forecast schema.

Metric logic involving cost_per_piece requires an explicit zero-volume
policy before that edge case becomes part of a relied-upon analytical
path.

ETL idempotency

Master/forecast ETLs currently use append semantics and are not intended
to be blindly rerun against already-loaded primary keys.

Do not use pandas if_exists="replace", because that would destroy
schema constraints.

Define explicit idempotency/upsert behavior only when a concrete
requirement makes it necessary.

Plan vs Actual

transport_actual is not implemented.

Plan-vs-Actual remains a valid future Transportation capability
described by the target architecture, but it is not required before
demonstrating the current bounded extensibility objective.

It must not delay Copilot integration.

If a later business question or portfolio requirement makes
Plan-vs-Actual necessary, implement it as a separate bounded increment
with deterministic tests.

Service-premium calibration

Do not reopen service-premium calibration unless a concrete business
requirement makes it necessary.

Do not manufacture synthetic complexity merely to produce more granular
premium values.

GHG / sustainability extension

Remains optional and outside the current minimum exit path.

Remaining bounded sequence from this checkpoint

The current sequence is intentionally short.

Planning + Materialization
DONE
↓
Advanced SQL BQ-00 -> BQ-09
DONE
↓
Deterministic Analytics + Tests
DONE for current integration scope
↓
Expose selected Transportation analytics through Copilot-compatible Tool Contract
NEXT
↓
Integrate LLM / Tool Calling
↓
Validate R001 golden case and selected natural-language questions
↓
Run full Inventory + Transportation regression
↓
Document demonstrated extensibility
↓
STOP

Do not add additional SQL BQs, frontend expansion, optimization,
detailed service-policy calibration, Plan-vs-Actual, GHG or unrelated
Transportation features unless they become necessary to complete this
chain.

Immediate next development increment

The next increment is:

Transportation Analytics -> Tool Contract -> LLM ->
Decision-Support Answer -> Tests

Before changing code, inspect the current integration surface:

src/ai/tools.py

src/ai/service.py

src/ai/context.py

src/ai/prompts.py

src/api/main.py

The objective is not to redesign the existing Copilot.

The objective is to expose a small number of completed Transportation
deterministic capabilities through compatible contracts and prove that
the existing architecture can support a second Supply Chain analytical
domain.

Preferred first integration target:

R001-style temporal/operational explanation, where deterministic
analytics provides the facts and the LLM converts them into a concise
business explanation.

The first implementation should remain narrow enough to test end-to-end
before adding more Transportation intents.

Resume instruction

When a new development session starts, this file should be treated as
the Transportation source of truth.

Resume from this Current Implementation Checkpoint, not from older
aspirational sequences.

Current regression baseline:

python -m pytest -q

Expected checkpoint result at the time of this update:

77 passed

If regression remains green:

inspect the existing Copilot integration surface;

define the minimum Transportation tool contract;

implement the bounded integration;

run targeted tests;

run full regression;

validate the R001 golden example;

continue only as far as required to demonstrate extensibility.

Do not reopen completed Advanced SQL learning work without a concrete
need.

Definition of Done --- Transportation Phase 0

Transportation Phase 0 is complete when:

all data and entities used by Transportation are fully synthetic;

no confidential or proprietary historical information is exposed;

Planning Policy v0 is implemented using explicit synthetic rules;

planned_trips is treated as a derived planning result;

plan materialization is deterministic and idempotent;

non-linear route/vehicle tariffs are represented;

short-route and long-route planning profiles are represented;

target service frequency is represented without becoming an absolute
universal constraint;

Capacity Requirement and Service Target remain semantically
distinct;

the core planning model is documented;

BQ-00 through BQ-09 provide a meaningful business-driven Advanced
SQL set;

advanced SQL concepts are demonstrated in realistic analytical
questions;

R$/Piece is implemented and tested;

capacity/utilization analytics are implemented;

capacity-threshold effects can be detected and explained from
deterministic evidence;

the analytical logic and SQL can be explained independently of the
LLM;

selected deterministic Transportation analytics are exposed through
compatible Copilot tool/API contracts;

selected natural-language Transportation questions invoke
deterministic analytics;

LLM output interprets structured results rather than recalculating
authoritative KPIs;

the R001 capacity-threshold case is validated as a
golden/calibration example;

existing Inventory behavior remains intact;

targeted and full regression tests pass;

the Copilot demonstrably supports a second Supply Chain analytical
domain;

no unnecessary standalone Transportation product has been created.

Plan-vs-Actual, historical tariff versions, GHG analysis and deeper
Transportation optimization are not required for the current Phase 0
exit unless a concrete integration requirement proves otherwise.

Then:

STOP Transportation expansion and move to the bounded LinkedIn Agentic
refactor.