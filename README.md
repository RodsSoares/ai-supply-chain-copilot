# AI Supply Chain Copilot

> 🚀 **Current Release:** **v1.1.0 — Cloud-Deployed AI Copilot**
> 🌐 **Live Demo:** [Open AI Supply Chain Copilot](https://ai-supply-chain-copilot.streamlit.app)


![Version](https://img.shields.io/badge/version-v1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.14-blue)
![Status](https://img.shields.io/badge/status-active-success)
![Portfolio](https://img.shields.io/badge/portfolio-AI%20Engineering-orange)

<p align="center">
  <img
    src="docs/images/architecture-overview.png?v=1.1.0"
    alt="High-level architecture of the AI Supply Chain Copilot"
    width="1000"
  >
</p>

> **End-to-end Supply Chain Decision Support platform combining deterministic analytics, business rules, REST APIs, Business Intelligence and Generative AI.**

The application integrates a deterministic Supply Chain analytics engine with a real Large Language Model (LLM), enabling natural-language interpretation of structured inventory insights while preserving business rules and calculations outside the probabilistic AI layer.

An enterprise-inspired software engineering portfolio that combines **Supply Chain expertise, Data Engineering and Artificial Intelligence** to solve realistic inventory management problems using fully synthetic ERP data.

Rather than presenting isolated coding exercises, this repository evolves incrementally into a maintainable business application, demonstrating practical skills in software engineering, analytics, automation and AI.

---

# Table of Contents

- Overview
- Current Status
- Main Objectives
- Technology Stack
- Solution Architecture
- AI Copilot
- Project Structure
- Project Presentation
- Getting Started - Local Development
- Automated Tests
- Automated Project Audit
- Engineering Practices
- Business Rules Configuration
- Development Workflow
- Roadmap
- Version History
- Current Development Stage
- Why this project?
- Repository Purpose
- License

---

# Overview

The objective of this project is to demonstrate how modern Supply Chain challenges can be addressed through software engineering and artificial intelligence.

The application simulates an enterprise inventory management environment, combining:

- Python
- ETL Pipelines
- SQLite
- Data Analytics
- Business Rules Engine
- Business Intelligence
- REST API
- Generative AI / LLM Integration
- Streamlit Conversational Frontend
- Public Cloud Deployment

All datasets are fully synthetic and inspired by real business processes, preserving corporate confidentiality while maintaining realistic operational scenarios.

---

# Current Status

| Module | Status |
|----------|--------|
| Project Architecture | ✅ |
| Synthetic ERP Dataset | ✅ |
| ETL Pipeline | ✅ |
| SQLite Database | ✅ |
| Inventory Analytics | ✅ |
| Business Rules Engine | ✅ |
| Configurable Business Rules | ✅ |
| Automated Project Audit | ✅ |
| SQL Analytics | ✅ |
| KPI Engine | ✅ |
| REST API | ✅ |
| Power BI Dashboard | ✅ |
| AI Layer Foundation | ✅ |
| Automated Test Suite | ✅ |
| Real LLM Integration | ✅ |
| Real LLM Golden Set Validation | ✅ |
| Multi-Model Benchmark | ✅ |
| LLM Cost / Activation Safeguards | ✅ |
| Streamlit Conversational Frontend | ✅ |
| Public Cloud Deployment | ✅ |
| End-to-End Cloud Integration | ✅ |

---

# Main Objectives

This repository demonstrates practical implementation of:

- Data Engineering
- Software Engineering
- AI-enabled Solution Architecture
- Supply Chain Analytics
- Business Process Automation
- Decision Support Systems

The focus is not simply learning Python syntax, but designing maintainable business software following professional engineering practices.

---

# Technology Stack

| Category | Technologies |
|----------|--------------|
| Language | Python 3.14 |
| Data Processing | Pandas |
| Database | SQLite |
| API Framework | FastAPI |
| Business Intelligence | Power BI |
| Business Rules Configuration | JSON |
| Version Control | Git / GitHub |
| IDE | Visual Studio Code |
| Documentation | Markdown |
| Automated Testing | Pytest |
| AI Integration | OpenAI API / Large Language Model |
| AI Architecture | Modular AI Layer with Real and Fake LLM Clients |
| Frontend | Streamlit |
| Backend Hosting | Render |
| Frontend Hosting | Streamlit Community Cloud |
| Cloud Configuration | Environment Variables / Secrets |

### Planned Technologies

- PostgreSQL
- Docker
- Azure AI Services

---

# Solution Architecture

```mermaid
flowchart TD

    ERP[Synthetic ERP Inventory Dataset]
    ANALYTICS[Deterministic Analytics]
    RULES[Business Rules]
    DECISION[Decision Support]
    OUTPUT[output/inventory_analysis.csv]

    API[FastAPI REST API]
    BI[Power BI]

    AI[AI Service]
    CONTEXT[Deterministic Context]
    LLM[LLM Client]
    OPENAI[OpenAI API]

    FRONTEND[Streamlit Frontend]
    USER[User]

    MASTER[Synthetic Master / Structured Data]
    ETL[ETL / Standardization]
    DB[(SQLite)]
    RELATIONAL[Relational Consumers]

    ERP --> ANALYTICS
    ANALYTICS --> RULES
    RULES --> DECISION
    DECISION --> OUTPUT

    OUTPUT --> API
    OUTPUT --> BI

    API --> AI
    AI --> CONTEXT
    CONTEXT --> LLM
    LLM --> OPENAI
    OPENAI --> LLM
    LLM --> AI
    AI --> API

    USER --> FRONTEND
    FRONTEND --> API
    API --> FRONTEND

    MASTER --> ETL
    ETL --> DB
    DB --> RELATIONAL
```

The solution adopts a layered and modular architecture in which each layer has a clearly defined responsibility and can evolve independently over time.

The **Analytical Inventory Path** processes the synthetic ERP inventory dataset through deterministic analytics, business rules and decision-support logic. Its consolidated output is materialized in `output/inventory_analysis.csv`, which serves as the current analytical artifact consumed by the REST API, Power BI and AI capabilities.

The **ETL Pipeline** supports ingestion, validation, transformation and standardization of structured data used by the relational data path.

The **SQLite Database** provides relational persistence for structured master and inventory-related entities. It supports relational application capabilities but is not the source of the current analytical inventory artifact consumed by the `/inventory` endpoint.

The **Analytics Engine** operates on the synthetic ERP inventory dataset and computes operational KPIs, inventory metrics, stockout risk indicators and prioritization scores based on configurable business parameters.

Business rules are externalized through the `config/business_rules.json` file, allowing operational thresholds, scoring parameters and decision criteria to evolve without modifying the application's source code.

The **Decision Support Engine** consolidates analytical outputs into actionable business recommendations, including replenishment priorities, excess inventory identification, stockout risk assessment and managerial prioritization.

The **REST API**, implemented with FastAPI, exposes the application's analytical and decision-support capabilities through HTTP endpoints. It serves as the integration layer for external consumers, including the Power BI dashboard and the AI Supply Chain Copilot.

The **Streamlit Conversational Frontend** provides the user-facing interface for interacting with the AI Copilot. It consumes the FastAPI backend through the REST API contract, keeping presentation responsibilities separated from business logic, analytics and AI orchestration.

The **AI Integration Layer** connects the deterministic application with Generative AI through a modular architecture composed of controlled data-access tools, deterministic context preparation, service orchestration, system prompting and an isolated LLM client.

The **AI Data-Access Tools** retrieve validated analytical inventory information from the application.

The **Context Preparation Layer**, implemented in `src/ai/context.py`, prepares and deterministically enriches the bounded business context sent to the LLM. This layer is responsible for context selection, consolidated indicators and exact aggregations that should not be delegated to probabilistic model reasoning.

Exact operations such as counts, aggregations, extrema and tie handling are kept in the deterministic layer whenever correctness can be guaranteed before the LLM call. The model receives these computed results as structured context and remains responsible for interpretation and communication rather than probabilistic recalculation.

The **AI Copilot Service**, implemented in `src/ai/service.py`, acts as an orchestration layer. It coordinates data retrieval, context preparation and LLM response generation without absorbing analytical or provider-specific responsibilities.

The **LLM Client** abstracts the model provider from the rest of the application and supports both Fake and Real execution modes.

This architecture promotes:

- Layered Architecture
- High Cohesion
- Low Coupling
- Single Responsibility Principle (SRP)
- Separation of Concerns
- Deterministic / Probabilistic Layer Separation
- Maintainability
- Testability
- Extensibility
- Modular AI Integration
- Controlled LLM Context
- Explicit LLM Activation Safeguards
- Cost-efficient AI Testing
---

## Cloud Deployment Architecture

The application is deployed as a distributed cloud solution while preserving the same layered architecture used during local development.

```mermaid
flowchart LR

U[User / Browser]

SC[Streamlit Community Cloud]
FE[Streamlit Conversational Frontend]

R[Render Web Service]
API[FastAPI REST API]

ANALYTICAL[Analytical Inventory Artifact]
DB[(SQLite Relational Persistence)]
AI[AI Service]
CTX[Deterministic Context Preparation]
LLM[LLM Client]

OAI[OpenAI API / Real LLM]

GH[GitHub Repository]

U -->|HTTPS| SC
SC --> FE

FE -->|HTTPS / JSON| R
R --> API

ANALYTICAL --> API
API --> AI

AI --> CTX
CTX --> LLM
LLM --> OAI
OAI -->|Generated Response| LLM
LLM --> AI

AI --> API
API -->|JSON Response| FE
FE --> U

GH -. Source / Deploy .-> SC
GH -. Source / Deploy .-> R
```

### Environment-based configuration

The same source code supports both local and cloud execution through environment-specific configuration.

| Configuration | Local | Cloud |
|---|---|---|
| Frontend API Base URL | `http://127.0.0.1:8000` | Render public backend URL |
| LLM Mode | configurable | `real` |
| Real LLM Enabled | configurable | `true` |
| OpenAI API Key | local environment variable | backend secret |

Application code, runtime configuration and secrets are deliberately separated.

The `OPENAI_API_KEY` is never stored in source code or exposed to the Streamlit frontend.

Detailed cloud deployment architecture, service responsibilities, runtime configuration and deployment decisions are documented in:

[`docs/architecture/05_cloud_deployment.md`](docs/architecture/05_cloud_deployment.md)
---

# AI Copilot

The **AI Supply Chain Copilot** provides a natural-language interface over the application's deterministic inventory analytics and decision-support capabilities.

Rather than delegating business calculations to the Large Language Model, the Copilot follows a controlled architecture in which operational metrics, risk indicators, prioritization scores and recommended actions are calculated by deterministic application modules before any information is sent to the LLM.

The Copilot workflow follows five main steps:

1. The deterministic application layers calculate inventory metrics, risks, scores and recommended actions.
2. The AI service retrieves validated inventory information through controlled data-access tools.
3. A structured and bounded business context is prepared for the LLM.
4. The LLM interprets the supplied context and generates a natural-language response.
5. The response is returned through the REST API to support human analysis and decision-making.

This design keeps **business calculations deterministic and auditable**, while using Generative AI for contextual interpretation, synthesis and communication.

## Fake and Real LLM Modes

The LLM client supports two execution modes:

- **Fake LLM** — enables cost-free development, automated testing and validation of the complete application flow without consuming an external AI provider.
- **Real LLM** — connects the Copilot to the OpenAI API and generates responses using a real Large Language Model.

Real LLM calls require explicit environment-based activation in addition to a valid API key. This deliberate safeguard reduces the risk of accidental external API consumption during development and testing.

The architecture also controls the amount of context sent to the model and limits the maximum response size, providing additional control over token consumption and API costs.

## Copilot API Endpoint

The AI Supply Chain Copilot is exposed through the REST API using the following endpoint:

```text
POST /copilot
```

The endpoint receives a natural-language business question, orchestrates the AI service, retrieves the analytical context produced by the deterministic application layers and returns the LLM-generated response.

### Request

Example request body:

```json
{
  "pergunta": "Quais produtos apresentam prioridade alta?"
}
```

### Response

The endpoint returns the original question together with the natural-language response generated by the configured LLM client.

Example response structure:

```json
{
  "pergunta": "Quais produtos apresentam prioridade alta?",
  "resposta": "Natural-language analysis generated from the supplied inventory context."
}
```

The response content depends on the analytical context supplied to the model and on the selected LLM execution mode.

### Execution Flow

```text
POST /copilot
      ↓
FastAPI Endpoint
      ↓
AI Service
      ↓
Controlled Data-Access Tools
      ↓
Structured Context Preparation
      ↓
LLM Client
      ↓
Fake LLM or Real LLM
      ↓
Natural-Language Response
```

The endpoint preserves the architectural separation between deterministic business logic and probabilistic AI interpretation. Inventory calculations, risk indicators, prioritization scores and recommended actions are generated before the LLM is called. The model receives these analytical results as context and is responsible for interpreting and communicating them in natural language.

## Real LLM Validation

The Real LLM integration was validated end-to-end through the `/copilot` endpoint using the OpenAI API and a structured Golden Set evaluation.

The evaluation covered factual accuracy, consolidated KPI interpretation, ranking, comparison, partial-context awareness, hallucination resistance, business-rule governance and deterministic aggregation.

During the baseline evaluation, a probabilistic inconsistency was identified in a supplier-frequency question: one model execution failed to preserve a tie.

Rather than addressing the issue only through prompting, the architecture was improved by moving exact aggregation, extrema and tie handling into the deterministic context-preparation layer.

After the architectural correction, the complete automated suite passed **42/42 tests**, and the corrected deterministic behavior was successfully reproduced across multiple real LLM executions and models.

A comparative benchmark between **GPT-5.6 Terra** and **GPT-5.6 Sol** was also performed. Both models demonstrated strong factual grounding and governance.

GPT-5.6 Terra remains the default model due to its balance of accuracy, conciseness and operational efficiency, while GPT-5.6 Sol produced richer but generally more verbose explanations.

A core lesson from the validation process is that deterministic calculations should remain in the application engine whenever exact results can be computed before the LLM call. The LLM is then responsible for interpretation, synthesis and communication.

The complete benchmark evidence is available at:

`docs/evaluations/LLM_Real_Model_Benchmark_Final.xlsx`

<p align="center">
  <img
    src="docs/images/first llm real answer.png"
    alt="First successful real LLM response from the AI Supply Chain Copilot"
    width="900"
  >
</p>

<p align="center">
  <em>First successful end-to-end response generated through the real LLM integration.</em>
</p>

### Cloud End-to-End Flow

The production-demo flow is currently:

`User → Streamlit Cloud → FastAPI on Render → deterministic analytics/context → LLM Client → OpenAI API → FastAPI → Streamlit → User`

The cloud deployment was validated end-to-end using the same analytical questions previously covered by the Golden Set and multi-model evaluation process.

The cloud milestone validates deployment and distributed integration rather than re-validating LLM analytical behavior, which had already been evaluated before deployment.

---
# Project Structure

```text
AI-SUPPLY-CHAIN-COPILOT/

├── config/
│   └── business_rules.json
│
├── data/
├── database/
│
├── docs/
│   ├── architecture/
│   │   ├── 01_system_overview.md
│   │   ├── 02_current_architecture.md
│   │   ├── 03_data_model.md
│   │   ├── 04_decision_log.md
│   │   └── 05_cloud_deployment.md
│   │
│   ├── evaluations/
│   │   └── LLM_Real_Model_Benchmark_Final.xlsx
│   ├── images/
│   ├── presentations/
│   ├── project_audit/
│   └── roadmap/
│
├── frontend/
│   └── app.py
│
├── output/
├── reports/
├── sample_data/
├── scripts/
│
├── src/
│   ├── ai/
│   │   ├── client.py
│   │   ├── context.py
│   │   ├── prompts.py
│   │   ├── service.py
│   │   └── tools.py
│   └── api/
│
├── tests/
│   ├── golden_test_set.md
│   ├── test_ai_client.py
│   ├── test_ai_context.py
│   ├── test_ai_service.py
│   ├── test_ai_tools.py
│   └── test_api_copilot.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Project Presentation

A comprehensive presentation describing the project's business case, software architecture, implementation strategy and development roadmap is available below.

### Downloads

- 📄 [Project Presentation (PDF)](docs/presentations/AI-Supply-Chain-Copilot.pdf)
- 📊 [Project Presentation (PowerPoint)](docs/presentations/AI-Supply-Chain-Copilot.pptx)

The presentation provides an executive overview of:

- Business Case
- Software Architecture
- ETL Pipeline
- Business Rules
- REST API
- Power BI Dashboard
- Engineering Decisions
- Development Roadmap
- AI Integration Roadmap

---

# Getting Started — Local Development

The steps below describe how to run the complete application locally.

For direct access to the deployed version, use the **Live Demo** available at the top of this README.

## 1. Clone the repository

```bash
git clone https://github.com/RodsSoares/ai-supply-chain-copilot.git
cd ai-supply-chain-copilot
```

## 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 4. Run the analytical pipeline

```powershell
python scripts/analyze_inventory.py
```

This executes the deterministic Supply Chain pipeline and generates the analytical outputs consumed by the application.

## 5. Choose the LLM execution mode

The Copilot supports both **Fake LLM** and **Real LLM** execution modes.

### Fake LLM Mode

Recommended for local development, testing and demonstrations that do not require external API consumption.

```powershell
$env:LLM_MODE="fake"
```

### Real LLM Mode

To enable the real LLM integration, configure the required environment variables:

```powershell
$env:OPENAI_API_KEY="your-api-key"
$env:LLM_MODE="real"
$env:LLM_REAL_ENABLED="true"
```

> **Security:** Never commit API keys, credentials or other secrets to the repository. Environment variables should be configured only in the local execution environment or through an appropriate secrets-management solution.

> **Cost control:** Real LLM calls consume external API resources and may generate costs. The `LLM_REAL_ENABLED` variable acts as an explicit safeguard so that selecting real mode alone does not automatically authorize external model calls.

## 6. Start the REST API

```powershell
python -m uvicorn src.api.main:app
```

After startup, the interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## 7. Test the Copilot

Through the Swagger interface, execute:

```text
POST /copilot
```

Example request:

```json
{
  "pergunta": "Quais produtos apresentam prioridade alta?"
}
```

In **Fake LLM Mode**, the application validates the complete internal AI flow without calling an external provider.

In **Real LLM Mode**, the request is processed through the complete application pipeline and sent to the configured external LLM provider.

## 8. Run the automated test suite

```powershell
python -m pytest
```

The automated tests validate the deterministic modules, API behavior, AI orchestration, context controls and LLM client safeguards.

## 9. Start the Streamlit Frontend

### Frontend API Configuration

The Streamlit frontend communicates with the FastAPI backend through the `API_BASE_URL` environment variable.

For local execution:

```powershell
$env:API_BASE_URL="http://127.0.0.1:8000"
```

In cloud environments, `API_BASE_URL` should point to the deployed FastAPI backend.

If the variable is not defined, the application defaults to the local API address.

With the REST API running, start the conversational frontend in a second terminal:

```powershell
python -m streamlit run frontend/app.py
```

---
# Automated Tests

The project includes an automated test suite built with **Pytest**, covering the REST API and AI integration components.

The current **v1.1.0** release is validated by **42 automated tests**, covering:

- AI client behavior and execution modes
- Fake and Real LLM safeguards
- AI service orchestration
- Controlled data-access tools
- Context preparation and validation
- REST API `/copilot` endpoint behavior
- Integration between the API and AI layers
- Error handling and external-call protection

The complete test suite can be executed from the project root with:

```powershell
python -m pytest
```

Current validated result:

```text
collected 42 items
42 passed
```

The automated test architecture allows the AI integration flow to be validated through simulated dependencies and the Fake LLM client, avoiding unnecessary external API consumption during routine testing.

Real LLM connectivity is validated separately through controlled end-to-end execution, while the automated test suite remains deterministic, repeatable and cost-efficient.
---

# Automated Project Audit

To ensure architectural consistency throughout development, the repository includes an automated engineering auditing tool.

Run:

```bash
python scripts/project_audit.py
```

The auditor automatically generates:

- Project Health Score
- Architecture Overview
- Pipeline Overview
- Python Module Inventory
- Function Catalog
- Dependency Analysis
- Repository Consistency Checks
- Syntax Validation
- Documentation Coverage
- TODO / FIXME Detection

Generated report:

```text
docs/project_audit/PROJECT_AUDIT.md
```

Rather than relying exclusively on manually maintained documentation, the project automatically generates engineering reports based on the current repository state, helping keep technical documentation aligned with the implementation.

---

# Engineering Practices

This project follows modern software engineering principles designed to maximize maintainability, extensibility and long-term evolution.

- Layered Architecture
- Modular Architecture
- High Cohesion
- Low Coupling
- Single Responsibility Principle (SRP)
- Separation of Concerns
- Configuration over Hardcoding
- Environment-based Runtime Configuration
- Business-driven Development
- Synthetic Enterprise Dataset
- Continuous Refactoring
- Automated Project Audit
- Incremental Delivery
- Version Control
- Automated Testing with Pytest
- Deterministic / Probabilistic Layer Separation
- Modular AI Integration
- Explicit LLM Activation Safeguards
- Controlled LLM Context
- Fake Client for Cost-free Testing

---

# Business Rules Configuration

Business parameters are centralized in:

```text
config/business_rules.json
```

This configuration layer separates configurable business parameters from application code, allowing operational thresholds, scoring values and business policies to evolve without modifying Python source files.

By externalizing these parameters into a JSON configuration file, the project reduces hardcoded values, improves maintainability and enables business rule adjustments without requiring changes to the application's implementation.

Current configurable parameters include:

- Inventory limits
- Financial scoring thresholds
- ABC classification weights
- Stockout risk scoring
- Lead time scoring
- Priority thresholds

This architecture supports future administrative interfaces and additional API-based configuration capabilities while keeping the core business logic modular and maintainable.

---

# Development Workflow

```text
Develop Feature
      │
      ▼
Execute Pipeline
      │
      ▼
Run Automated Tests
      │
      ▼
Execute Project Audit
      │
      ▼
Review PROJECT_AUDIT.md
      │
      ▼
Commit
      │
      ▼
Push to GitHub
      │
      ▼
Cloud Deployment
      │
      ▼
End-to-End Validation
```

---

# Roadmap

| Phase | Planned Release | Status |
|---------|----------------|--------|
| Foundation (Architecture, Dataset, ETL, Database) | v0.1.0 | ✅ |
| Business Intelligence (Inventory Analytics, Rules Engine, Audit) | v0.2.0 | ✅ |
| Analytics (SQL Analytics, KPI Engine) | v0.3.0 | ✅ |
| Applications (REST API and Dashboard) | v0.4.0 | ✅ |
| AI Integration Layer | v0.5.0 | ✅ |
| Functional AI Copilot | v1.0.0 | ✅ |
| Cloud Deployment & Conversational Frontend | v1.1.0 | ✅ |
| Production Hardening | Future | ⏳ |

---

# Version History

| Version | Highlights |
|-----------|------------|
| **v0.1.0** | Project architecture, synthetic ERP dataset and repository foundation |
| **v0.2.0** | ETL Pipeline, SQLite integration, Inventory Analytics MVP, Business Rules Configuration, Configurable Business Rules and Automated Project Audit |
| **v0.3.0** | SQL Analytics, KPI Engine and advanced business metrics |
| **v0.4.0** | REST API, Dashboard and application layer |
| **v0.5.0** | AI Layer Foundation |
| **v1.0.0** | Functional AI Copilot with validated real LLM integration, controlled context, explicit activation safeguards and end-to-end API flow |
| **v1.1.0** | Streamlit conversational frontend, public cloud deployment, Render-hosted FastAPI backend, Streamlit Community Cloud frontend, environment-based service configuration and validated end-to-end cloud integration |

---

# Current Development Stage

The **AI Supply Chain Copilot v1.1.0** is a functional, publicly accessible cloud-deployed portfolio application.

The current release integrates deterministic Supply Chain analytics, configurable business rules and decision support with a complementary relational data path, REST API, Power BI dashboard, conversational Streamlit frontend and a modular Generative AI layer.

The AI integration has completed structured Golden Set validation and a comparative multi-model benchmark. Exact calculations, aggregations, extrema and tie handling remain under deterministic application control, while the LLM is responsible for interpretation, synthesis and natural-language communication.

The application is deployed through a distributed cloud architecture. The Streamlit frontend is hosted on Streamlit Community Cloud and communicates over HTTPS with the FastAPI backend hosted on Render. Runtime configuration is externalized through environment variables, while sensitive credentials remain isolated from source code and the frontend.

The complete public flow has been validated end-to-end:

`User → Streamlit Cloud → FastAPI / Render → deterministic analytics/context → LLM Client → OpenAI API → FastAPI → Streamlit → User`

Version **v1.1.0 remains a portfolio-grade deployment rather than a production-ready enterprise system**. Future production hardening may include a production-grade persistent database, authentication and authorization, observability, containerization, centralized secrets management, scalability improvements and additional AI governance controls.

The current architectural foundation allows these capabilities to evolve without requiring fundamental redesign of the core application.

---

# Why this project?

This repository reflects my transition from Supply Chain leadership toward AI Solutions, Intelligent Automation and AI Transformation.

It combines nearly two decades of enterprise experience in Supply Chain, Planning and Operations with data, automation, software architecture and Generative AI.

The objective is not only to build software, but to demonstrate the ability to design maintainable business solutions that integrate engineering, analytics and artificial intelligence.

---

# Repository Purpose

This repository serves as a functional AI Solutions portfolio project demonstrating the end-to-end design, implementation and cloud deployment of a business application integrating data engineering, analytics, business rules, APIs, Business Intelligence and Generative AI.

Each sprint delivers an enterprise-inspired capability while preserving architecture quality, maintainability and long-term scalability.

---

# License

This repository is intended exclusively for educational and portfolio purposes.

All datasets, business rules and operational scenarios are fictional or synthetically generated and do not contain confidential corporate information.