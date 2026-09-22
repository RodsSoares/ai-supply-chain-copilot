AI Supply Chain Copilot — System Overview

Purpose

This document provides a high-level overview of the AI Supply Chain Copilot v1.1.0.

The project is an end-to-end business application inspired by real-world Supply Chain planning and operational challenges, using synthetic data to preserve corporate confidentiality.

Its objective is to demonstrate how operational data can be transformed into structured analytics, deterministic decision support, Business Intelligence and AI-assisted business interpretation within a modular software architecture.

This document focuses on the system as a whole. Detailed implementation architecture and cloud deployment are documented separately.

Business Problem

Supply Chain operations may contain large volumes of inventory, consumption, coverage, lead-time and supplier data.

Having this data available does not necessarily mean that decision-ready information is immediately available.

The AI Supply Chain Copilot addresses this problem by combining deterministic analytical processing with a conversational AI interface capable of helping users interpret the resulting business context.

The system is designed around a fundamental separation:

Deterministic application components calculate and classify business information, while Generative AI interprets, synthesizes and communicates that information in natural language.

System Capabilities

The current application integrates the following capabilities:

synthetic ERP-style data ingestion;

ETL and data standardization;

relational persistence with SQLite;

two bounded Supply Chain analytical domains: Inventory and Transportation;

deterministic Inventory and Transportation analytics;

configurable business rules;

deterministic risk and priority classification;

decision-support outputs;

Power BI visualization;

REST API integration through FastAPI;

controlled context preparation for Generative AI;

Fake and Real LLM execution modes;

conversational interaction through Streamlit;

automated testing;

structured LLM evaluation;

public cloud deployment.

High-Level Architecture

flowchart TD

    USER[User]
    FRONTEND[Streamlit Frontend]
    DOMAIN[Explicit Domain Selection]

    INV[Inventory Domain]
    TR[Transportation Domain]

    INVDET[Inventory Deterministic Analytics]
    TRROUTER[Transportation Intent Router<br/>Pydantic Structured Output]
    TRDISP[Transportation Dispatcher]
    TRDET[Transportation SQL / Deterministic Analytics]

    INVCTX[Inventory Context]
    TRCTX[Transportation Context]

    AI[Multidomain AI Service]
    LLM[LLM Client]
    OPENAI[OpenAI API]

    BI[Power BI]
    API[FastAPI REST API]

    USER --> FRONTEND
    FRONTEND --> DOMAIN
    DOMAIN -->|inventory| INV
    DOMAIN -->|transportation| TR

    INV --> INVDET
    INVDET --> INVCTX
    INVDET --> BI

    TR --> TRROUTER
    TRROUTER -->|authorized intent| TRDISP
    TRROUTER -->|out_of_scope| AI
    TRDISP --> TRDET
    TRDET --> TRCTX

    INVCTX --> AI
    TRCTX --> AI
    AI --> LLM
    LLM --> OPENAI
    OPENAI --> LLM
    LLM --> AI

    FRONTEND --> API
    API --> AI
    AI --> API
    API --> FRONTEND

The Copilot now demonstrates a multidomain Supply Chain architecture.

The user explicitly selects the business domain in the calling layer. Domain selection is therefore deterministic and does not consume an LLM call.

Inventory preserves the established analytical path based on deterministic inventory analytics, decision-support information and controlled context preparation.

Transportation is a bounded architectural extensibility case. Inside the already-selected Transportation domain, an LLM router interprets the analytical intent through Pydantic Structured Output. A deterministic dispatcher then selects an authorized analytical capability, SQL and deterministic analytics calculate the authoritative result, and the LLM explains that result in business language.

Transportation is not a standalone product. It exists to demonstrate that the Copilot can support a second Supply Chain analytical domain without breaking Inventory or duplicating the complete application architecture.

The compact responsibility principle is:

UI defines the domain. LLM interprets the intent. Dispatcher selects the capability. SQL calculates. Analytics detects. AI explains. Human decides.

Core Architectural Layers

Data and ETL

The application uses synthetic data to represent realistic Supply Chain scenarios while protecting confidential corporate information.

The current architecture contains two distinct data-processing responsibilities.

For the primary inventory analytical path, the synthetic ERP inventory dataset provides the operational information required by the deterministic analytics pipeline.

Separately, ETL and standardization processes support the relational data path used to populate structured entities maintained in SQLite.

Persistence

The current architecture uses two forms of persisted application data for different purposes.

The primary analytical workflow materializes its consolidated output in:

output/inventory_analysis.csv

This analytical artifact is consumed by the /inventory REST API endpoint and supports downstream Business Intelligence and AI capabilities.

SQLite provides a separate relational persistence layer for structured master and inventory-related entities.

The two persistence mechanisms currently coexist and should not be interpreted as a single sequential pipeline.

Analytics

The analytical layer transforms the synthetic ERP inventory dataset into deterministic Supply Chain metrics and structured decision-support information.

Examples include inventory value, coverage, lead-time analysis and operational risk indicators.

The resulting analytical information is materialized in output/inventory_analysis.csv for downstream consumption.

Exact numerical calculations remain under deterministic application control rather than being delegated to the LLM.

Business Rules and Decision Support

Configurable business rules convert analytical information into deterministic classifications and recommended actions.

Critical calculations and classifications remain under application control rather than being delegated to the LLM.

REST API

FastAPI exposes application capabilities through HTTP endpoints and acts as the integration contract between backend services and external consumers.

This allows presentation layers to consume backend capabilities without depending directly on their internal implementation.

Business Intelligence

Power BI provides analytical visualization and management-oriented exploration of the structured outputs produced by the deterministic pipeline.

AI Integration

The AI layer orchestrates the preparation of controlled business context and communication with the configured LLM client.

The application supports Fake and Real LLM execution modes, allowing controlled development, testing and external model usage.

The external LLM is used primarily for:

interpretation;

synthesis;

explanation;

natural-language communication.

Exact calculations, business rules, aggregations and classifications remain deterministic.

Conversational Frontend

Streamlit provides the public conversational interface.

The frontend communicates with the backend through the REST API rather than containing the application's core business or AI logic.

End-to-End Business Flow

The application currently supports two analytical domains behind the same Copilot boundary.

Inventory Flow

User → Streamlit → Inventory selected → FastAPI → Inventory deterministic data/context → LLM → Business Answer

Inventory remains backward compatible with the original Copilot behavior and continues to use deterministic business facts as the source of truth.

Transportation Flow

User → Streamlit → Transportation selected → FastAPI → Structured Intent Router → Deterministic Dispatcher → SQL / Analytics → Transportation Context → LLM → Business Answer

The LLM does not select Inventory versus Transportation. That decision is explicit in the frontend/calling layer.

Within Transportation, the router is allowed to interpret the analytical intent, but it cannot directly calculate authoritative KPIs. The dispatcher maps the validated intent to an authorized deterministic capability.

An out_of_scope intent stops execution before Transportation analytics and before the explanatory LLM call.

Relational and Analytical Data Flows

The project continues to use multiple data representations according to responsibility.

Inventory retains its analytical artifact and relational reference-data paths.

Transportation adds a relational analytical model in SQLite for routes, vehicle types, route/vehicle alternatives and tariffs, forecast demand, derived planning results and deterministic Transportation analytics.

Shared Architectural Principle

Across both domains:

Deterministic application components establish business facts. Generative AI interprets and communicates those facts.

The multidomain increment extends this principle rather than replacing it.

AI Design Principle

The AI Supply Chain Copilot follows a hybrid deterministic and generative architecture.

The LLM is not treated as the system of record or as the primary calculation engine.

Instead:

Application code determines facts.

The LLM communicates and interprets those facts.

This design reduces the risk of delegating exact business calculations to probabilistic model behavior while preserving the flexibility of natural-language interaction.

The architecture was validated through automated testing, Golden Set evaluation and comparative real-model execution before the public cloud deployment milestone.

Deployment Overview

Version v1.1.0 is publicly deployed through a distributed cloud architecture.

The main runtime topology is:

User → Streamlit Community Cloud → FastAPI on Render → Application Layers → OpenAI API → FastAPI → Streamlit → User

GitHub acts as the version-controlled source for the deployed application components.

Environment-specific runtime configuration allows the same core codebase to operate locally and in cloud environments without embedding deployment-specific values into the core business logic.

Detailed deployment architecture is documented in:

docs/architecture/05_cloud_deployment.md

Engineering Principles

The project follows several architectural and engineering principles:

Separation of Concerns

Single Responsibility Principle

Low Coupling

High Cohesion

Deterministic Business Logic

Configuration over Hardcoding

Environment-based Runtime Configuration

Modular Architecture

API-based Integration

Business-driven Development

Incremental Evolution

Synthetic Data for Confidentiality Protection

The underlying engineering philosophy remains:

Technology exists to solve business problems.

New technologies are introduced when they support a clear business or architectural requirement rather than for technology adoption alone.

Current Development Stage

The AI Supply Chain Copilot is a functional portfolio application whose v1.1.0 baseline is publicly cloud-deployed and whose current development increment demonstrates a second analytical domain.

The current implementation includes the complete path from synthetic operational data through deterministic analytics and decision support to Business Intelligence, REST API integration, Generative AI and a conversational frontend.

The current multidomain increment demonstrates Inventory and Transportation behind the same Copilot architecture, with explicit domain selection and domain-specific deterministic capabilities.

The current milestone validates:

end-to-end application architecture;

deterministic analytical processing;

configurable business rules;

REST API integration;

Business Intelligence;

controlled Generative AI integration;

real LLM behavior through structured evaluation;

frontend/backend separation;

environment-based configuration;

public cloud deployment;

distributed end-to-end integration;

multidomain orchestration across Inventory and Transportation;

deterministic domain selection;

structured Transportation intent routing;

deterministic Transportation capability dispatch;

preservation of Inventory backward compatibility.

The application remains portfolio-grade rather than production-ready.

Future evolution may introduce production hardening capabilities such as managed relational persistence, authentication and authorization, observability, centralized secrets management, containerization, CI/CD automation, scalability and additional AI governance controls.

Documentation Map

The architecture documentation is organized by responsibility:

Document

Purpose

01_system_overview.md

High-level system and business architecture

02_current_architecture.md

Current technical implementation architecture

03_data_model.md

Data model and persistence structure

04_decision_log.md

Significant architectural decisions

05_cloud_deployment.md

Cloud deployment architecture and runtime topology

06_transportation_architecture.md

Bounded Transportation domain architecture and Phase 0 implementation record

Together, these documents provide progressively deeper views of the same application.

Status

Project: AI Supply Chain Copilot
Baseline Version: v1.1.0
Status: Active Development
Current Stage: Functional Multidomain Portfolio Application
Domains: Inventory + Transportation
Last Updated: 2026-09-22