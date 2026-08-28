# Architecture Decision Log

## Purpose

This document records the most important architectural decisions made throughout the development of the AI Supply Chain Copilot.

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

## ADR-007

### Date

August 2026

### Decision

Business rules and analytical thresholds will be externalized from the core analytical implementation whenever appropriate.

### Reason

Business parameters may evolve without requiring changes to the underlying source code.

Separating configurable business behavior from implementation logic improves maintainability and reduces unnecessary hardcoding.

### Status

✅ Adopted

---

## ADR-008

### Date

August 2026

### Decision

The application will expose its analytical and decision-support capabilities through a REST API implemented with FastAPI.

### Reason

The REST API establishes an explicit integration contract between backend capabilities and external consumers.

This reduces coupling and allows presentation or integration layers to evolve without requiring direct access to internal application modules.

### Status

✅ Adopted

---

## ADR-009

### Date

August 2026

### Decision

Exact business calculations and classifications will remain under deterministic application control rather than being delegated to the LLM.

### Reason

Large Language Models are probabilistic and should not be treated as the authoritative calculation engine for exact business information.

Counts, aggregations, extrema, tie handling, scores, classifications and other deterministic facts are calculated by application code before being supplied to the model.

The LLM is primarily responsible for interpretation, synthesis, explanation and natural-language communication.

### Status

✅ Adopted

---

## ADR-010

### Date

August 2026

### Decision

The AI integration will use a dedicated orchestration layer with controlled context preparation and isolated LLM client implementations.

### Reason

Separating orchestration, deterministic context preparation and provider communication improves maintainability and testability.

The architecture also supports Fake and Real LLM execution modes without requiring changes to the higher business layers.

### Status

✅ Adopted

---

## ADR-011

### Date

August 2026

### Decision

Real LLM behavior will be evaluated separately from deterministic software correctness.

### Reason

Traditional automated tests and probabilistic model evaluation address different quality concerns.

The deterministic application is validated through automated tests, while LLM behavior is evaluated through a structured Golden Set and comparative real-model executions.

This prevents model variability from being confused with deterministic software defects.

### Status

✅ Adopted

---

## ADR-012

### Date

August 2026

### Decision

The conversational frontend will remain separated from backend business and AI logic and will consume application capabilities through the REST API contract.

### Reason

Separating presentation from backend responsibilities reduces coupling and allows the frontend technology to evolve independently.

Streamlit therefore acts as an API client rather than becoming the location of Supply Chain calculations or LLM orchestration.

### Status

✅ Adopted

---

## ADR-013

### Date

August 2026

### Decision

Environment-specific runtime values will be externalized from source code.

### Reason

The same application codebase must support local and cloud execution without requiring environment-specific modifications to core application logic.

Values such as backend addresses and LLM execution controls can therefore vary through runtime configuration.

Sensitive credentials remain treated separately as secrets.

### Status

✅ Adopted

---

## ADR-014

### Date

August 2026

### Decision

Sensitive external-provider credentials will remain isolated from source code, the public repository and the frontend.

### Reason

Credentials such as `OPENAI_API_KEY` provide authenticated access to external services and may generate real consumption and cost.

The credential is therefore required only by the backend component responsible for communicating with the external LLM provider.

### Status

✅ Adopted

---

## ADR-015

### Date

August 2026

### Decision

The Streamlit frontend and FastAPI backend will be deployed as independent cloud services.

### Reason

Independent deployment preserves the existing separation between presentation and backend responsibilities.

The frontend communicates with the backend through the established REST API contract, allowing each component to evolve independently.

The additional distributed-system complexity is accepted as a trade-off for clearer architectural boundaries and deployment flexibility.

### Status

✅ Adopted

---

## ADR-016

### Date

August 2026

### Decision

SQLite will be retained for the v1.1.0 cloud deployment.

### Reason

The objective of the v1.1.0 milestone is to validate cloud deployment, public accessibility and distributed end-to-end integration without introducing an unnecessary database migration at the same time.

The current relational workload is synthetic, controlled and limited in scope, making SQLite sufficient for the relational persistence responsibilities required by the portfolio-grade deployment.

A managed relational database remains a future production-hardening evolution.

### Status

✅ Adopted

---

## ADR-017

### Date

August 2026

### Decision

The initial cloud deployment will use managed application-hosting services rather than lower-level infrastructure management.

### Reason

Managed hosting allows the project to demonstrate practical cloud deployment and distributed application integration while remaining focused on business architecture, data, automation and AI.

Lower-level infrastructure technologies should be introduced only when they solve a requirement that exists in the project.

### Status

✅ Adopted

---

## ADR-018

### Date

August 2026

### Decision

Cloud deployment and production hardening will be treated as separate architectural milestones.

### Reason

A publicly accessible cloud application is not automatically production-ready.

The v1.1.0 milestone validates deployment and distributed integration.

Production concerns such as managed persistence, authentication, authorization, observability, centralized secrets management, scalability, resilience and CI/CD automation remain separate future evolutions.

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
|---|---|---|
| ADR-001 | Modular architecture | ✅ |
| ADR-002 | SQLite database | ✅ |
| ADR-003 | Independent ETLs | ✅ |
| ADR-004 | Centralized database connection | ✅ |
| ADR-005 | 80/20 Development vs Documentation | ✅ |
| ADR-006 | Synthetic business data | ✅ |
| ADR-007 | Externalized business-rule configuration | ✅ |
| ADR-008 | REST API integration contract | ✅ |
| ADR-009 | Deterministic ownership of business calculations | ✅ |
| ADR-010 | Modular AI orchestration architecture | ✅ |
| ADR-011 | Separate LLM behavioral evaluation | ✅ |
| ADR-012 | Frontend/backend separation | ✅ |
| ADR-013 | Environment-based runtime configuration | ✅ |
| ADR-014 | Backend secret isolation | ✅ |
| ADR-015 | Independent cloud deployment | ✅ |
| ADR-016 | SQLite retained for v1.1.0 | ✅ |
| ADR-017 | Managed cloud hosting | ✅ |
| ADR-018 | Deployment separated from production hardening | ✅ |

---

# Document Information

| Property | Value |
|----------|-------|
| Document | Architecture Decision Log |
| Directory | docs/architecture |
| Version | 1.1 |
| Status | Active |
| Owner | Rodrigo Soares |
| Repository | AI Supply Chain Copilot |
| Last Updated | August 2026 |