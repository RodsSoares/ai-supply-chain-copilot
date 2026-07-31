# Architecture Decision Log

## Purpose

This document records the most important architectural decisions made throughout the development of the AI Supply Chain Engineering Portfolio.

Its objective is to explain why certain technical choices were made, providing context for future maintenance and evolution of the project.

Only significant engineering decisions should be recorded here.

---

# Decision Log

---

## ADR-001

### Date

July 2026

### Decision

The project will be developed incrementally using independent modules instead of a monolithic architecture.

### Reason

Small modules are easier to understand, maintain and test.

This approach also reflects common software engineering practices used in enterprise applications.

### Status

✅ Adopted

---

## ADR-002

### Date

July 2026

### Decision

SQLite was selected as the project's initial database.

### Reason

SQLite requires no installation or server configuration, making it ideal for the early stages of development while still allowing the use of SQL and relational modeling.

The architecture is designed to allow future migration to PostgreSQL with minimal changes.

### Status

✅ Adopted

---

## ADR-003

### Date

July 2026

### Decision

Each business entity will have its own ETL pipeline.

Examples include:

- Orders
- Products
- Inventory
- Transportation

### Reason

Independent ETLs simplify maintenance and reduce coupling between different business processes.

### Status

✅ Adopted

---

## ADR-004

### Date

July 2026

### Decision

Database access will be centralized in a single connection module.

### Reason

All database communication should pass through `connection.py`.

This avoids duplicated code and makes future database migrations easier.

### Status

✅ Adopted

---

## ADR-005

### Date

July 2026

### Decision

The repository will prioritize software development over extensive documentation.

### Reason

The project follows the 80/20 principle:

- Approximately 80% of the effort will be dedicated to software development.
- Approximately 20% will be dedicated to documentation.

Documentation should explain architectural milestones and important decisions without slowing down product development.

### Status

✅ Adopted

---

## ADR-006

### Date

July 2026

### Decision

The business case will use synthetic data inspired by real Supply Chain operations.

### Reason

The objective is to demonstrate realistic business processes while protecting confidential corporate information.

No proprietary or confidential business data will be published in this repository.

### Status

✅ Adopted

---

# Decision Guidelines

A new decision should only be added when it significantly affects one or more of the following:

- Software architecture
- Database design
- Project organization
- Technology stack
- Development methodology

Routine implementation details should not be recorded.

---

# Current Decisions Summary

| ID | Decision | Status |
|----|----------|--------|
| ADR-001 | Modular architecture | ✅ |
| ADR-002 | SQLite database | ✅ |
| ADR-003 | Independent ETLs | ✅ |
| ADR-004 | Centralized database connection | ✅ |
| ADR-005 | 80/20 Development vs Documentation | ✅ |
| ADR-006 | Synthetic business data | ✅ |

---

# Document Information

| Property | Value |
|----------|-------|
| Document | Architecture Decision Log |
| Directory | docs/architecture |
| Version | 1.0 |
| Status | Active |
| Owner | Rodrigo Soares |
| Repository | AI Supply Chain Engineering Portfolio |
| Last Updated | July 2026 |