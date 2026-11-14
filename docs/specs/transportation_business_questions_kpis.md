# Transportation Network — Business Questions & KPI Dictionary

> **Release line:** v2.1 → v2.6
> **Status:** ✅ Implemented — capabilities in `src/analytics/network/service.py`, exposed through the Transportation router/dispatcher
> **Last updated:** 2026-11-14
> **Related:** [Dataset Specification](transportation_network_dataset_spec.md) · [Roadmap](../roadmap/ROADMAP_v2.x_Network_Planning_Budget.md)

---

## 1. Purpose

This document defines **what the Copilot must answer** and **how every number is calculated**. Each question maps to one deterministic capability (allow-listed intent) and to KPIs with explicit formulas. The LLM interprets the question and explains the result; it never computes a KPI.

## 2. Business questions

### 2.1 Planning and capacity (v2.3)

| ID | Question | Intent | KPIs |
|---|---|---|---|
| Q-PLN-01 | How many trips per week does route X need, and with which vehicle? | `plan_route_week` | Required trips, utilization, cost per piece |
| Q-PLN-02 | Which route-weeks exceed the planned frequency, and what does the overflow cost? | `analyze_overflow` | Overflow rate, overflow cost |
| Q-PLN-03 | Which routes run below the utilization threshold, and what happens if we change vehicle or frequency? | `find_consolidation_candidates` | Utilization, cost per piece delta |
| Q-PLN-04 | What if volume rises 10% in Q4? | `run_what_if` | Trips, cost, overflow, utilization, budget and emissions deltas |
| Q-PLN-05 | Which DC is closest to its dispatch capacity in peak weeks? | `analyze_dc_load` | DC load factor |

### 2.2 Demand and forecast (v2.2)

| ID | Question | Intent | KPIs |
|---|---|---|---|
| Q-FCT-01 | How accurate was the forecast by DC / route / store? | `forecast_accuracy` | WAPE, bias |
| Q-FCT-02 | Is the forecast systematically over or under? Where? | `forecast_bias` | Bias, tracking signal |
| Q-FCT-03 | Does the model beat a naïve forecast? | `forecast_value_added` | FVA |
| Q-FCT-04 | Which stores have the most volatile demand? | `demand_variability` | Coefficient of variation |

### 2.3 Budget and finance (v2.4)

| ID | Question | Intent | KPIs |
|---|---|---|---|
| Q-BUD-01 | What is the 2027 freight budget by month, DC and component? | `budget_summary` | Budget lines |
| Q-BUD-02 | Why does 2027 differ from 2026? | `budget_bridge` | Volume, efficiency, rate effects; adjustments |
| Q-BUD-03 | What is the impact of a 6% vs. 9% rate adjustment? | `run_what_if` | Budget delta |
| Q-BUD-04 | How much of the budget comes from management adjustments, and why? | `adjustment_report` | Adjustment share, reasons |
| Q-BUD-05 | What will a new store in state Y cost to serve? | `new_store_cost_estimate` | Cost per piece reference by UF and route profile |

### 2.4 Performance (v2.4)

| ID | Question | Intent | KPIs |
|---|---|---|---|
| Q-PRF-01 | Where did actual cost deviate from plan, and why? | `plan_vs_actual` | Variance with three-effect decomposition |
| Q-PRF-02 | How much did extras cost, and for which reasons? | `extras_analysis` | Extras share by reason |
| Q-PRF-03 | Which carrier misses the on-time target, and in which weeks? | `carrier_performance` | On-time delivery |

### 2.5 Sustainability (v2.5)

| ID | Question | Intent | KPIs |
|---|---|---|---|
| Q-SUS-01 | What are the emissions per route and per piece? | `emissions_summary` | tCO₂e, kgCO₂e per piece |
| Q-SUS-02 | How do emissions change if route X switches vehicle? | `run_what_if` | Emissions delta |

### 2.6 Inventory link (v2.6, optional)

| ID | Question | Intent | KPIs |
|---|---|---|---|
| Q-INV-01 | What safety stock does SKU X need for a 95% service level? | `safety_stock` | Safety stock, reorder point |
| Q-INV-02 | Which SKUs are below their dynamic reorder point? | `reorder_alerts` | Coverage, reorder point gap |

## 3. KPI dictionary

Notation: *V* = pieces; *T* = trips (pieces for air routes, which are priced per piece); *C* = cost (BRL); *Cap* = vehicle capacity in pieces; subscripts *b* = baseline / plan / prior year, *a* = actual / new scenario.

### 3.1 Capacity and cost

| KPI | Formula | Notes |
|---|---|---|
| Required trips (week) | `ceil(V_week / Cap)` | Road routes; air = not trip-based |
| Monthly fixed frequency | `max(min_frequency(profile), f(required_trips of the month's weeks))`, f = rounded MEAN, rounded P75 or MAX | 0 when the route has no demand in the month |
| Overflow trips | `max(0, required_trips_week − planned_frequency_month)` | When the frequency is fixed per month |
| Overflow rate | `route-weeks with overflow / total route-weeks` | |
| Overflow cost | `overflow_trips × rate × spot_premium` | |
| Utilization | `V / (T × Cap)` | Reported per trip, route-week, route-month |
| Cost per trip | `C / T` | |
| Cost per piece | `C / V` | Primary efficiency KPI |
| Cost per km | `C / (T × distance_km)` | One-way distance convention, documented |
| DC load factor | `V_dispatched_week / weekly_dispatch_capacity` | |
| Consolidation candidate | `utilization < utilization_threshold` (parameter, default 0.60) for ≥ N weeks | |

Alternating-week routes are served on alternating weeks: their monthly frequency is half that of a standard route with the same required trips.

### 3.2 Forecast accuracy

| KPI | Formula |
|---|---|
| WAPE | `Σ|A − F| / Σ A` |
| Bias | `Σ(F − A) / Σ A` (positive = over-forecast) |
| Tracking signal | `Σ(F − A) / MAD` |
| Forecast value added (FVA) | `WAPE_naive − WAPE_model` |
| Demand CV | `σ(weekly demand) / μ(weekly demand)` |

WAPE is preferred over MAPE because store-weeks can have near-zero volume.

### 3.3 Budget and variance

Cost is decomposed as a chain of three drivers:

```
C = V × (T / V) × (C / T)
     volume   efficiency   rate
```

Sequential decomposition (sums exactly to `C_a − C_b`):

| Effect | Formula |
|---|---|
| Volume effect | `(V_a − V_b) × (T/V)_b × (C/T)_b` |
| Efficiency effect | `V_a × [(T/V)_a − (T/V)_b] × (C/T)_b` |
| Rate effect | `V_a × (T/V)_a × [(C/T)_a − (C/T)_b]` |
| Adjustments | `Σ approved management adjustments` (budget only) |

Budget composition per civil month (rates are gross, tax-inclusive):

```
freight      = Σ planned_trips × rate (effective-dated × scenario adjustments), allocated by civil_month_share
overflow     = Σ overflow_trips × rate × spot_premium
extras       = (freight + overflow) × extras_rate
tax_credit   = −(freight + overflow + extras) × recoverable_credit_rate
model_budget = freight + overflow + extras + tax_credit
final_budget = model_budget + Σ approved adjustments
```

Adjustments: `MULTIPLIER` adds (value − 1) × model total in scope (non-compounding); `ABSOLUTE_BRL` adds the value, allocated by model weight in scope. Only `APPROVED` adjustments apply.

| KPI | Formula |
|---|---|
| Adjustment share | `Σ adjustments / final_budget` |
| Plan vs. actual variance | `C_actual − C_plan` and `%` |
| Extras share | `extra_cost / freight_cost` by reason |

### 3.4 Service

| KPI | Formula |
|---|---|
| On-time delivery (OTD) | `trips delivered on time / total trips` |

### 3.5 Sustainability

| KPI | Formula |
|---|---|
| Fuel (liters) per trip | `(2 × distance_km) / km_per_liter` — round trip |
| Emissions per trip (kgCO₂e) | `liters × kg_co2e_per_liter` |
| Emissions per piece | `Σ kgCO₂e / Σ V` |
| Air emissions | `pieces × kg_co2e_per_piece_air` (parameter) |

Emission factors are illustrative parameters with a documented public source.

### 3.6 Inventory (v2.6)

| KPI | Formula |
|---|---|
| Safety stock | `z(service_level) × σ_d × √LT` (constant lead time) |
| Reorder point | `d̄ × LT + safety_stock` |
| Coverage (days) | `on_hand / d̄` |

## 4. Golden Set expansion

For each release, add at least:
- 2 questions per new intent with expected numeric answers taken from deterministic outputs;
- 1 out-of-scope question per domain area (must be blocked);
- 1 question that requires citing a parameter or approved adjustment (explainability check).

Numeric fidelity rule: any number in an LLM answer must exist in the structured tool result.
