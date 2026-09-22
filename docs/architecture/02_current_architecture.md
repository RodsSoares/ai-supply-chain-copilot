Current Architecture

Purpose

This document describes the current technical architecture of the AI Supply Chain Copilot after the bounded Transportation multidomain increment completed in September 2026.

The v1.1.0 cloud deployment remains the public baseline. This document focuses on the currently implemented software architecture, including Inventory and Transportation.

Cloud hosting and deployment-specific concerns are documented separately in 05_cloud_deployment.md.

Current Development Stage

The AI Supply Chain Copilot is a functional portfolio application with:

synthetic Supply Chain data;

ETL and data standardization;

SQLite relational persistence;

deterministic Inventory analytics and decision support;

deterministic Transportation planning and analytics;

configurable business rules;

REST API through FastAPI;

Power BI integration for Inventory;

multidomain AI service orchestration;

domain-specific context preparation;

Pydantic Structured Output for Transportation intent routing;

deterministic Transportation capability dispatch;

Fake and Real LLM clients;

Streamlit conversational frontend;

explicit Inventory / Transportation domain selection;

automated testing;

structured LLM evaluation;

public cloud deployment of the v1.1.0 baseline.

The architecture deliberately separates deterministic business processing from probabilistic interpretation.

Current Logical Architecture

flowchart TD

    USER[User]
    FE[Streamlit Frontend]
    DOMAIN[Explicit Domain Selection]
    API[FastAPI REST API]
    SERVICE[Multidomain AI Service]

    subgraph INVENTORY[Inventory Domain]
        INVDATA[Inventory Analytical Data]
        INVAN[Deterministic Inventory Analytics]
        INVCTX[Inventory Context]
        BI[Power BI]
        INVDATA --> INVAN
        INVAN --> INVCTX
        INVAN --> BI
    end

    subgraph TRANSPORTATION[Transportation Domain]
        TRDB[(SQLite Transportation Data)]
        ROUTER[LLM Intent Router]
        CONTRACT[Pydantic Structured Output]
        DISP[Deterministic Dispatcher]
        TRAN[SQL / Deterministic Analytics]
        TRCTX[Transportation Context]
        ROUTER --> CONTRACT
        CONTRACT -->|authorized intent| DISP
        DISP --> TRAN
        TRDB --> TRAN
        TRAN --> TRCTX
    end

    CLIENT[LLM Client]
    OAI[OpenAI API]

    USER --> FE
    FE --> DOMAIN
    DOMAIN --> API
    API --> SERVICE

    SERVICE -->|inventory| INVCTX
    SERVICE -->|transportation| ROUTER
    CONTRACT -->|out_of_scope| SERVICE
    TRCTX --> SERVICE

    SERVICE --> CLIENT
    CLIENT --> OAI
    OAI --> CLIENT
    CLIENT --> SERVICE

    SERVICE --> API
    API --> FE
    FE --> USER

The user or calling layer explicitly selects inventory or transportation.

The LLM is not used to decide which domain should handle the request. This keeps domain selection deterministic, avoids unnecessary token consumption and removes probabilistic behavior from a decision already known by the interface.

Multidomain Orchestration

The public service contract is conceptually:

responder(pergunta, dominio="inventory")

Supported domains:

inventory;

transportation.

Inventory remains the default for backward compatibility.

Inventory Path

domain=inventory → Inventory data/tool → Inventory context → system/domain prompt → explanatory LLM response

The existing Inventory behavior remains intact.

Transportation Path

domain=transportation → Transportation router → Structured Output → dispatcher → SQL/deterministic analytics → Transportation context → explanatory LLM response

The final explanatory LLM call receives the original user question so that the response remains aligned with the user's business intent.

Transportation Intent Boundary

The Transportation router answers:

What analytical capability does this Transportation question require?

The router uses an explicit structured contract rather than unrestricted free-form interpretation.

Its output may contain an authorized Transportation analytical intent and supported parameters such as route_id, or it may classify the request as out_of_scope.

out_of_scope is a guardrail: it stops execution before deterministic Transportation analytics and before the final explanatory LLM call.

Deterministic Dispatcher

The Transportation dispatcher answers:

Which authorized deterministic function executes this validated capability?

It maps the structured intent to completed deterministic analytical functions.

The dispatcher does not calculate KPIs and does not ask the LLM to calculate them.

When a supported route_id is present and the analytical result is route-grained, the dispatcher applies the bounded route filtering defined by the Transportation contract.

This preserves an explicit chain of responsibility:

Router interprets → Dispatcher selects → SQL/Analytics calculates.

Domain Context Layer

Inventory Context

The Inventory context builder supplies controlled deterministic Inventory facts to the LLM.

Transportation Context

src/ai/transportation_context.py structures the official deterministic Transportation result for downstream interpretation.

It does not recalculate metrics or invent conclusions.

The context includes domain metadata, analysis type, result metadata and the original deterministic analytical result.

API and Tool Integration

FastAPI remains the external integration contract between the frontend and backend.

Transportation uses a bounded API/tool surface. The architecture does not create one HTTP endpoint for every deterministic SQL analytical function.

Completed deterministic analytical capabilities may be invoked internally through the dispatcher when they are already inside the trusted application boundary.

This avoids infrastructure scope creep while keeping analytical capabilities explicit and testable.

Data and Persistence Architecture

The project currently contains domain-specific data paths.

Inventory

Inventory uses:

synthetic ERP-style inventory source data;

deterministic analytical processing;

output/inventory_analysis.csv as the consolidated analytical artifact;

SQLite for structured relational reference entities;

Power BI and API/AI consumers.

Transportation

Transportation uses synthetic relational and planning data in SQLite, including concepts such as:

routes;

vehicle types;

route/vehicle alternatives;

effective-dated route/vehicle tariffs;

weekly forecast demand;

derived planned trips.

Transportation analytical functions query deterministic persisted data and derived planning results to calculate authoritative KPIs and detect measurable changes.

Detailed Transportation schema, planning policy, SQL questions and analytical capabilities are documented in 06_transportation_architecture.md.

LLM Responsibility

The LLM may:

interpret a Transportation question inside an already-selected domain;

produce validated structured intent;

synthesize deterministic results;

explain drivers supported by deterministic evidence;

communicate business meaning in natural language.

The LLM must not:

select the business domain when the interface already knows it;

become the source of truth for exact KPIs;

invent unsupported causes;

bypass the dispatcher to execute arbitrary analytics;

redefine deterministic business rules.

The core principle remains:

LLM ≠ Calculator.

Architectural Responsibility Boundary

The implemented end-to-end responsibility model is:

Frontend / Calling Layer
        ↓
Explicit Domain Selection
        ↓
Inventory ---------------- Transportation
   ↓                            ↓
Deterministic Data        LLM Intent Router
   ↓                            ↓
Inventory Context         Pydantic Contract
                                ↓
                         Deterministic Dispatcher
                                ↓
                         SQL / Deterministic Analytics
                                ↓
                         Transportation Context
        └──────────────┬──────────────┘
                       ↓
                 Explanatory LLM
                       ↓
                 Business Answer
                       ↓
                     Human

Canonical compact principle:

UI defines the domain.
LLM interprets the intent.
Dispatcher selects the capability.
SQL calculates.
Analytics detects.
AI explains.
Human decides.

Testing Architecture

The project separates deterministic software correctness from probabilistic model behavior.

Automated tests cover, among other responsibilities:

Inventory backward compatibility;

multidomain service orchestration;

invalid-domain rejection;

prompt forwarding;

Structured Output client behavior;

Transportation router contracts;

out_of_scope behavior;

deterministic dispatcher mapping;

route filtering;

Transportation context construction;

Transportation API/tool integration;

deterministic Transportation analytics.

Current full regression checkpoint:

python -m pytest -q

105 passed

Real-model behavior is evaluated separately from deterministic software correctness.

A plausible LLM explanation is not evidence that the underlying analytical calculation is correct.

Current Limitations and Bounded Future Work

The application remains portfolio-grade rather than production-ready.

Production-hardening opportunities include:

managed relational persistence;

authentication and authorization;

centralized observability;

production-grade logging and alerting;

centralized secrets management;

CI/CD automation;

containerization;

scalability and resilience mechanisms;

advanced API protection;

additional AI governance controls.

Transportation-specific future extensions may include:

plan versus actual;

historical tariff-version enforcement;

explicit zero-volume policy;

ETL idempotency/upsert behavior where required;

GHG/sustainability analytics;

deeper optimization.

These are future extensions, not blockers for the current Transportation portfolio milestone.

Document Relationships

Document

Responsibility

01_system_overview.md

High-level system and business view

03_data_model.md

Global data model and persistence structure

04_decision_log.md

Significant architectural decisions

05_cloud_deployment.md

Cloud deployment architecture

06_transportation_architecture.md

Detailed bounded Transportation architecture

Document Information

Property

Value

Document

Current Architecture

Directory

docs/architecture

Baseline Application Version

v1.1.0

Current Increment

Inventory + Transportation multidomain architecture

Status

Active

Last Updated

2026-09-22