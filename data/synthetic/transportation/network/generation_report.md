# Synthetic Network — Generation Report

- **dataset_version:** `network_v1`
- **seed:** `42`
- **data:** 100% synthetic — no real companies, stores, carriers, tariffs or volumes.

## Row counts

| Table | Rows |
|---|---:|
| `tn_calendar` | 209 |
| `tn_dcs` | 3 |
| `tn_stores` | 120 |
| `tn_carriers` | 3 |
| `tn_vehicles` | 6 |
| `tn_routes` | 29 |
| `tn_route_stops` | 120 |
| `tn_route_vehicle_options` | 83 |
| `tn_rates` | 249 |
| `tn_demand_history` | 30,610 |
| `tn_forecast` | 22,733 |
| `tn_trips_actual` | 5,679 |
| `tn_scenarios` | 2 |
| `tn_parameters` | 17 |
| `tn_management_adjustments` | 3 |
| `tn_emission_factors` | 3 |

## Injected anomalies (tn_demand_history)

| Type | Rows |
|---|---:|
| ZERO_SHIPMENT | 222 |
| MISSING_ROW | 156 |
| OUTLIER | 92 |

## Network shape

- Route types: {'AIR': 2, 'ALTERNATING_WEEK': 2, 'STANDARD': 19, 'TWO_DRIVERS': 6}
- Route profiles: {'LONG': 12, 'MEDIUM': 9, 'SHORT': 8}
- Store status: {'ACTIVE': 115, 'CLOSED': 2, 'PLANNED': 3}
