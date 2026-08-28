      # Current Architecture

      ## Purpose

      This document describes the current technical architecture of the **AI Supply Chain Copilot v1.1.0**.

      Unlike the System Overview, which presents the application from a high-level business and system perspective, this document focuses on how the currently implemented software components are organized and interact.

      Cloud hosting and deployment-specific concerns are documented separately in `05_cloud_deployment.md`.

      ---

      # Current Development Stage

      The AI Supply Chain Copilot is currently a functional cloud-deployed portfolio application.

      The implemented architecture includes:

      - synthetic ERP-style source data;
      - ETL and data standardization;
      - SQLite relational persistence;
      - deterministic Supply Chain analytics;
      - configurable business rules;
      - decision-support logic;
      - REST API through FastAPI;
      - Power BI integration;
      - AI service orchestration;
      - deterministic context preparation;
      - Fake and Real LLM clients;
      - Streamlit conversational frontend;
      - automated testing;
      - structured LLM evaluation;
      - public cloud deployment.

      The application follows a layered architecture designed to keep deterministic business processing separated from Generative AI interpretation and presentation responsibilities.

      ---

      # Current Logical Architecture

      The current implementation contains two complementary data paths within the same application architecture.

      ```mermaid
      flowchart TD

      ERP[Synthetic ERP Inventory Dataset]

      ANALYTICS[Deterministic Analytics Layer]

      CONFIG[Business Rules Configuration]

      DECISION[Decision Support Layer]

      OUTPUT[Analytical Artifact<br/>output/inventory_analysis.csv]

      API[FastAPI REST API]

      BI[Power BI]

      AISERVICE[AI Service]

      CONTEXT[Context Builder]

      CLIENT[LLM Client]

      OPENAI[OpenAI API]

      FRONTEND[Streamlit Frontend]

      USER[User]

      MASTER[Synthetic Master / Structured Data]

      ETL[ETL / Standardization]

      DB[(SQLite)]

      RELATIONAL[Relational Consumers]

      ERP --> ANALYTICS
      CONFIG --> ANALYTICS
      ANALYTICS --> DECISION
      DECISION --> OUTPUT

      OUTPUT --> API
      OUTPUT --> BI

      API --> AISERVICE
      AISERVICE --> CONTEXT
      CONTEXT --> CLIENT

      CLIENT --> OPENAI
      OPENAI --> CLIENT

      CLIENT --> AISERVICE
      AISERVICE --> API

      USER --> FRONTEND
      FRONTEND --> API
      API --> FRONTEND
      FRONTEND --> USER

      MASTER --> ETL
      ETL --> DB
      DB --> RELATIONAL
      ```

      The current architecture contains two distinct but complementary data paths.

      The **analytical inventory path** processes the synthetic ERP inventory dataset through deterministic analytics, business rules and decision-support logic. The resulting analytical artifact is materialized in `output/inventory_analysis.csv` and consumed by the REST API, Power BI and AI capabilities.

      The **relational path** uses ETL and SQLite to maintain structured master and inventory-related entities for relational application capabilities.

      These paths coexist within the same application but currently serve different persistence and consumption responsibilities.

      ---

      # Architectural Layers

      ## Data Source Layer

      The application uses synthetic ERP-style operational data inspired by realistic Supply Chain scenarios.

      The source data is intentionally fictional and reproducible, allowing realistic analytical behavior without exposing confidential corporate information.

      ---

      ## ETL Layer

      The ETL layer currently supports the relational data path.

      Its responsibilities include:

      - source-data ingestion;
      - data cleaning;
      - column standardization;
      - type normalization;
      - transformation into application-ready structures;
      - preparation for relational persistence.

      This layer isolates source-format concerns from the structured relational model maintained in SQLite.

      The primary analytical inventory path is separate: it processes the synthetic ERP inventory dataset through deterministic analytical components and materializes its consolidated output in `output/inventory_analysis.csv`.

      ---

      ## Persistence Layer

      The current implementation uses two persistence mechanisms with different responsibilities.

      ### Analytical Artifact

      The primary inventory analytical workflow materializes its consolidated output in:

      `output/inventory_analysis.csv`

      This file contains deterministic analytical and decision-support information and is consumed by downstream capabilities including:

      - the FastAPI `/inventory` endpoint;
      - Power BI;
      - AI context preparation through backend application services.

      ### Relational Persistence

      SQLite provides the relational persistence layer for structured master and inventory-related entities.

      Current relational concepts include:

      - products;
      - warehouses;
      - inventory parameters;
      - inventory movements.

      SQLite therefore remains an implemented persistence technology, but it should not be interpreted as the source of the current 300-SKU analytical artifact consumed by `/inventory`.

      The detailed physical relational schema is documented in `03_data_model.md`.

      ---

      ## Analytics Layer

      The Analytics Layer processes the synthetic ERP inventory dataset and produces deterministic Supply Chain metrics and structured business information.

      Current analytical concepts include:

      - inventory value;
      - inventory coverage;
      - lead-time analysis;
      - rupture-risk indicators;
      - financial impact;
      - ABC-related prioritization;
      - business aggregations.

      Business-rule configuration supplies thresholds and parameters used by the deterministic analytical and decision-support logic.

      The resulting consolidated analytical information is materialized in `output/inventory_analysis.csv`.

      Exact numerical calculations remain under deterministic application control.

      ---

      ## Business Rules Configuration

      Business thresholds and classification parameters are externalized from the analytical implementation where appropriate.

      Configuration allows business behavior to evolve without requiring unnecessary modifications to analytical source code.

      This follows the principle:

      `Business Parameter Change ≠ Source-Code Change`

      Configuration is distinct from environment-specific runtime configuration and from sensitive application secrets.

      ---

      ## Decision Support Layer

      The Decision Support Layer converts analytical outputs into deterministic classifications and recommended actions.

      Current decision concepts include:

      - replenishment;
      - excess inventory treatment;
      - no-action classification;
      - rupture risk;
      - priority scoring;
      - business-action value.

      The decision layer provides structured business information that can be consumed by APIs, Business Intelligence and AI components.

      ---

      ## REST API Layer

      FastAPI exposes application capabilities through HTTP endpoints.

      The API acts as an integration boundary between the backend and external consumers.

      Current consumers include:

      - Streamlit conversational frontend;
      - AI Copilot interaction flow;
      - analytical consumers where applicable.

      The REST API contract allows consumers to interact with backend capabilities without depending on the internal implementation of analytical modules.

      ---

      ## Business Intelligence Layer

      Power BI consumes structured application outputs for visual analytical exploration.

      The dashboard provides management-oriented visualization of inventory, prioritization, risk and decision-support information.

      Business Intelligence remains a consumer of deterministic application outputs rather than the source of business calculations.

      ---

      # AI Integration Architecture

      The AI layer follows a hybrid deterministic and generative architecture.

      Its primary components are:

      ```text
      User Question
            │
            ▼
      FastAPI
            │
            ▼
      AI Service
            │
            ▼
      Deterministic Context Preparation
            │
            ▼
      LLM Client
            │
            ▼
      External LLM
            │
            ▼
      Generated Natural-Language Response
      ```

      ---

      ## AI Service

      The AI Service orchestrates the AI-assisted request flow.

      Its responsibilities include coordinating:

      - the incoming business question;
      - deterministic application information;
      - context preparation;
      - LLM client execution;
      - response delivery.

      The service separates orchestration from provider-specific LLM communication.

      ---

      ## Context Preparation

      The context layer prepares a controlled and bounded representation of business information for the LLM.

      Its responsibilities include:

      - selecting relevant deterministic information;
      - providing precomputed business aggregations;
      - preserving deterministic extrema and tie handling;
      - controlling context size;
      - structuring information for model consumption.

      This reduces dependence on probabilistic model behavior for exact business calculations.

      ---

      ## LLM Client

      The LLM client isolates communication with the configured language-model implementation.

      The architecture supports:

      - Fake LLM execution;
      - Real LLM execution.

      Fake execution supports development and controlled testing without external model consumption.

      Real execution communicates with the external LLM provider when explicitly enabled through runtime configuration.

      ---

      ## Deterministic versus Generative Responsibilities

      The architecture deliberately separates responsibilities between application code and the LLM.

      ### Deterministic Application Responsibilities

      The application remains responsible for:

      - calculations;
      - aggregations;
      - inventory metrics;
      - scoring;
      - business classifications;
      - extrema;
      - tie handling;
      - decision rules;
      - structured business context.

      ### Generative AI Responsibilities

      The LLM is primarily responsible for:

      - interpreting supplied business information;
      - synthesizing findings;
      - explaining results;
      - communicating in natural language.

      The core architectural principle is:

      **Application code determines business facts; the LLM interprets and communicates them.**

      ---

      # Conversational Frontend

      Streamlit provides the conversational presentation layer.

      The frontend is responsible for:

      - receiving user questions;
      - calling the FastAPI backend;
      - receiving structured responses;
      - presenting natural-language answers.

      The frontend does not implement the core deterministic business logic or directly access the external LLM provider.

      The backend address is supplied through environment-based runtime configuration using `API_BASE_URL`.

      This allows the same frontend implementation to communicate with either a local or cloud backend.

      ---

      # Runtime Configuration

      The application separates source code from environment-specific runtime configuration.

      Relevant runtime controls include:

      | Variable | Responsibility |
      |---|---|
      | `API_BASE_URL` | Defines the backend consumed by the frontend |
      | `LLM_MODE` | Selects Fake or Real LLM execution |
      | `LLM_REAL_ENABLED` | Explicitly enables external LLM calls |
      | `OPENAI_API_KEY` | Provides protected authentication for the external LLM provider |

      `OPENAI_API_KEY` is treated as a secret rather than ordinary configuration and remains isolated from source code and the frontend.

      Detailed deployment and secret-handling architecture is documented in `05_cloud_deployment.md`.

      ---

      # Current End-to-End Data Flow

      The current implementation contains two complementary data flows with different responsibilities.

      ## Analytical Inventory Flow

      The primary analytical workflow is:

      ```text
      Synthetic ERP Inventory Dataset
            │
            ▼
      Deterministic Analytics
            │
            ▼
      Business Rules
            │
            ▼
      Decision Support
            │
            ▼
      output/inventory_analysis.csv
      ```

      The resulting analytical artifact supports multiple downstream consumers.

      ### REST API

      ```text
      output/inventory_analysis.csv
            │
            ▼
      FastAPI /inventory
            │
            ▼
      Structured JSON Response
      ```

      ### Business Intelligence

      ```text
      output/inventory_analysis.csv
            │
            ▼
      Power BI
            │
            ▼
      Business User
      ```

      ### Conversational AI

      ```text
      User
      │
      ▼
      Streamlit
      │
      ▼
      FastAPI
      │
      ▼
      AI Service
      │
      ▼
      Deterministic Context Preparation
      │
      ▼
      LLM Client
      │
      ▼
      External LLM
      │
      ▼
      FastAPI
      │
      ▼
      Streamlit
      │
      ▼
      User
      ```

      The AI flow consumes deterministic application information rather than using the LLM as the source of business calculations.

      ---

      ## Relational Data Flow

      The relational workflow is:

      ```text
      Synthetic Master / Structured Data
            │
            ▼
      ETL / Standardization
            │
            ▼
      SQLite
            │
            ▼
      Relational Consumers
      ```

      SQLite maintains structured master and inventory-related entities independently from the primary analytical inventory artifact.

      For example, relational application capabilities such as product retrieval can consume data directly from SQLite.

      ---

      ## Data-Flow Boundary

      The two paths currently coexist but should not be represented as a single sequential pipeline.

      The analytical path is centered on:

      `Synthetic ERP Inventory → Analytics → Decision Support → inventory_analysis.csv`

      The relational path is centered on:

      `Structured Data → ETL → SQLite`

      Both remain deterministic application components and can evolve independently while serving different application responsibilities.

      ---

      # Testing and Validation Architecture

      Automated testing is part of the current engineering architecture rather than an isolated final activity.

      The current automated suite validates:

      - deterministic modules;
      - API behavior;
      - AI service orchestration;
      - context controls;
      - LLM client safeguards.

      The current release is validated by **42 automated tests**.

      Real LLM behavior was additionally evaluated through a structured Golden Set and comparative multi-model executions.

      This separates two validation concerns:

      - deterministic software correctness;
      - probabilistic LLM behavior.

      Cloud end-to-end validation adds a third concern by confirming that independently deployed components are correctly connected.

      ---

      # Cloud Runtime Architecture

      The current application is deployed through independent managed services.

      ```text
      GitHub
      │
      ├──────────────► Streamlit Community Cloud
      │                         │
      │                         ▼
      │                       User
      │
      └──────────────► Render / FastAPI
                                    │
                                    ▼
                        Application Layers
                                    │
                                    ▼
                              OpenAI API
      ```

      The public runtime flow is:

      `User → Streamlit Community Cloud → FastAPI on Render → Application Layers → OpenAI API → FastAPI → Streamlit → User`

      The local development machine is not required for the deployed application to remain accessible.

      Detailed cloud architecture is documented in:

      [`05_cloud_deployment.md`](05_cloud_deployment.md)

      ---

      # Architecture Principles

      The current implementation follows these principles:

      ## Separation of Concerns

      Data ingestion, persistence, analytics, decision support, API integration, AI orchestration and presentation have distinct responsibilities.

      ## Single Responsibility

      Modules and layers are designed around focused responsibilities.

      ## Low Coupling

      Components interact through explicit interfaces and contracts rather than unnecessary knowledge of internal implementations.

      ## High Cohesion

      Related functionality remains grouped within the appropriate architectural layer.

      ## Deterministic Business Logic

      Exact business calculations and classifications remain under application control.

      ## Configuration over Hardcoding

      Business and environment-specific values are externalized where appropriate.

      ## API-based Integration

      Presentation layers communicate with backend capabilities through explicit REST contracts.

      ## Incremental Evolution

      New capabilities extend the existing architecture rather than requiring repeated redesign of the complete system.

      ---

      # Current Architectural Boundaries

The current architecture separates responsibilities across two data paths that converge at application integration and consumption boundaries.

```text
                    ┌─────────────────────────────┐
                    │ Analytical Inventory Path   │
                    │                             │
Synthetic ERP ─────►│ Analytics                   │
                    │      ↓                      │
                    │ Decision Support            │
                    │      ↓                      │
                    │ Analytical Artifact         │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                         Integration / API
                           │             │
                           ▼             ▼
                    Business BI     AI Orchestration
                                         │
                                         ▼
                                    Presentation


                    ┌─────────────────────────────┐
                    │ Relational Data Path        │
                    │                             │
Structured Data ───►│ ETL / Standardization      │
                    │      ↓                      │
                    │ SQLite                      │
                    │      ↓                      │
                    │ Relational Consumers        │
                    └─────────────────────────────┘

The analytical and relational paths have different persistence and processing responsibilities but remain part of the same application architecture.

These boundaries are intended to support future evolution of individual technologies without unnecessarily changing unrelated layers.

Examples include:

- SQLite → managed relational database;
- analytical CSV artifact → managed analytical persistence;
- Streamlit → alternative frontend technology;
- current LLM provider/model → alternative provider or model;
- current managed hosting → alternative cloud infrastructure.

Such changes may require adapter, persistence or configuration changes while preserving the application's core business architecture.

      ---

      # Current Limitations

      Version v1.1.0 is a functional portfolio-grade architecture rather than a production-ready enterprise system.

      Current production-hardening opportunities include:

      - managed relational persistence;
      - authentication and authorization;
      - centralized observability;
      - production-grade logging and alerting;
      - centralized secrets management;
      - CI/CD automation;
      - containerization;
      - scalability and resilience mechanisms;
      - advanced API protection;
      - additional AI governance controls.

      These limitations are architectural evolution opportunities rather than blockers for the current portfolio objective.

      ---

      # Document Relationships

      This document should be read together with:

      | Document | Responsibility |
      |---|---|
      | `01_system_overview.md` | High-level system and business view |
      | `03_data_model.md` | Data model and persistence structure |
      | `04_decision_log.md` | Significant architectural decisions |
      | `05_cloud_deployment.md` | Detailed cloud deployment architecture |

      ---

      # Document Information

      | Property | Value |
      |---|---|
      | Document | Current Architecture |
      | Directory | `docs/architecture` |
      | Application Version | v1.1.0 |
      | Status | Active |
      | Last Updated | August 2026 |