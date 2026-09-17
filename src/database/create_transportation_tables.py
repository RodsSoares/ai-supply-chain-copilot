"""Criação das tabelas do domínio Transportation."""

from src.database.connection import conectar_banco


def criar_tabela_routes(cursor):
    """Cria a tabela de rotas."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS routes (
            route_id TEXT NOT NULL PRIMARY KEY,
            origin_id TEXT NOT NULL,
            destination_id TEXT NOT NULL,
            distance_km REAL NOT NULL CHECK (distance_km >= 0)
        )
        """
    )


def criar_tabela_vehicle_types(cursor):
    """Cria a tabela de tipos de veículos."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vehicle_types (
            vehicle_type_id TEXT NOT NULL PRIMARY KEY,
            vehicle_name TEXT NOT NULL,
            capacity_pieces INTEGER NOT NULL CHECK (capacity_pieces > 0)
        )
        """
    )


def criar_tabela_route_vehicle_options(cursor):
    """Cria as combinações operacionais válidas entre rota e veículo."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS route_vehicle_options (
            route_id TEXT NOT NULL,
            vehicle_type_id TEXT NOT NULL,

            PRIMARY KEY (route_id, vehicle_type_id),

            FOREIGN KEY (route_id)
                REFERENCES routes(route_id),

            FOREIGN KEY (vehicle_type_id)
                REFERENCES vehicle_types(vehicle_type_id)
        )
        """
    )


def criar_tabela_route_vehicle_rates(cursor):
    """Cria o histórico de tarifas por combinação rota e veículo."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS route_vehicle_rates (
            route_id TEXT NOT NULL,
            vehicle_type_id TEXT NOT NULL,
            effective_from TEXT NOT NULL,
            effective_to TEXT,
            rate_per_trip REAL NOT NULL CHECK (rate_per_trip > 0),

            PRIMARY KEY (
                route_id,
                vehicle_type_id,
                effective_from
            ),

            FOREIGN KEY (route_id)
                REFERENCES routes(route_id),

            FOREIGN KEY (vehicle_type_id)
                REFERENCES vehicle_types(vehicle_type_id)
        )
        """
    )


def criar_tabela_forecast_raw(cursor):
    """Cria a tabela de forecast semanal recebido da fonte."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS forecast_raw (
            year INTEGER NOT NULL,
            week INTEGER NOT NULL CHECK (week BETWEEN 1 AND 53),
            route_id TEXT NOT NULL,
            forecast_pieces INTEGER NOT NULL CHECK (forecast_pieces >= 0),

            PRIMARY KEY (year, week, route_id),

            FOREIGN KEY (route_id)
                REFERENCES routes(route_id)
        )
        """
    )


def criar_tabela_demand_forecast(cursor):
    """Cria a tabela canônica de forecast semanal por rota."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS demand_forecast (
            week_start TEXT NOT NULL,
            route_id TEXT NOT NULL,
            forecast_pieces INTEGER NOT NULL CHECK (forecast_pieces >= 0),
            PRIMARY KEY (week_start, route_id),
            FOREIGN KEY (route_id) REFERENCES routes(route_id)
        )
        """
    )


def criar_tabela_planned_trips(cursor):
    """Cria a tabela de viagens planejadas."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS planned_trips (
            trip_id TEXT NOT NULL PRIMARY KEY,
            week_start TEXT NOT NULL,
            route_id TEXT NOT NULL,
            vehicle_type_id TEXT NOT NULL,
            planned_pieces INTEGER NOT NULL CHECK (planned_pieces > 0),
            planned_capacity INTEGER NOT NULL CHECK (planned_capacity > 0),
            planned_cost REAL NOT NULL CHECK (planned_cost > 0),

            FOREIGN KEY (route_id)
                REFERENCES routes(route_id),

            FOREIGN KEY (vehicle_type_id)
                REFERENCES vehicle_types(vehicle_type_id)
        )
        """
    )


def criar_tabelas_transportation():
    """Cria todas as tabelas iniciais do domínio Transportation."""
    with conectar_banco() as conexao:
        cursor = conexao.cursor()

        criar_tabela_routes(cursor)
        criar_tabela_vehicle_types(cursor)
        criar_tabela_route_vehicle_options(cursor)
        criar_tabela_route_vehicle_rates(cursor)
        criar_tabela_forecast_raw(cursor)
        criar_tabela_demand_forecast(cursor)
        criar_tabela_planned_trips(cursor)

        conexao.commit()
        

if __name__ == "__main__":
    criar_tabelas_transportation()


