"""Schema SQLite da rede sintética de Transportation (namespace tn_*, v2.1).

As tabelas da v2.0.0 (routes, vehicle_types, demand_forecast, planned_trips...)
não são alteradas por este módulo.
"""

from src.database.connection import conectar_banco


DDL_NETWORK = {
    "tn_calendar": """
        CREATE TABLE IF NOT EXISTS tn_calendar (
            week_start TEXT PRIMARY KEY,
            week_idx INTEGER NOT NULL UNIQUE,
            iso_year INTEGER NOT NULL,
            iso_week INTEGER NOT NULL CHECK (iso_week BETWEEN 1 AND 53),
            retail_year INTEGER NOT NULL,
            retail_month INTEGER NOT NULL CHECK (retail_month BETWEEN 1 AND 12),
            retail_week_of_month INTEGER NOT NULL,
            civil_month_share_json TEXT NOT NULL,
            season_flag TEXT NOT NULL,
            holiday_count INTEGER NOT NULL
        )""",
    "tn_dcs": """
        CREATE TABLE IF NOT EXISTS tn_dcs (
            dc_id TEXT PRIMARY KEY,
            dc_name TEXT NOT NULL,
            city TEXT NOT NULL,
            uf TEXT NOT NULL,
            weekly_dispatch_capacity_pieces INTEGER NOT NULL CHECK (weekly_dispatch_capacity_pieces > 0),
            active_from TEXT NOT NULL
        )""",
    "tn_stores": """
        CREATE TABLE IF NOT EXISTS tn_stores (
            store_id TEXT PRIMARY KEY,
            store_name TEXT NOT NULL,
            brand_set TEXT NOT NULL,
            city TEXT NOT NULL,
            uf TEXT NOT NULL,
            cluster TEXT NOT NULL CHECK (cluster IN ('S', 'M', 'L', 'XL')),
            opening_date TEXT NOT NULL,
            closing_date TEXT,
            status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'PLANNED', 'CLOSED')),
            primary_dc_id TEXT NOT NULL REFERENCES tn_dcs(dc_id)
        )""",
    "tn_carriers": """
        CREATE TABLE IF NOT EXISTS tn_carriers (
            carrier_id TEXT PRIMARY KEY,
            carrier_name TEXT NOT NULL,
            contract_doc_id TEXT,
            on_time_target REAL NOT NULL CHECK (on_time_target BETWEEN 0 AND 1)
        )""",
    "tn_vehicles": """
        CREATE TABLE IF NOT EXISTS tn_vehicles (
            vehicle_type_id TEXT PRIMARY KEY,
            vehicle_name TEXT NOT NULL,
            mode TEXT NOT NULL CHECK (mode IN ('ROAD', 'AIR')),
            capacity_pieces INTEGER,
            capacity_m3 REAL,
            km_per_liter REAL,
            fuel_type TEXT NOT NULL
        )""",
    "tn_routes": """
        CREATE TABLE IF NOT EXISTS tn_routes (
            route_id TEXT PRIMARY KEY,
            dc_id TEXT NOT NULL REFERENCES tn_dcs(dc_id),
            carrier_id TEXT NOT NULL REFERENCES tn_carriers(carrier_id),
            route_type TEXT NOT NULL CHECK (route_type IN ('STANDARD', 'ALTERNATING_WEEK', 'AIR', 'TWO_DRIVERS')),
            distance_km REAL NOT NULL CHECK (distance_km > 0),
            stops_count INTEGER NOT NULL CHECK (stops_count > 0),
            route_profile TEXT NOT NULL CHECK (route_profile IN ('SHORT', 'MEDIUM', 'LONG')),
            uf TEXT NOT NULL,
            active_from TEXT NOT NULL,
            active_to TEXT
        )""",
    "tn_route_stops": """
        CREATE TABLE IF NOT EXISTS tn_route_stops (
            route_id TEXT NOT NULL REFERENCES tn_routes(route_id),
            store_id TEXT NOT NULL REFERENCES tn_stores(store_id),
            stop_sequence INTEGER NOT NULL,
            valid_from TEXT NOT NULL,
            valid_to TEXT,
            PRIMARY KEY (route_id, store_id, valid_from)
        )""",
    "tn_route_vehicle_options": """
        CREATE TABLE IF NOT EXISTS tn_route_vehicle_options (
            route_id TEXT NOT NULL REFERENCES tn_routes(route_id),
            vehicle_type_id TEXT NOT NULL REFERENCES tn_vehicles(vehicle_type_id),
            is_default INTEGER NOT NULL CHECK (is_default IN (0, 1)),
            PRIMARY KEY (route_id, vehicle_type_id)
        )""",
    "tn_rates": """
        CREATE TABLE IF NOT EXISTS tn_rates (
            route_id TEXT NOT NULL,
            vehicle_type_id TEXT NOT NULL,
            rate_basis TEXT NOT NULL CHECK (rate_basis IN ('PER_TRIP', 'PER_PIECE')),
            rate_value REAL NOT NULL CHECK (rate_value > 0),
            spot_premium REAL NOT NULL CHECK (spot_premium >= 1),
            effective_from TEXT NOT NULL,
            effective_to TEXT,
            PRIMARY KEY (route_id, vehicle_type_id, effective_from),
            FOREIGN KEY (route_id, vehicle_type_id)
                REFERENCES tn_route_vehicle_options(route_id, vehicle_type_id)
        )""",
    "tn_demand_history": """
        CREATE TABLE IF NOT EXISTS tn_demand_history (
            week_start TEXT NOT NULL REFERENCES tn_calendar(week_start),
            store_id TEXT NOT NULL REFERENCES tn_stores(store_id),
            brand TEXT NOT NULL,
            channel TEXT NOT NULL,
            pieces_shipped INTEGER NOT NULL CHECK (pieces_shipped >= 0),
            PRIMARY KEY (week_start, store_id, brand, channel)
        )""",
    "tn_forecast": """
        CREATE TABLE IF NOT EXISTS tn_forecast (
            forecast_version TEXT NOT NULL,
            week_start TEXT NOT NULL REFERENCES tn_calendar(week_start),
            store_id TEXT NOT NULL REFERENCES tn_stores(store_id),
            brand TEXT NOT NULL,
            channel TEXT NOT NULL,
            forecast_pieces INTEGER NOT NULL CHECK (forecast_pieces >= 0),
            model_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (forecast_version, week_start, store_id, brand, channel)
        )""",
    "tn_trips_actual": """
        CREATE TABLE IF NOT EXISTS tn_trips_actual (
            trip_id TEXT PRIMARY KEY,
            week_start TEXT NOT NULL REFERENCES tn_calendar(week_start),
            ship_date TEXT NOT NULL,
            route_id TEXT NOT NULL REFERENCES tn_routes(route_id),
            vehicle_type_id TEXT NOT NULL REFERENCES tn_vehicles(vehicle_type_id),
            carrier_id TEXT NOT NULL REFERENCES tn_carriers(carrier_id),
            trip_kind TEXT NOT NULL CHECK (trip_kind IN ('PLANNED', 'OVERFLOW_SPOT')),
            pieces INTEGER NOT NULL CHECK (pieces >= 0),
            freight_cost REAL NOT NULL CHECK (freight_cost >= 0),
            extra_cost REAL NOT NULL CHECK (extra_cost >= 0),
            extra_reason TEXT NOT NULL,
            delivered_on_time INTEGER NOT NULL CHECK (delivered_on_time IN (0, 1))
        )""",
    "tn_scenarios": """
        CREATE TABLE IF NOT EXISTS tn_scenarios (
            scenario_id TEXT PRIMARY KEY,
            scenario_name TEXT NOT NULL,
            scenario_type TEXT NOT NULL CHECK (scenario_type IN ('BASELINE', 'BUDGET', 'WHAT_IF')),
            base_scenario_id TEXT REFERENCES tn_scenarios(scenario_id),
            forecast_version TEXT NOT NULL,
            plan_year INTEGER NOT NULL,
            description TEXT,
            created_by_role TEXT,
            created_at TEXT NOT NULL,
            locked INTEGER NOT NULL CHECK (locked IN (0, 1))
        )""",
    "tn_parameters": """
        CREATE TABLE IF NOT EXISTS tn_parameters (
            scenario_id TEXT NOT NULL REFERENCES tn_scenarios(scenario_id),
            parameter_key TEXT NOT NULL,
            scope TEXT NOT NULL,
            value TEXT NOT NULL,
            valid_from TEXT NOT NULL,
            valid_to TEXT,
            source_note TEXT,
            PRIMARY KEY (scenario_id, parameter_key, scope, valid_from)
        )""",
    "tn_management_adjustments": """
        CREATE TABLE IF NOT EXISTS tn_management_adjustments (
            adjustment_id TEXT PRIMARY KEY,
            scenario_id TEXT NOT NULL REFERENCES tn_scenarios(scenario_id),
            scope TEXT NOT NULL,
            adjustment_type TEXT NOT NULL CHECK (adjustment_type IN ('MULTIPLIER', 'ABSOLUTE_BRL')),
            value REAL NOT NULL,
            reason TEXT NOT NULL CHECK (length(reason) > 0),
            requested_by_role TEXT NOT NULL,
            approved_by_role TEXT,
            approved_at TEXT,
            status TEXT NOT NULL CHECK (status IN ('PROPOSED', 'APPROVED', 'REJECTED'))
        )""",
    "tn_emission_factors": """
        CREATE TABLE IF NOT EXISTS tn_emission_factors (
            factor_key TEXT NOT NULL,
            unit TEXT NOT NULL,
            value REAL NOT NULL CHECK (value > 0),
            valid_from TEXT NOT NULL,
            source_note TEXT NOT NULL,
            PRIMARY KEY (factor_key, valid_from)
        )""",
}

ORDEM_CARGA = list(DDL_NETWORK.keys())


def criar_tabelas_network() -> None:
    """Cria (idempotente) todas as tabelas tn_*."""
    with conectar_banco() as conexao:
        for ddl in DDL_NETWORK.values():
            conexao.execute(ddl)


def remover_tabelas_network() -> None:
    """Remove as tabelas tn_* (ordem reversa por causa das FKs)."""
    with conectar_banco() as conexao:
        conexao.execute("PRAGMA foreign_keys = OFF")
        for tabela in reversed(ORDEM_CARGA):
            conexao.execute(f"DROP TABLE IF EXISTS {tabela}")
        conexao.execute("PRAGMA foreign_keys = ON")


if __name__ == "__main__":
    criar_tabelas_network()
    print("Tabelas tn_* criadas.")
