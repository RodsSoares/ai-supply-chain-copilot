# AI Supply Chain Copilot — Roadmap v2.x: Network Planning & Budget

> **Branch:** `feature/network-planning-budget`
> **Status:** 🟢 v2.1–v2.4 implemented · v2.5 partially implemented (Power BI pending) · v2.6 implemented as a side-by-side engine (Copilot inventory flow unchanged)
> **Last updated:** 2026-11-14
> **Related documents:**
> - [Synthetic Dataset Specification](../specs/transportation_network_dataset_spec.md)
> - [Business Questions & KPI Dictionary](../specs/transportation_business_questions_kpis.md)
> - [Transportation Architecture](../architecture/06_transportation_architecture.md)
> - [Decision Log — ADR-022](../architecture/04_decision_log.md)

---

## 1. Purpose

v2.0.0 proved that the Copilot architecture supports a second Supply Chain domain. The Transportation domain, however, still runs on a small, single-DC, route-level dataset with no history, no actuals and no financial layer.

The v2.x line turns Transportation into a **Network Planning & Budget Simulator**: a deterministic analytics engine that answers the questions a transportation planning, operations or Supply Chain analytics team actually asks — capacity, frequency, cost, budget, plan vs. actual, forecast accuracy and emissions — with the LLM explaining the results, never calculating them.

Portfolio narrative:

> A planning and budgeting problem class I solved professionally with spreadsheets, rebuilt as an auditable, testable analytics product with synthetic data, explicit assumptions, scenario versioning and an AI layer that explains — but never invents — the numbers.

## 2. Gaps this roadmap closes

| # | Gap identified in the portfolio review | Closed by |
|:-:|---|:-:|
| G1 | Supply Chain analytics depth is shallow (ABC / stockout only) | v2.2, v2.3, v2.6 |
| G2 | No measurable business impact (no plan vs. actual, no R$ story) | v2.4, v2.5 |
| G3 | No forecasting nor forecast-accuracy measurement | v2.2 |
| G4 | No public BI showcase connected to the engine | v2.5 |
| G5 | Single, flat target frequency (all route profiles = 2/week) | v2.3 |
| G6 | Peak weeks can exceed planned capacity with no cost attached (overflow) | v2.3 |
| G7 | Management adjustments live implicitly inside calculations | v2.4 |
| G8 | No scenario / what-if capability (backlog BIZ-001, BIZ-002) | v2.3, v2.4 |
| G9 | No sustainability (GHG) view | v2.5 |

## 3. Guiding principles

1. **Rebuild the problem, not the spreadsheet.** Clean-room rules from `06_transportation_architecture.md` remain mandatory: no employer names, real data, real tariffs, real identifiers or copied formulas.
2. **LLM ≠ Calculator.** Every KPI is computed in SQL / deterministic Python. The LLM selects authorized capabilities and explains results.
3. **Parameters are data, not code.** Rates, tax components, seasonality, extras and adjustments live in versioned tables or config — never as literals inside formulas.
4. **Every budget number is traceable** to volume, policy, rate, parameter or an explicitly approved management adjustment.
5. **Backward compatibility.** v2.0.0 tables, endpoints and the 105-test baseline keep passing until an ADR explicitly retires them.
6. **Analytics, not optimization.** No solvers in this line. Decision support stays rule-based, transparent and explainable.
7. **Human owns the decision.** The Copilot recommends and explains; approvals remain human.

## 4. Release plan

| Release | Status |
|:-:|:-:|
| v2.1.0 | ✅ Implemented |
| v2.2.0 | ✅ Implemented |
| v2.3.0 | ✅ Implemented |
| v2.4.0 | ✅ Implemented |
| v2.5.0 | 🟡 GHG, case study, BI data model and Golden Set v2 (18 cases + runner) done; Power BI report and the real-LLM run pending |
| v2.6.0 | ✅ Engine + capabilities; integration into the Inventory Copilot flow pending (requires Golden Set update) |

| Release | Theme | Main deliverables | Closes |
|:-:|---|---|:-:|
| **v2.1.0** | Data Foundation | Seeded synthetic network generator, new schema, ETL, reconciliation tests | base |
| **v2.2.0** | Demand & Forecast Accuracy | Baseline forecasting models, backtesting, WAPE / bias by store and route | G1, G3 |
| **v2.3.0** | Capacity, Frequency & What-if | Profile-based frequency policy, peak-aware planning, overflow cost, vehicle what-if | G1, G5, G6, G8 |
| **v2.4.0** | Budget Engine & Governance | Retail calendar, rate adjustments, extras, taxes, scenarios, management adjustments, budget bridge, plan vs. actual | G2, G7, G8 |
| **v2.5.0** | Sustainability & BI Showcase | GHG estimation, public Power BI dashboard, case study with quantified impact | G2, G4, G9 |
| **v2.6.0** | Inventory Link *(optional)* | Same forecast engine feeding safety stock and reorder point by service level | G1 |

### v2.1.0 — Data Foundation

**Goal:** a realistic, reproducible synthetic network that every later release reads from.

Deliverables:
- `scripts/generate_transportation_network.py` — deterministic generator (fixed seed, versioned `dataset_version`).
- CSVs under `data/synthetic/transportation/network/` and loaders under `src/etl/network/`.
- New tables as defined in the dataset specification (`tn_*` namespace, v2.0 tables untouched).
- Reconciliation and integrity tests (keys, ranges, sums, calendar coverage).
- Data dictionary in the dataset specification (linked from `03_data_model.md`).

Acceptance criteria:
- Same seed → byte-identical CSVs.
- Store-level demand aggregated to route level reconciles 100% with route-level views.
- Every store belongs to exactly one active route per period; every route has ≥ 1 eligible vehicle and a valid rate on every planning week.
- Seasonality, trend and event effects are visible and documented (generator report).
- All v2.0.0 tests still pass.

### v2.2.0 — Demand & Forecast Accuracy

**Goal:** prove forecasting competence with honest, measurable accuracy.

Deliverables:
- Baseline models: seasonal naïve, moving average, exponential smoothing (ETS / Holt-Winters).
- Rolling-origin backtest over the 2025 history; model selection by WAPE per route.
- Forecast versions stored in `tn_forecast` (`budget`, `reforecast_q1`…).
- Analytics: WAPE and bias by store, route, DC and month; forecast value added vs. naïve.

Acceptance criteria:
- Backtest is reproducible and documented, with a baseline-vs-model comparison table.
- Accuracy KPIs match hand-computed values in unit tests.
- Copilot answers "how accurate was the forecast for DC X / route Y?" using the deterministic tool only.

### v2.3.0 — Capacity, Frequency & What-if

**Goal:** turn the planning policy from a flat rule into a realistic, explainable decision layer.

Deliverables:
- Frequency policy by route profile and store cluster, read from parameters (replaces the flat value of 2/week).
- Peak-aware planning: monthly fixed frequency (MEAN / P75 / MAX) + weekly check of required trips; overflow trips priced at the spot rate.
- Alternating-week routes and air-mode routes as explicit route types.
- What-if engine (backlog BIZ-001): volume shock, vehicle change, frequency change, rate change — each scenario stored and comparable.
- Consolidation candidates: routes below the utilization threshold, with the cost impact of switching vehicle or frequency.

Acceptance criteria:
- Overflow rate and overflow cost are reported per route-week; zero hidden overflow.
- Every recommendation carries a structured explanation (backlog RULE-002).
- A what-if scenario never mutates the baseline scenario.

### v2.4.0 — Budget Engine & Governance

**Goal:** the financial layer that turns plans into a budget a finance team can audit.

Deliverables:
- Retail (4-5-4) calendar ↔ civil month mapping for budget allocation.
- Rate tables with effective-dated adjustments, extras policy, tax components with credit flags.
- `tn_management_adjustments`: scoped, justified, approved adjustments applied **on top of** the model baseline.
- Budget output: model baseline, adjustments and final budget shown separately.
- Budget bridge (waterfall): prior year → volume effect → efficiency effect → rate effect → adjustments → budget.
- Plan vs. actual with the same three-effect decomposition (backlog BIZ-002).

Acceptance criteria:
- Budget bridge effects sum exactly to the total variance (tested).
- Removing all management adjustments returns exactly the model baseline (tested).
- Copilot explains a variance by citing the effects and, when relevant, the approved adjustment and its reason.

### v2.5.0 — Sustainability & BI Showcase

**Goal:** make the work visible and quantify impact.

Deliverables:
- GHG estimate per trip, route and piece from distance, vehicle fuel efficiency and parameterized emission factors (illustrative values, source documented).
- Power BI report on the new model: Network, Capacity, Budget Bridge, Plan vs. Actual, Forecast Accuracy, Emissions — published publicly with screenshots in the README.
- Case study (`docs/case_studies/network_planning_budget.md`): problem → method → quantified synthetic impact (e.g. cost per piece, utilization and tCO₂e before/after a policy change).
- Golden Set extended with network/budget questions; real-LLM validation run.

Acceptance criteria:
- Dashboard numbers reconcile with API outputs.
- The case study states assumptions and limits explicitly.

### v2.6.0 — Inventory Link *(optional)*

**Goal:** close the inventory-depth gap with the same forecasting foundation.

Deliverables:
- SKU-level demand history for the inventory dataset.
- Safety stock and reorder point by target service level; cycle-service-level reporting.
- Inventory recommendations (REPOR / EXCESSO / SEM AÇÃO) using the dynamic reorder point instead of static min/max.

Implementation notes:
- `src/synthetic/inventory_demand_generator.py` + `config/inventory_policy.json` generate 104 weeks of SKU demand calibrated to the existing ERP dataset (CV and intermittency by ABC class).
- `src/analytics/inventory_policy/` computes the dynamic policy **side by side** with the static min/max: the current Copilot recommendations and the Inventory Golden Set are untouched.
- Results: `scripts/run_inventory_policy.py` → `reports/inventory/inventory_policy_summary.md`.

## 5. Definition of Done (every release)

- Deterministic logic covered by unit tests; total test count never decreases.
- New capabilities exposed through API/tool contracts and the Transportation dispatcher (allow-listed intents only).
- Golden Set updated with questions for the new capabilities.
- Documentation updated: README release table, data model, decision log (when relevant), PROJECT_AUDIT.
- Clean-room checklist reviewed.
- Tagged release with release notes.

## 6. Out of scope for v2.x

- Mathematical optimization (VRP, MILP, network design solvers).
- Real-time telematics or carrier integrations.
- Any real operational data.
- Autonomous decisions without human approval.

## 7. Risks

| Risk | Mitigation |
|---|---|
| Synthetic data looks "too clean" | Noise, missing weeks, outliers, store openings/closures and late deliveries are generated on purpose |
| Scope creep toward a standalone TMS | Bounded scope and ADR-022; optimization explicitly excluded |
| Breaking the v2.0.0 baseline | `tn_*` namespace, regression suite on every PR |
| LLM starts "doing math" | Allow-listed intents, deterministic dispatcher, Golden Set checks for numeric fidelity |
