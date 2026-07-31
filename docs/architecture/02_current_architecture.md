# Current Architecture

## Purpose

This document describes the current technical architecture of the project.

Unlike the System Overview, which presents the long-term vision, this document represents the software exactly as it exists at the current stage of development.

It should evolve continuously as new modules are implemented.

---

# Current Development Stage

Current Phase:

**Infrastructure & Data Foundation**

The project currently focuses on establishing the technical foundation required for future business features.

Implemented components include:

- Modular Python architecture
- SQLite database
- Database connection layer
- Database initialization
- First ETL pipeline
- CSV ingestion
- Data persistence
- Technical documentation

---

# Current Repository Structure

```text
AI-SUPPLY-CHAIN-COPILOT/

backend/
data/
database/
│
└── inventory.db

docs/

frontend/
notebooks/
output/
sample_data/
scripts/

src/
│
├── analysis/
│
├── database/
│   ├── connection.py
│   ├── create_tables.py
│   └── load_orders.py
│
├── utils/
│
└── main.py

tests/

README.md
requirements.txt
.gitignore
```

---

# Current Software Architecture

```text
                    AI Supply Chain Engineering Portfolio

                         sample_data/pedidos.csv
                                    │
                                    ▼
                         load_orders.py (ETL)
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
          Data Extraction                    Data Transformation
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    │
                                    ▼
                           connection.py
                                    │
                                    ▼
                              SQLite Database
                                    │
                                    ▼
                             inventory.db
                                    │
                                    ▼
                              Table: pedidos
```

---

# Current Components

## connection.py

### Responsibility

Creates and manages the connection between Python and the SQLite database.

This module centralizes database access so that all future modules use a single connection implementation.

---

## create_tables.py

### Responsibility

Creates the database structure.

Current implementation creates the project tables inside SQLite.

This script is typically executed once when initializing the database or whenever structural changes are introduced.

---

## load_orders.py

### Responsibility

Implements the project's first ETL pipeline.

Current responsibilities:

- Read CSV file
- Standardize column names
- Load data into SQLite

This module demonstrates the complete ETL lifecycle:

Extract

↓

Transform

↓

Load

---

## inventory.db

### Responsibility

Stores the project's persistent data.

At the current stage, it contains the relational tables created by the initialization scripts.

---

# Current Data Flow

The current implementation follows the architecture below.

```text
CSV

↓

Pandas DataFrame

↓

Data Cleaning

↓

Column Standardization

↓

SQLite

↓

Persistent Table
```

At this stage, the project performs data ingestion and persistence only.

Business analytics have not yet been implemented.

---

# Current Database

Existing tables:

| Table | Purpose | Status |
|--------|----------|--------|
| pedidos | Stores operational order data | Active |
| inventory_analysis | Reserved for future inventory analysis | Created |

---

# Architecture Principles

The current architecture follows a few simple engineering principles.

## Single Responsibility

Each Python module performs one primary responsibility.

Examples:

- connection.py → database connection
- create_tables.py → database initialization
- load_orders.py → ETL

---

## Separation of Concerns

Business logic, database logic and data ingestion are intentionally separated into different modules.

---

## Incremental Development

New features are added without changing the existing architecture whenever possible.

The goal is to allow the system to evolve gradually while remaining organized.

---

# Known Limitations

At the current stage the project does **not** yet include:

- SQL analytical queries
- KPI calculations
- Relational joins
- Artificial Intelligence
- REST APIs
- Dashboards
- Authentication
- Cloud deployment

These components will be introduced in future milestones.

---

# Current Milestone

**Milestone 01**

Infrastructure and Data Foundation

Status:

✅ Completed