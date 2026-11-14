# Transportation Network — Synthetic Dataset Specification

> **Release:** v2.1.0 — Data Foundation
> **Status:** ✅ Implemented in v2.1 (`src/synthetic/network_generator.py`, `config/synthetic_network.json`)
> **Last updated:** 2026-11-14
> **Roadmap:** [ROADMAP v2.x](../roadmap/ROADMAP_v2.x_Network_Planning_Budget.md)

---

## 1. Objectives

The dataset must:

1. Be **100% synthetic** and comply with the clean-room rules (no real companies, stores, carriers, tariffs, volumes or identifiers).
2. Be **reproducible**: one seed and one `dataset_version` produce identical files.
3. Be **realistic enough to create real analytical problems**: seasonality, peaks, under-utilized routes, store openings, rate adjustments, late deliveries, noisy forecasts.
4. Support every question in the [KPI dictionary](transportation_business_questions_kpis.md) without manual patching.
5. Coexist with the v2.0.0 tables (`routes`, `vehicle_types`, `route_vehicle_options`, `route_vehicle_rates`, `demand_forecast`, `planned_trips`), which stay untouched.

## 2. Scale and horizon

| Dimension | Target |
|---|---|
| Distribution centers | 3 |
| Stores | 120 (≈ 110 active at start + ≈ 10 openings during the horizon) |
| Brands / business units | 3 (`BRAND_A`, `BRAND_B`, `BRAND_C`) |
| Channels | 2 (`STORE`, `ECOM_REPLENISHMENT`) |
| States (UF) | 14 (2 served by air) |
| Routes | 29 (25 road incl. two-driver and alternating-week, 2 air) |
| Vehicle types | 5 truck types + `AIR` mode |
| Carriers | 3 (`ATLAS`, `NOVA`, `ORION` — matching the existing synthetic contracts in `data/enterprise_documents`) |
| Demand history | 2024-W01 → 2026-W44 (148 weeks — "today" in the synthetic world is 2026-W46) |
| Forecast horizon | 2026-W01 → 2027-W52 (budget + re-forecast versions) |
| Actuals | 2025-W01 → 2026-W44 |

Volume unit: **pieces**. Each vehicle also has volumetric capacity (m³) so a future release can switch the binding constraint.

## 3. Entity model

```
tn_calendar ─┐
tn_dcs ──────┼── tn_routes ── tn_route_stops ── tn_stores
tn_carriers ─┘       │                              │
                     ├── tn_route_vehicle_options    ├── tn_demand_history
tn_vehicles ─────────┤                              └── tn_forecast
                     ├── tn_rates
                     ├── tn_trips_actual
                     └── tn_planned_trips (engine output)

tn_scenarios ── tn_parameters
             ├─ tn_management_adjustments
             └─ tn_budget_lines (engine output)
tn_emission_factors
```

## 4. Tables

Conventions: `snake_case`; dates ISO-8601; money in BRL, 2 decimals; percentages as decimals (`0.04` = 4%); weeks identified by `iso_year` + `iso_week` plus `week_start` (Monday).

### 4.1 Master data

**`tn_calendar`** — one row per ISO week.

| Column | Type | Notes |
|---|---|---|
| week_start | DATE PK | Monday |
| iso_year, iso_week | INT | |
| retail_year, retail_month, retail_week_of_month | INT | 4-5-4 retail calendar |
| civil_month_share_json | TEXT | share of the week's days in each civil month, e.g. `{"2026-03":0.43,"2026-04":0.57}` |
| season_flag | TEXT | `NORMAL`, `WINTER`, `BLACK_FRIDAY`, `CHRISTMAS`, `BACK_TO_SCHOOL` |
| holiday_count | INT | national holidays in the week |

**`tn_dcs`** — `dc_id` PK, `dc_name`, `city`, `uf`, `weekly_dispatch_capacity_pieces`, `active_from`.

**`tn_stores`** — `store_id` PK, `store_name`, `brand_set` (pipe-separated brands), `city`, `uf`, `cluster` (`S`, `M`, `L`, `XL`), `opening_date`, `closing_date` (nullable), `status`, `primary_dc_id` FK.

**`tn_carriers`** — `carrier_id` PK, `carrier_name`, `contract_doc_id` (link to RAG documents), `on_time_target`.

**`tn_vehicles`** — `vehicle_type_id` PK, `vehicle_name`, `mode` (`ROAD`/`AIR`), `capacity_pieces`, `capacity_m3`, `km_per_liter` (null for AIR), `fuel_type`.

Suggested synthetic vehicle grid:

| vehicle_type_id | vehicle_name | capacity_pieces | capacity_m3 | km_per_liter |
|---|---|---:|---:|---:|
| NV01 | VAN | 2,500 | 8 | 9.0 |
| NV02 | LIGHT_TRUCK | 6,000 | 20 | 6.5 |
| NV03 | MEDIUM_TRUCK | 12,000 | 38 | 4.8 |
| NV04 | HEAVY_TRUCK | 20,000 | 60 | 3.6 |
| NV05 | SEMI_TRAILER | 30,000 | 90 | 2.8 |
| NA01 | AIR_CARGO | n/a (priced per piece) | n/a | n/a |

**`tn_routes`** — `route_id` PK, `dc_id` FK, `carrier_id` FK, `route_type` (`STANDARD`, `ALTERNATING_WEEK`, `AIR`, `TWO_DRIVERS`), `distance_km` (one way), `stops_count`, `route_profile` (`SHORT` < 300 km, `MEDIUM` 300–800, `LONG` > 800), `active_from`, `active_to`.

**`tn_route_stops`** — `route_id`, `store_id`, `stop_sequence`, `valid_from`, `valid_to`. PK (`route_id`, `store_id`, `valid_from`).

**`tn_route_vehicle_options`** — `route_id`, `vehicle_type_id`, `is_default`.

### 4.2 Commercial data

**`tn_rates`** — effective-dated tariffs.

| Column | Type | Notes |
|---|---|---|
| route_id, vehicle_type_id | FK | |
| rate_basis | TEXT | `PER_TRIP` (road) or `PER_PIECE` (air) |
| rate_value | DECIMAL | |
| spot_premium | DECIMAL | multiplier for overflow trips, e.g. `1.35` |
| effective_from, effective_to | DATE | at least one adjustment event inside the horizon |

Rate generation: base rate = fixed cost per trip + variable cost × distance × vehicle size factor, plus noise; one annual adjustment event per carrier (e.g. +4% to +9%), on a carrier-specific date.

### 4.3 Demand

**`tn_demand_history`** — store × week × brand × channel, 2024-W01 → 2026-W44.

| Column | Type |
|---|---|
| week_start | DATE FK |
| store_id | FK |
| brand | TEXT |
| channel | TEXT |
| pieces_shipped | INT |

Generation model (per store-brand-channel series):

```
pieces = base_level(cluster, brand)
         × trend(t)                    # ±0–6% per year, store-specific
         × seasonality(week)           # winter uplift, Black Friday and Christmas peaks, January low
         × event_effect(week)          # promotions, holidays, ramp-up after store opening
         × noise                       # lognormal, CV 8–20% by cluster
```

Deliberate realism:
- New stores ramp up over 6–10 weeks after `opening_date`.
- 1–2% of store-weeks with zero or missing shipments (data-quality tests must catch and report them).
- A small set of outlier weeks (e.g. extraordinary replenishment).

**`tn_forecast`** — `forecast_version` (`BUDGET_2026`, `BUDGET_2027`, `REFORECAST_2026_Q2`…), `week_start`, `store_id`, `brand`, `channel`, `forecast_pieces`, `model_name`, `created_at`.

Budget versions simulate common planning practice: same ISO week of the previous year × store growth assumption × noise. They inherit calendar shifts (e.g. Black Friday changing week) and an optimistic bias, which gives v2.2 a real accuracy problem. Stores without a previous year use a planner estimate. Model forecasts are produced by `forecasting.gerar_forecast_modelo`.

### 4.4 Execution

**`tn_trips_actual`** — one row per executed trip, 2025-W01 → 2026-W44.

| Column | Type | Notes |
|---|---|---|
| trip_id | TEXT PK | |
| week_start, ship_date | DATE | |
| route_id, vehicle_type_id, carrier_id | FK | |
| trip_kind | TEXT | `PLANNED`, `OVERFLOW_SPOT` (re-deliveries are recorded as extras) |
| pieces | INT | |
| freight_cost | DECIMAL | |
| extra_cost | DECIMAL | |
| extra_reason | TEXT | `NONE`, `RE_DELIVERY`, `FISCAL_HOLD`, `EXTRA_HELPER`, `WAITING_TIME` |
| delivered_on_time | BOOL | carrier-specific on-time probability, lower in peak weeks |

### 4.5 Scenarios, parameters and governance

**`tn_scenarios`** — `scenario_id` PK, `scenario_name`, `scenario_type` (`BASELINE`, `BUDGET`, `WHAT_IF`), `base_scenario_id`, `forecast_version`, `description`, `created_by_role`, `created_at`, `locked` (bool).

**`tn_parameters`** — every assumption that the spreadsheet world would hide in a formula.

| Column | Type | Notes |
|---|---|---|
| scenario_id | FK | |
| parameter_key | TEXT | e.g. `extras_rate`, `rate_adjustment.ATLAS`, `seasonality.WINTER`, `tax.icms`, `tax.pis`, `tax.cofins`, `utilization_threshold`, `frequency.SHORT.L` |
| scope | TEXT | `NETWORK`, `DC:<id>`, `ROUTE:<id>`, `CARRIER:<id>` |
| value | DECIMAL / TEXT | |
| valid_from, valid_to | DATE | |
| source_note | TEXT | where the assumption comes from |

**`tn_management_adjustments`** — explicit top-down adjustments.

| Column | Type | Notes |
|---|---|---|
| adjustment_id | TEXT PK | |
| scenario_id | FK | |
| scope | TEXT | `NETWORK`, `DC:<id>`, `ROUTE:<id>`, `MONTH:<yyyy-mm>` |
| adjustment_type | TEXT | `MULTIPLIER` or `ABSOLUTE_BRL` |
| value | DECIMAL | |
| reason | TEXT | mandatory |
| requested_by_role, approved_by_role | TEXT | roles only, never names |
| approved_at | DATE | |
| status | TEXT | `PROPOSED`, `APPROVED`, `REJECTED` |

Only `APPROVED` adjustments enter the final budget. The engine always keeps model baseline and adjusted values side by side.

**`tn_emission_factors`** — `fuel_type`, `kg_co2e_per_liter`, `source_note`, `valid_from`. Values are illustrative and must cite a public reference in `source_note`.

### 4.6 Engine outputs (not generated, computed)

- `tn_planned_trips` (`planning.planejar_cenario`) — `scenario_id`, `week_start`, `route_id`, `vehicle_type_id`, `planned_trips`, `required_trips`, `overflow_trips`, `planned_pieces`, `planned_capacity`, `planned_cost`, `overflow_cost`, `explanation_json`.
- `tn_budget_lines` (`budget.orcamento`) — `scenario_id`, `civil_month`, `dc_id`, `route_id`, `cost_component` (`FREIGHT`, `OVERFLOW`, `EXTRAS`, `TAX`, `TAX_CREDIT`, `ADJUSTMENT`), `amount_brl`, `source` (`MODEL` or `ADJUSTMENT:<id>`).

## 5. Generator requirements

- Single entry point: `python scripts/generate_transportation_network.py --seed 42 --version network_v1`.
- Output: CSVs + `generation_report.md` (row counts, seasonality summary, injected anomalies, seed, version).
- Pure functions per entity; no network access; no real-world lookups.
- Parameters of the generator itself in `config/synthetic_network.json`.

## 6. Validation and reconciliation tests (v2.1 Definition of Done)

| Test | Rule |
|---|---|
| Reproducibility | Same seed and version → identical file hashes |
| Referential integrity | All FKs resolve; no orphan stores, routes or rates |
| Coverage | Every route × eligible vehicle has exactly one valid rate on every week |
| Route assignment | Each active store belongs to exactly one active route per week |
| Reconciliation | Σ store demand per route-week = route-level aggregate view |
| Calendar | 52/53-week years handled; civil-month shares of each week sum to 1 |
| Ranges | No negative pieces or costs; utilization of actual trips ≤ 1 + tolerance |
| Anomaly injection | Report lists injected anomalies; data-quality checks detect them |
| Regression | All v2.0.0 tests pass |

## 7. Clean-room checklist

- [ ] No real company, brand, store, DC, carrier or city-store combination that identifies a real network
- [ ] No real tariffs, volumes, budgets or operational constraints
- [ ] Formulas designed independently and documented in the KPI dictionary
- [ ] Synthetic names only (`DC01`, `ST0001`, `BRAND_A`, `ATLAS`…)
