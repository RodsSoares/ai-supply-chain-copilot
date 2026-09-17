Transportation Analytics Architecture

Document: 06_transportation_architecture.md
Project: AI Supply Chain Copilot
Status: Phase 0 --- Bounded Transportation Extension
Last updated: 2026-09-16

1. Purpose

Transportation is a bounded analytics extension of the existing AI
Supply Chain Copilot.

Its purpose is to:

strengthen advanced SQL skills through realistic Supply Chain
problems;

rebuild classes of transportation-planning problems previously
encountered professionally using 100% synthetic data;

demonstrate a strong deterministic analytics layer;

prove that the Copilot architecture can support a second Supply
Chain domain without breaking Inventory;

expose Transportation analytics through compatible API/tool
contracts;

allow the LLM layer to interpret deterministic analytical results in
business language.

Transportation is not intended to become a standalone product.

Transportation is an analytics extensibility case, not a
transportation optimization product.

The target portfolio narrative is:

I took classes of transportation-planning problems I had solved
professionally and rebuilt them with a modern analytics architecture
using fully synthetic data, then integrated those capabilities into an
existing AI Supply Chain Copilot to demonstrate architectural
extensibility.

2. Clean-Room and Confidentiality Rules

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

3. Scope

The Transportation domain will cover a bounded planning and analytics
chain:

Forecast Demand
      ↓
Route Characteristics
      ↓
Planning Policy
      ↓
Vehicle / Capacity Choice
      ↓
Required Trips
      ↓
Capacity Utilization
      ↓
Transportation Cost
      ↓
R$/Piece
      ↓
Plan vs Actual
      ↓
Variance / Driver Analysis
      ↓
Prioritization

The emphasis is on analytics and decision support, not mathematical
optimization.

4. Architectural Position

Transportation becomes a second analytical domain inside the existing
Copilot.

Data / Synthetic ERP
        ↓
Canonical Data Layer
        ↓
Decision / Analytics Layer
        ├── Inventory
        └── Transportation
                ↓
         API / Tool Contracts
                ↓
          LLM / Copilot

For natural-language analytical questions:

User Question
      ↓
LLM Intent / Tool Selection
      ↓
Transportation Analytical Tool
      ↓
SQL / Deterministic Analytics
      ↓
Structured Result
      ↓
LLM Interpretation
      ↓
Business Answer

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

5. Planning Policy v0

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

accept that this may produce a somewhat higher transportation cost
per piece.

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

Forecast
   +
Route
   +
Vehicle Capacity
   +
Service Policy
   +
Route/Vehicle Tariff
        ↓
Vehicle Configuration
        ↓
Planned Trips

planned_trips may be materialized in the plan for analytics, but it
remains a derived planning output.

6. Planning Policy vs Optimization

The MVP must not evolve into a vehicle-routing or fleet-optimization
engine.

The Planning Policy exists primarily to produce a realistic and
explainable planning scenario.

Conceptually:

Forecast
    ↓
Route Characteristics
    ↓
Eligible / Preferred Vehicle Logic
    ↓
Target Service Frequency
    ↓
Economic Feasibility
    ↓
Vehicle + Trips
    ↓
Capacity Utilization
    ↓
Planned Cost
    ↓
R$/Piece

The analytical system can compare valid alternatives, but the objective
is not to build a globally optimal mathematical transportation plan.

A lower-cost configuration is not automatically the correct
configuration if it violates the synthetic service policy.

7. PLAN and ACTUAL

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

8. Minimum Synthetic Data Model

The initial model should remain small.

routes

route_id
origin_id
destination_id
distance_km
route_profile       -- SHORT / LONG

vehicle_types

vehicle_type_id
vehicle_name
capacity_pieces

route_vehicle_rates

route_id
vehicle_type_id
effective_from
effective_to
rate_per_trip

The temporal fields allow future synthetic tariff changes without
redesigning the schema.

demand_forecast

period
route_id
forecast_pieces

transport_plan

period
route_id
vehicle_type_id
planned_trips
planned_capacity
planned_utilization
planned_cost
planned_cost_per_piece

transport_plan is a derived/materialized analytical output.

transport_actual

period
route_id
actual_pieces
actual_trips
actual_cost

Additional fields should only be introduced when required by a concrete
business question.

9. Core Planning Calculations

For a candidate vehicle configuration:

Capacity-Driven Trips

[ Trips_{capacity} = \left{=tex}\lceil{=tex}
\frac{ForecastPieces}{VehicleCapacity}{=tex}
\right{=tex}\rceil{=tex} ]

Offered Capacity

[ OfferedCapacity = PlannedTrips \times {=tex}VehicleCapacity ]

Capacity Utilization

[ Utilization = \frac{ForecastPieces}{OfferedCapacity}{=tex} ]

Planned Transportation Cost

[ PlannedCost = PlannedTrips \times {=tex}RatePerTrip ]

Cost per Piece

[ R$/Piece = \frac{TransportationCost}{TransportedPieces}{=tex} ]

These formulas are deterministic and must be tested independently of the
LLM.

The final number of planned trips may also reflect the target service
frequency and economic-exception rule.

10. Why R$/Piece Is a Core KPI

R$/Piece is not a cosmetic metric.

It normalizes transportation spending by transported volume and answers
an important executive question:

Did transportation cost increase because we moved more volume, or
because transporting each unit became more expensive?

For example:

cost +15%, pieces +20% → R$/piece decreases → unit economics
improved;

cost +15%, pieces +5% → R$/piece increases → unit economics
deteriorated;

cost +15%, pieces +15% → R$/piece approximately stable → increase
is largely volume-driven.

R$/piece is therefore a protagonist of the Transportation analytical
layer.

11. Cost Variance Decomposition

Let:

[ C = V \times {=tex}U ]

where:

C = transportation cost;

V = transported pieces;

U = transportation cost per piece.

Between period 0 and period 1:

Volume Effect

[ VolumeEffect = (V_1 - V_0) \times {=tex}U_0 ]

Unit Cost Effect

[ UnitCostEffect = V_1 \times {=tex}(U_1 - U_0) ]

Reconciliation

[ \Delta {=tex}Cost = VolumeEffect + UnitCostEffect ]

Example:

January
1,000,000 pieces × R$0.50 = R$500,000

February
1,200,000 pieces × R$0.55 = R$660,000

Cost change = +R$160,000
Volume effect = +R$100,000
Unit-cost effect = +R$60,000

Interpretation:

R$100k of the increase came from additional transported volume;

R$60k came from deterioration in transportation cost per piece.

This decomposition should remain simple, transparent and explainable.

12. Driver Hierarchy

The analytical hierarchy should distinguish detection from diagnosis.

BQ-00 --- What operation is required for the forecast?

Forecast
→ Vehicle / Capacity
→ Trips
→ Utilization
→ Cost
→ R$/Piece

BQ-01 --- Why did transportation cost change?

Primary decomposition:

Cost Change
├── Volume Effect
└── Unit-Cost Effect

BQ-02 --- Why did R$/Piece change?

Potential diagnostic drivers:

R$/Piece
├── route/vehicle tariff
├── capacity utilization
├── trips / service frequency
├── vehicle mix
├── route mix
└── volume crossing a capacity threshold

The MVP should avoid claiming causal precision beyond what the
deterministic data supports.

The objective is explainable driver analysis, not an unnecessarily
complex causal model.

13. Capacity Threshold Effect

Transportation cost can behave discontinuously.

Example:

Vehicle capacity: 10,000 pieces
Rate per trip: R$3,000

For 9,900 pieces:

1 trip
Cost = R$3,000
R$/piece ≈ R$0.303

For 10,100 pieces:

2 trips
Cost = R$6,000
R$/piece ≈ R$0.594

A small increase in volume can therefore create a large cost increase
when demand crosses a capacity threshold.

This illustrates why:

volume change alone does not explain transportation cost behavior.

The analytical layer should be able to distinguish volume growth from
operational effects such as additional trips and lower utilization.

14. Canonical Business Questions

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

Where does maintaining target frequency materially increase
R$/piece?

Which routes operate below target frequency because of economic
rules?

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

Which routes should be prioritized for operational review in the
next period, and why?

Candidate analytical output:

route_id
forecast_volume
planned_trips
capacity_utilization
planned_cost
cost_per_piece
cost_change_pct
cost_per_piece_change_pct
utilization_change
network_cost_share
priority_rank

Prioritization logic must remain transparent and explainable.

15. Advanced SQL Learning Objectives

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

The target is approximately 10--15 high-quality business queries,
not a large collection of generic exercises.

16. SQL Learning Progression

A single business problem may evolve through increasingly advanced SQL.

Level 1 --- Aggregation

Question:

What is forecast volume by route and period?

Concepts:

JOIN
GROUP BY
SUM

Level 2 --- Capacity

Question:

How many trips does each candidate vehicle require?

Concepts:

JOIN
division
rounding / ceiling logic
business rules

Level 3 --- Utilization and Cost

Question:

What utilization, planned cost and R$/piece result from each
configuration?

Concepts:

derived metrics
CASE
multiple joins

Level 4 --- Temporal Comparison

Question:

How did cost and R$/piece change versus the previous period?

Concept:

LAG()

Level 5 --- Trend

Question:

Is deterioration temporary or persistent?

Concepts:

AVG() OVER(...)
rolling windows

Level 6 --- Contribution and Prioritization

Question:

Which routes explain the network variance and deserve attention first?

Concepts:

chained CTEs
CASE
SUM() OVER(...)
RANK()
multiple KPIs

The capstone should combine several of these concepts in one explainable
analytical flow.

17. SQL Exit Criterion

Phase 0 SQL is considered sufficient when the user can independently
reason through:

Business Problem
      ↓
Required Grain
      ↓
Required Tables
      ↓
Joins
      ↓
Aggregation
      ↓
Window / Temporal Comparison
      ↓
Business Rule
      ↓
Analytical Result
      ↓
Business Interpretation

The objective is not memorizing syntax.

The user should be able to explain:

why the query has its chosen grain;

why each join exists;

why a window function is needed;

how the business rule is represented;

what the output means operationally;

what the query does not prove.

18. Candidate Transportation Analytical Tools

Names are provisional and should only be implemented when supported by
completed deterministic analytics.

Potential tools:

analyze_transport_cost_variance(...)
rank_transport_cost_drivers(...)
analyze_capacity_utilization(...)
forecast_route_capacity(...)
rank_cost_per_piece_deterioration(...)
analyze_plan_vs_actual(...)

Example structured output:

{
  "cost_change_pct": 18.4,
  "volume_change_pct": 12.1,
  "cost_per_piece_change_pct": 5.6,
  "volume_effect": 420000,
  "unit_cost_effect": 190000
}

The LLM receives structured analytical results and produces a business
explanation.

Tool contracts should remain stable, explicit and testable.

19. Testing Strategy

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

python -m pytest <target> -q
python -m pytest -q

A plausible LLM explanation is not evidence that the analytical
calculation is correct.

20. Optional GHG Extension

Environmental impact existed as a dimension in the broader class of
transportation-planning problems.

A future bounded extension may use synthetic data such as:

distance;

vehicle category;

fuel consumption;

emission factor;

estimated emissions.

This could enable a question such as:

How do candidate transportation decisions compare on cost and
estimated environmental impact?

However:

GHG is not part of the Phase 0 minimum exit criterion.

It must not delay:

advanced SQL completion;

deterministic Transportation analytics;

Copilot integration;

transition to the next roadmap phase.

21. Explicit Non-Goals

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

a reconstruction of a previous employer's proprietary planning
model.

Interesting adjacent ideas go to the backlog.

22. Scope-Control Rule

The development path is:

Synthetic Transportation Problem
        ↓
Advanced SQL
        ↓
Deterministic Analytics + Tests
        ↓
Copilot Integration
        ↓
LLM / Tool Calling
        ↓
Extensibility Demonstrated
        ↓
STOP

Any adjacent idea that is not necessary for this chain:

Good Idea
   ↓
BACKLOG
   ↓
Continue Current Scope

The word STOP is intentional.

Transportation exists to complete Phase 0, not to delay the broader
career roadmap.

23. Relationship to Career Roadmap

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

24. Portfolio Value

The value of this extension is not the number of features.

It demonstrates a combination of:

Business Reasoning
        +
Supply Chain Domain Knowledge
        +
Data Modeling
        +
Advanced SQL
        +
Deterministic Analytics
        +
Testing
        +
API / Tool Contracts
        +
LLM Interpretation
        +
Software Extensibility

The desired architectural story is:

Historical approach
Business Problem
→ Planning Model
→ Advanced Spreadsheet
→ Analytical Decision Support

Modern reconstruction
Business Problem
→ Synthetic Canonical Data
→ SQL Analytics
→ Deterministic Decision Support
→ API / Tool
→ LLM Interpretation

The technology changes.

The underlying ability to structure and solve complex business problems
remains central.

25. Design Principles

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

Short routes favor frequency/flexibility; long routes favor
scale/unit economics.

Planning Policy exists to support analytics, not to become an
optimization product.

Prove extensibility by adding Transportation without breaking
Inventory.

Tests before trusting AI interpretation.

Concept before code.

Finish bounded scope before adjacent capabilities.

Portfolio value = business reasoning + architecture, not feature
count.

26. First Development Sequence

With architecture and scope frozen, implementation should proceed in
this order:

1. Create minimal synthetic schema
2. Create small deterministic synthetic dataset
3. Validate planning-policy calculations
4. Start business-question-driven SQL exercises
5. Progress from aggregation to advanced analytical SQL
6. Implement deterministic Transportation analytics
7. Add tests
8. Expose selected analytics through Copilot-compatible contracts
9. Integrate LLM/tool calling
10. Run Inventory + Transportation regression
11. Document demonstrated extensibility
12. STOP

Documentation should not become the work itself.

After this architecture document is accepted, the emphasis moves to
implementation and learning.

27. Definition of Done --- Transportation Phase 0

Transportation Phase 0 is complete when:

all data and entities are fully synthetic;

no confidential or proprietary historical information is
exposed;

Planning Policy v0 is implemented using explicit synthetic
rules;

planned_trips is treated as a derived planning result;

non-linear route/vehicle tariffs are represented;

short-route and long-route planning profiles are represented;

target service frequency is represented without becoming an
absolute universal constraint;

the core planning model is documented;

approximately 10--15 meaningful business-driven SQL queries are
completed;

advanced SQL concepts are demonstrated in realistic analytical
questions;

R$/piece is implemented and tested;

volume vs unit-cost variance decomposition is implemented and
tested;

capacity/utilization analytics are implemented;

capacity-threshold effects can be analyzed;

bounded Plan vs Actual analytics are implemented;

a transparent route-prioritization capstone is completed;

the analytical logic and SQL can be explained independently;

deterministic Transportation analytics are exposed through
compatible Copilot API/tool contracts;

selected natural-language Transportation questions invoke
deterministic tools;

LLM output interprets structured results rather than
recalculating authoritative KPIs;

existing Inventory behavior remains intact;

targeted and full regression tests pass;

the Copilot demonstrably supports a second Supply Chain
analytical domain;

no unnecessary standalone Transportation product has been
created.

Then:

STOP Transportation expansion and move to the bounded LinkedIn
Agentic refactor.