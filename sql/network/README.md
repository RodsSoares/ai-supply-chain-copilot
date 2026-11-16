# SQL analytics layer — Transportation Network (`tn_*`)

One query per business question from the
[Business Questions & KPI Dictionary](../../docs/specs/transportation_business_questions_kpis.md).
No query exists here without a question ID behind it.

The layer runs **side by side** with the Python engine. Copilot capabilities still come from
`src/analytics/network/service.py`; these queries are an independent check of the same numbers
and a direct source for BI.

| File | Question | Answers | Reconciles with |
|---|---|---|---|
| `q_prf_01_actual_weekly_by_route.sql` | Q-PRF-01 | Actual volume, trips, cost, extras and overflow per route-week (actual side of plan vs. actual) | `variance.realizado_semanal` |
| `q_prf_02_extras_by_reason.sql` | Q-PRF-02 | Extras cost by reason and share of freight | `variance.analise_extras` |
| `q_prf_03_carrier_on_time.sql` | Q-PRF-03 | On-time delivery by carrier vs. target | `variance.desempenho_transportadoras` |
| `q_prf_03_carrier_on_time_by_month.sql` | Q-PRF-03 | Months in which each carrier missed the target | `variance.desempenho_transportadoras(por_mes=True)` |
| `q_fct_01_forecast_accuracy.sql` | Q-FCT-01 / Q-FCT-02 | WAPE and bias by store, route, DC or network | `forecasting.acuracia_forecast` |
| `q_fct_04_demand_variability.sql` | Q-FCT-04 | Coefficient of variation of weekly demand by store | `forecasting.variabilidade_demanda` |

## Running a query

```python
from src.analytics.network.sql_queries import executar_consulta

executar_consulta("forecast_accuracy", forecast_version="BUDGET_2026", level="DC")
```

Parameters are bound by name (`:forecast_version`, `:level`, `:start_week`…); nothing is
concatenated into the SQL text. Defaults live in the catalog in `src/analytics/network/sql_queries.py`.

## Reconciliation

`tests/test_network_sql_queries.py` loads the synthetic network into an in-memory SQLite database,
runs every query and compares the result row by row with the Python engine. A divergence between
the two implementations fails the suite.

## Not covered here

Questions that depend on the planning or budget engine (frequency policy, overflow costing,
budget bridge, what-if, emissions) stay in Python: they apply parameterized policies that are
not a single query over the base tables.
