# Transportation Analytics --- Context, Architecture & Development Charter

**Project:** AI Supply Chain Copilot\
**Module / use case:** Transportation Analytics\
**Status:** Pre-development context freeze\
**Date:** 2026-09-16

------------------------------------------------------------------------

## 1. Purpose

Transportation is **not a new standalone product**. It is a bounded
extension of the existing **AI Supply Chain Copilot** whose primary
purposes are:

1.  consolidate advanced SQL through realistic Transportation Planning
    problems;
2.  translate Rodrigo's prior planning/domain experience into a modern
    analytics implementation;
3.  add a second analytical domain to the Copilot, alongside Inventory;
4.  prove that the Copilot architecture is extensible without rebuilding
    the application;
5.  expose deterministic Transportation analytics as tools that can
    later be selected and interpreted by an LLM.

The intended portfolio story is:

> **Business problem → Data/SQL → Analytics → Decision Support →
> LLM/Tool Calling**

and, at the broader Copilot level:

> **Analytics → Decision Intelligence → AI Copilot → Agentic Execution**

Transportation stops after the SQL/analytics capability is connected to
the Copilot and extensibility is demonstrated. Further
optimization/productization belongs in backlog.

------------------------------------------------------------------------

## 2. Origin of the business problem

The case is inspired by classes of Transportation Planning problems
Rodrigo previously solved through an advanced Excel planning model.

The original model connected concepts such as:

-   demand/forecast;
-   destinations and routes;
-   transportation capacity;
-   vehicle size/category;
-   required frequency / number of trips;
-   capacity utilization;
-   route rates;
-   transportation budget;
-   cost per piece (`R$/PÇ`);
-   planning assumptions and scenarios;
-   seasonality;
-   operational/financial consolidation;
-   environmental/GHG-related calculations.

The goal is **not to reproduce the original spreadsheet**.

The spreadsheet is evidence of the type of analytical reasoning and
planning problems involved. Transportation will rebuild those problem
classes using a new data model and synthetic data.

------------------------------------------------------------------------

## 3. Confidentiality and clean-room rule

The public/project implementation must not expose or reproduce
confidential or company-specific information.

### Do not reuse

-   company name or branding;
-   real distribution centers;
-   real stores/destinations;
-   real routes;
-   real carriers;
-   real tariffs;
-   real costs;
-   real volumes;
-   real identifiers/codes;
-   proprietary commercial rules;
-   original datasets;
-   copied spreadsheet formulas or implementation details where they
    encode proprietary logic.

### What may be reused

The project may reuse **general domain knowledge and classes of business
questions**, such as:

-   how forecast affects transportation requirements;
-   capacity and utilization reasoning;
-   relationship between volume, trips and costs;
-   transportation cost normalization;
-   budget variance reasoning;
-   planning-vs-actual analysis;
-   generic sustainability reasoning.

All entities and observations in the new implementation must be
**synthetic**.

The principle is:

> **Rebuild the problem, not the spreadsheet.**

------------------------------------------------------------------------

## 4. Architectural principle

Transportation is a new analytical capability inside the existing
Copilot.

Conceptually:

``` text
                         AI SUPPLY CHAIN COPILOT
                                  |
                           LLM / Tool Calling
                                  |
                    Decision / Analytics Layer
                         /               \
                  Inventory          Transportation
                         \               /
                         Canonical Data Layer
                                  |
                              Data / ERP
```

The intended proof is that a second business domain can be introduced
while preserving the existing Copilot architecture and Inventory
capability.

### Extensibility criterion

The project succeeds architecturally when:

-   Inventory continues to work;
-   Transportation has its own deterministic analytics;
-   Transportation capabilities follow compatible contracts/tool
    patterns;
-   the LLM can route natural-language questions to the appropriate
    analytical capability;
-   adding Transportation does not require rebuilding the Copilot.

------------------------------------------------------------------------

## 5. Separation of responsibilities

A core architectural rule is:

> **LLM ≠ Calculator.**

The LLM should not be responsible for computing authoritative
transportation KPIs from raw records.

The intended flow is:

``` text
Natural-language question
        ↓
LLM / intent + tool selection
        ↓
Transportation analytical tool
        ↓
SQL / deterministic analytics
        ↓
Structured output
        ↓
LLM interpretation/explanation
```

Example:

``` text
User:
"Why did transportation cost increase in August?"

        ↓

Tool:
analyze_transport_cost_variance(...)

        ↓

Structured analytics:
- total cost change
- volume change
- R$/piece change
- volume effect
- unit-cost effect

        ↓

LLM:
business-language explanation
```

SQL/analytics owns the calculation. The LLM owns interpretation,
synthesis and natural-language interaction.

This also follows the broader project principle:

> **Context ≠ Policy.**

Critical rules, contracts and calculations should live in
deterministic/enforceable layers rather than merely in prompts.

------------------------------------------------------------------------

## 6. Analytical model: PLAN and ACTUAL

Transportation should not be merely historical reporting. The original
planning problem was fundamentally prospective:

> **Given the demand we expect, what transportation operation will we
> need?**

The synthetic model should therefore distinguish at least two analytical
worlds:

``` text
PLAN
demand_forecast
planned_capacity
planned_trips
planned_costs

          ↕ comparison

ACTUAL
shipments
actual_trips
actual_volume
actual_costs
```

This enables both forward-looking planning and plan-vs-actual analysis.

------------------------------------------------------------------------

## 7. Candidate synthetic data model

Exact schema should be finalized during implementation rather than
over-designed in advance.

Likely entities include:

``` text
distribution_centers
destinations
routes
carriers
vehicle_types
route_rates
demand_forecast
planned_trips
shipments
actual_trips
planning_assumptions
calendar
```

Possible conceptual relationships:

``` text
destinations
     ↓
demand_forecast
     ↓
routes ───────────── carriers
     ↓
vehicle_types
     ↓
route_rates
     ↓
planned_trips
     ↓
planned_transport_cost
```

### Route rates

Rates should not simply be a `cost` column embedded in `routes`.

A generic model may include:

``` text
route_rates
- route_id
- carrier_id
- vehicle_type_id
- effective_from
- effective_to
- rate
- rate_type
```

This supports rate changes, vehicle/capacity choices and temporal
analysis.

------------------------------------------------------------------------

## 8. Core planning chain

The principal business flow to preserve is:

``` text
Demand forecast
      ↓
Consolidation by destination / route / period
      ↓
Required transportation volume
      ↓
Vehicle capacity
      ↓
Required trips / frequency
      ↓
Expected capacity utilization
      ↓
Applicable rate
      ↓
Planned transportation cost
      ↓
R$/piece
      ↓
Budget / variance / decision
```

This is the backbone of the Transportation case.

------------------------------------------------------------------------

## 9. Canonical business questions

The SQL work should be driven by business questions rather than by
isolated syntax exercises.

### BQ-01 --- Transportation cost variance

**Canonical question:**

> **Did transportation cost increase because we moved more volume, or
> because transporting each unit became more expensive?**

Portuguese business formulation:

> **O custo aumentou porque transportamos mais ou porque ficou mais caro
> transportar?**

This is a central question of the case.

The primary normalization metric is:

``` text
R$/PÇ = Total Transportation Cost / Pieces Transported
```

Cost alone is insufficient because transportation cost naturally changes
with business volume.

Interpretation examples:

-   cost ↑ while pieces grow faster → unit transportation efficiency may
    have improved;
-   cost ↑ while pieces grow more slowly → `R$/PÇ` deteriorated;
-   cost and pieces grow proportionally → cost increase is largely
    volume-driven.

------------------------------------------------------------------------

## 10. Cost variance decomposition

A useful analytical extension is to explicitly decompose cost variance.

Let:

``` text
C = transportation cost
V = transported volume/pieces
U = unit transportation cost (R$/piece)

C = V × U
```

For baseline period `0` and current period `1`:

``` text
Volume Effect = (V1 - V0) × U0

Unit Cost Effect = V1 × (U1 - U0)

Δ Cost = Volume Effect + Unit Cost Effect
```

This allows the system to explain not only that cost changed, but how
much of the change came from:

-   business/volume growth;
-   deterioration or improvement in unit transportation cost.

A later diagnostic layer can investigate **why `R$/PÇ` changed**.

Candidate drivers include:

``` text
R$/PÇ change
    |
    +-- rate changes
    +-- capacity utilization
    +-- frequency / number of trips
    +-- route mix
    +-- vehicle mix
    +-- modal mix
```

Do not prematurely implement a sophisticated causal decomposition. Start
with a transparent, explainable variance model.

------------------------------------------------------------------------

## 11. Other business questions

### Demand and capacity

-   How much volume must each route transport by week/month?
-   How many trips are required to serve forecast demand?
-   What is expected capacity utilization by route?
-   Which routes are approaching or exceeding available capacity?
-   Which routes are persistently underutilized?
-   Is demand on a route increasing or decreasing?
-   Is a capacity issue temporary or persistent?

### Cost and budget

-   What is projected transportation spend for the next period?
-   Which routes account for the largest share of the transportation
    budget?
-   Which routes have the fastest cost growth?
-   Which routes have deteriorating `R$/PÇ`?
-   How much of a cost increase is explained by volume versus unit cost?
-   Which routes are driving budget variance?
-   Did a rate change materially affect cost?
-   Is the chosen vehicle/capacity economically appropriate for the
    forecast volume?

### Plan vs. actual

-   Where is actual volume diverging from forecast?
-   Where are actual trips exceeding planned trips?
-   Where is actual utilization worse than planned?
-   Which routes are generating unfavorable cost variance?
-   Is the deviation isolated or persistent?

### Prioritization

A capstone question should be:

> **Which routes should be prioritized for operational review in the
> next period, and why?**

Candidate output:

``` text
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
```

The prioritization logic should remain explainable.

------------------------------------------------------------------------

## 12. SQL learning objectives

Transportation is the bounded Phase 0 of the current learning roadmap.

The project should consolidate SQL through real analytical problems,
including:

-   `JOIN`;
-   `GROUP BY`;
-   conditional aggregation;
-   `CASE WHEN`;
-   subqueries where appropriate;
-   CTEs;
-   chained CTEs;
-   `ROW_NUMBER()`;
-   `RANK()` / `DENSE_RANK()`;
-   `LAG()` / `LEAD()`;
-   `SUM() OVER (...)`;
-   `AVG() OVER (...)`;
-   rolling/moving averages;
-   temporal comparisons;
-   cumulative/network-share calculations;
-   basic query-performance reasoning;
-   indexes;
-   understanding query plans;
-   avoiding unnecessary scans.

The direction is deliberately:

``` text
Business Question
      ↓
Required analytical reasoning
      ↓
SQL technique
```

not:

``` text
SQL technique
      ↓
invent an artificial exercise
```

------------------------------------------------------------------------

## 13. Example progression

A single business problem can progress in difficulty.

### Level 1 --- Aggregation

> How much volume must each route transport per week?

Concepts:

``` text
JOIN
GROUP BY
SUM
```

### Level 2 --- Capacity

> How many trips does each route require?

Adds:

-   capacity;
-   division/rounding;
-   business rules.

### Level 3 --- Utilization

> What is expected vehicle utilization?

Adds derived metrics.

### Level 4 --- Temporal comparison

> Is demand increasing or decreasing?

Adds:

``` text
LAG()
```

### Level 5 --- Trend

> Is the increase temporary or persistent?

Adds:

``` text
AVG() OVER (...)
rolling windows
```

### Level 6 --- Prioritization

> Which routes represent the highest operational/cost risk?

Adds:

``` text
chained CTEs
CASE
RANK()
multiple KPIs
```

------------------------------------------------------------------------

## 14. SQL exit criterion

The objective is **not to master all of SQL** or become a database
specialist.

Transportation is complete as a SQL learning phase when Rodrigo can
independently reason through a sufficiently complex business question
approximately as:

``` text
business problem
    ↓
grain
    ↓
required tables / joins
    ↓
aggregation
    ↓
windowing / temporal comparison
    ↓
business rule
    ↓
result
    ↓
business interpretation
```

A practical target is approximately **10--15 high-quality business
queries**, not hundreds of generic exercises.

The capstone should combine several advanced SQL concepts into a
route-prioritization / cost-driver analysis that Rodrigo can both
**build and explain**.

------------------------------------------------------------------------

## 15. Candidate analytical tools for the Copilot

Only after deterministic Transportation analytics are working should
they be exposed as Copilot capabilities.

Candidate tool concepts:

``` text
analyze_transport_cost_variance(...)
rank_transport_cost_drivers(...)
analyze_capacity_utilization(...)
forecast_route_capacity(...)
rank_cost_per_piece_deterioration(...)
analyze_plan_vs_actual(...)
```

Names and contracts are provisional.

Tools should return structured outputs suitable for LLM interpretation.

Example conceptual response:

``` json
{
  "cost_change_pct": 18.4,
  "volume_change_pct": 12.1,
  "cost_per_piece_change_pct": 5.6,
  "volume_effect": 420000,
  "unit_cost_effect": 190000
}
```

The LLM should not recreate these calculations from prose or raw rows.

------------------------------------------------------------------------

## 16. Testing expectations

Transportation should follow the existing engineering discipline of the
Copilot.

At minimum:

-   deterministic analytics should have tests;
-   KPI formulas should have known expected outputs;
-   edge cases should be explicit;
-   tool contracts should be tested before LLM integration;
-   existing Inventory regressions must remain green;
-   integration of Transportation must not silently alter existing
    behavior.

Project workflow preference:

``` text
python -m pytest <target>
python -m pytest -q
```

Never rely solely on LLM-generated interpretation as evidence that an
analytical calculation is correct.

------------------------------------------------------------------------

## 17. Sustainability / GHG

The source planning model contained a GHG/environmental dimension
involving concepts such as distance, vehicle category, consumption and
emissions factors.

This can become a **small optional extension** if it fits naturally
after the core Transportation capability is complete.

Potential question:

> Can a transportation decision be compared on both financial cost and
> environmental impact?

However:

-   this is not part of the minimum Phase 0 exit criterion;
-   it must not delay SQL completion;
-   it must not turn Transportation into a separate sustainability
    product.

Kyntra's broader sustainability principle remains relevant, but scope
discipline takes priority here.

------------------------------------------------------------------------

## 18. Explicit non-goals

For this phase, do **not** turn Transportation into:

-   a standalone SaaS;
-   a full TMS;
-   a route optimizer;
-   a vehicle-routing optimization engine;
-   a carrier marketplace;
-   a real-time tracking platform;
-   a digital twin;
-   a new agentic product;
-   a large frontend project;
-   an excuse to refactor the entire Copilot;
-   a new repository unless technically justified by the existing
    project structure;
-   a research project on every possible logistics KPI.

Interesting extensions go to backlog.

------------------------------------------------------------------------

## 19. Scope-control rule

Rodrigo tends to identify valuable adjacent product opportunities while
implementing projects. These ideas should be preserved without
interrupting the current learning/reemployment roadmap.

Use:

``` text
Good adjacent idea
       ↓
     BACKLOG
       ↓
continue current bounded scope
```

For Transportation:

``` text
Synthetic Transportation problem
        ↓
Advanced SQL
        ↓
Deterministic analytics + tests
        ↓
Copilot integration
        ↓
LLM/tool calling
        ↓
Extensibility demonstrated
        ↓
STOP
```

------------------------------------------------------------------------

## 20. Relationship to the current career roadmap

Transportation is **Phase 0**, not the destination.

Current sequence:

``` text
PHASE 0
Transportation + Advanced SQL
        ↓
PHASE 1
Bounded refactor of My LinkedIn Agentic AI System
        ↓
PHASE 2
Practical RAG
        ↓
PHASE 3
Evals + Observability
        ↓
Active applications / interview-driven gap closure
```

Active applications should begin by early October 2026 without waiting
for mastery of every remaining topic.

Later/parallel topics include:

-   APIs;
-   security/auth/RBAC;
-   Docker;
-   one cloud platform;
-   n8n hands-on;
-   gaps discovered from real vacancies/interviews.

Currently frozen/backlog:

-   AI Solution Factory;
-   AI Supervisor;
-   Copilot Studio;
-   Power Automate;
-   unnecessary Transportation product expansion.

------------------------------------------------------------------------

## 21. Portfolio narrative

Transportation should help demonstrate continuity between Rodrigo's
prior planning experience and his current AI/engineering development.

Historical capability:

``` text
Business problem
      ↓
Planning model
      ↓
Advanced Excel
      ↓
Analytical decision support
```

Modern implementation:

``` text
Business problem
      ↓
Synthetic canonical data
      ↓
SQL analytics
      ↓
Deterministic decision support
      ↓
API / Tool
      ↓
LLM interpretation
```

The story is not:

> "I learned some advanced SQL commands."

It is:

> **"I took classes of transportation-planning problems I had solved
> professionally and rebuilt them with a modern analytics architecture
> using fully synthetic data, then integrated those capabilities into an
> existing AI Supply Chain Copilot to demonstrate architectural
> extensibility."**

------------------------------------------------------------------------

## 22. Key design principles

Keep these visible during development:

1.  **Business question before SQL syntax.**
2.  **Rebuild the problem, not the original spreadsheet.**
3.  **Synthetic data only.**
4.  **LLM ≠ Calculator.**
5.  **Deterministic analytics before natural-language interpretation.**
6.  **Context ≠ Policy.**
7.  **Plan and Actual are distinct analytical concepts.**
8.  **R\$/PÇ is a core normalization KPI, not a cosmetic metric.**
9.  **Explain cost variance, don't merely report it.**
10. **Prove extensibility by adding Transportation without breaking
    Inventory.**
11. **Tests before trusting AI interpretation.**
12. **Concept before code.**
13. **Finish the bounded scope before adding adjacent capabilities.**
14. **Portfolio value comes from the business reasoning + architecture,
    not feature count.**

------------------------------------------------------------------------

## 23. First development step

When development resumes, do **not** begin with LLM integration.

Start by defining the minimum synthetic Transportation data model
necessary to answer the first canonical business questions.

Recommended first vertical slice:

``` text
Synthetic routes + periods + volumes + costs
        ↓
calculate R$/piece
        ↓
compare periods
        ↓
use LAG()
        ↓
decompose total cost variance
        ↓
test expected results
```

First canonical analytical question:

> **Did transportation cost increase because we moved more volume, or
> because transporting each unit became more expensive?**

Only after the deterministic analytical foundation is correct should the
capability move toward the Copilot/tool layer.

------------------------------------------------------------------------

## 24. Definition of Done --- Transportation Phase 0

Transportation is considered complete when:

-   the data used is fully synthetic;
-   the core planning model is documented;
-   approximately 10--15 meaningful business queries cover the intended
    advanced SQL concepts;
-   `R$/PÇ` and cost-variance analysis are implemented and tested;
-   capacity/utilization and plan-vs-actual analyses exist at an
    appropriate bounded level;
-   at least one meaningful prioritization/capstone query combines
    advanced SQL concepts;
-   Rodrigo can explain the analytical logic and SQL reasoning;
-   deterministic Transportation analytics are exposed through
    compatible Copilot tool/API contracts;
-   the LLM can answer selected Transportation questions by invoking
    those capabilities;
-   existing Inventory behavior remains intact;
-   tests pass;
-   the project demonstrates a second Supply Chain analytical domain;
-   no unnecessary standalone Transportation product has been created.

At that point:

> **STOP Transportation and move to the bounded refactor of My LinkedIn
> Agentic AI System.**
