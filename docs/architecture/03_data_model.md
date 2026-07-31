# Module Relationships

## Purpose

This document describes the responsibilities and interactions between the current Python modules.

Its objective is to explain how the software is organized internally and how each component collaborates with the others.

Unlike the Current Architecture document, this file focuses specifically on the Python codebase.

---

# Current Modules

```text
src/

├── main.py
│
├── database/
│   ├── connection.py
│   ├── create_tables.py
│   └── load_orders.py
│
├── analysis/
│
└── utils/
```

---

# Module Dependency Diagram

```text
                    main.py
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
create_tables.py                 load_orders.py
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
                 connection.py
                        │
                        ▼
                  SQLite Database
                        │
                        ▼
                  inventory.db
```

---

# Module Responsibilities

## main.py

### Responsibility

Acts as the application's entry point.

Its purpose is to orchestrate the execution of the project's modules.

At the current stage, its responsibilities are intentionally minimal.

Future versions will coordinate:

- ETL execution
- KPI generation
- AI services
- Dashboards
- APIs

---

## connection.py

### Responsibility

Provides a centralized connection to the SQLite database.

Instead of every module opening its own database connection, all database communication passes through this module.

Advantages:

- Single source of truth
- Easier maintenance
- Consistent database access

---

## create_tables.py

### Responsibility

Creates the project's relational database structure.

Current responsibilities include:

- Creating tables
- Initializing the database

Future responsibilities may include:

- Schema updates
- Database migrations

---

## load_orders.py

### Responsibility

Implements the first ETL pipeline.

Current workflow:

1. Read CSV file
2. Load data into Pandas
3. Standardize column names
4. Persist data into SQLite

This module represents the project's first complete data ingestion pipeline.

---

## inventory.db

### Responsibility

Stores the project's persistent information.

The database currently contains the initial relational structure required by the application.

Future modules will expand its contents with additional business entities.

---

# Current Module Interactions

The current execution flow is relatively simple.

```text
main.py

↓

load_orders.py

↓

connection.py

↓

SQLite
```

Database initialization follows a similar path.

```text
main.py

↓

create_tables.py

↓

connection.py

↓

SQLite
```

---

# Dependency Matrix

| Module | Uses | Purpose |
|---------|------|----------|
| main.py | create_tables.py | Application orchestration |
| main.py | load_orders.py | Execute ETL |
| create_tables.py | connection.py | Database initialization |
| load_orders.py | connection.py | Persist ETL results |
| connection.py | SQLite | Database communication |

---

# Design Decisions

## Single Responsibility Principle

Each module performs one primary responsibility.

Examples:

- Database connection
- Database creation
- ETL

Responsibilities are intentionally separated.

---

## Loose Coupling

Modules communicate through well-defined interfaces instead of sharing internal implementation details.

This makes future maintenance significantly easier.

---

## High Cohesion

Each module groups together closely related functionality.

For example:

load_orders.py contains only ETL-related logic.

Database connection logic is intentionally isolated.

---

# Future Module Evolution

The architecture has been designed to accommodate new modules without changing the existing structure.

Examples of future modules include:

```text
analysis/

├── inventory_analysis.py
├── transportation_analysis.py
├── demand_forecast.py
└── kpi_engine.py
```

```text
database/

├── load_products.py
├── load_inventory.py
├── load_transportation.py
└── migrations.py
```

```text
api/

├── routes.py
├── services.py
└── auth.py
```

Each new module should preserve the same architectural principles established in the current implementation.

---

# Module Evolution Strategy

The project adopts incremental modular growth.

Instead of creating large files with multiple responsibilities, new functionality will be introduced through independent modules.

This approach provides:

- Better readability
- Easier testing
- Improved maintainability
- Lower coupling
- Higher scalability

---

# Current Assessment

Current architecture demonstrates:

✅ Modular organization

✅ Clear separation of responsibilities

✅ Reusable database connection

✅ Independent ETL implementation

Although still relatively small, the architecture already follows software engineering practices commonly found in production systems.

---

# Document Information

| Property | Value |
|----------|-------|
| Document | Module Relationships |
| Directory | docs/architecture |
| Version | 1.0 |
| Status | Active |
| Owner | Rodrigo Soares |
| Repository | AI Supply Chain Engineering Portfolio |
| Last Updated | July 2026 |
| Next Review | After Milestone 02 |