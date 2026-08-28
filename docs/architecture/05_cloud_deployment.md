# Cloud Deployment Architecture

## Purpose

This document describes the cloud deployment architecture of the **AI Supply Chain Copilot v1.1.0**.

The objective is to document how the application's existing logical architecture is distributed across cloud services while preserving the separation of responsibilities established during local development.

The cloud deployment enables the application to remain publicly accessible independently of the local development machine.

---

## Scope

This document covers:

- frontend deployment through Streamlit Community Cloud;
- backend deployment through Render;
- communication between frontend and backend through the REST API;
- integration with the external LLM provider;
- environment-based runtime configuration;
- management and isolation of application secrets;
- source-code integration with GitHub;
- local versus cloud execution;
- current persistence strategy and deployment limitations;
- end-to-end cloud request flow.

This document focuses on the architectural and application-level aspects relevant to the project. Detailed infrastructure administration, networking, operating-system management and low-level cloud infrastructure are outside the current project scope.

---

## Deployment Overview

The cloud deployment distributes the application across independent services while preserving the same logical responsibilities defined by the application architecture.

```mermaid
flowchart LR

    GH[GitHub Repository]
    USER[User / Browser]
    SC[Streamlit Community Cloud]
    FE[Streamlit Frontend]
    RENDER[Render Web Service]
    API[FastAPI Backend]
    ANALYTICAL[Analytical Inventory Artifact]
    DB[(SQLite Relational Persistence)]
    AI[AI Service]
    CTX[Deterministic Context]
    LLM[LLM Client]
    OAI[OpenAI API / Real LLM]

    GH -. Source / Deploy .-> SC
    GH -. Source / Deploy .-> RENDER

    USER -->|HTTPS| SC
    SC --> FE
    FE -->|HTTPS / JSON| RENDER
    RENDER --> API

    ANALYTICAL --> API

    API --> AI
    AI --> CTX
    CTX --> LLM
    LLM -->|External API Call| OAI
    OAI -->|Generated Response| LLM
    LLM --> AI
    AI --> API

    API -->|JSON Response| FE
    FE --> USER
    ```

The deployment consists of four main external environments:

| Environment | Primary Responsibility |
|---|---|
| Local Development Machine | Development, testing, project audit and local execution |
| GitHub | Source-code repository and deployment source |
| Streamlit Community Cloud | Hosting and execution of the conversational frontend |
| Render | Hosting and execution of the FastAPI backend |
| OpenAI API | External LLM inference service |

GitHub stores the application source code but does not execute the application itself. Streamlit Community Cloud and Render retrieve the required source code and execute their respective application components in cloud environments.

The frontend and backend are deployed independently. The Streamlit frontend acts as an API client and communicates with the FastAPI backend over HTTPS using the REST API contract.

The FastAPI backend remains responsible for application processing and orchestration. It accesses the deterministic application layers, prepares the controlled business context and, when Real LLM Mode is enabled, communicates with the external OpenAI API.

This distribution allows the public application to operate independently of the local development machine while preserving the same separation of concerns used during local execution.

---

## Service Responsibilities

The cloud architecture assigns a specific responsibility to each external service. This separation preserves low coupling and allows individual components to evolve without requiring fundamental changes to the complete application.

### GitHub

GitHub acts as the source-code repository and deployment source for the cloud services.

Its responsibilities include:

- storing and versioning the application source code;
- preserving the development history through Git;
- providing the source used by Streamlit Community Cloud and Render during deployment;
- supporting controlled evolution of the application through commits and releases.

GitHub stores the application code but is not responsible for executing the public application.

### Streamlit Community Cloud

Streamlit Community Cloud hosts and executes the conversational frontend implemented in `frontend/app.py`.

Its responsibilities include:

- rendering the user-facing conversational interface;
- receiving natural-language questions from the user;
- sending requests to the FastAPI backend;
- receiving JSON responses from the backend;
- presenting the generated response to the user.

The frontend does not contain the core Supply Chain business logic, deterministic analytics or LLM orchestration.

### Render

Render hosts and executes the FastAPI backend.

Its responsibilities include:

- exposing the public REST API;
- receiving HTTPS requests from the Streamlit frontend;
- executing the application backend;
- accessing deterministic analytical and decision-support components;
- orchestrating the AI service;
- communicating with the external LLM provider when Real LLM Mode is enabled;
- returning structured responses to the frontend.

The Render service therefore represents the primary cloud execution environment for the application's backend responsibilities.

### OpenAI API

The OpenAI API provides the external Large Language Model inference capability used by the Real LLM client.

Its responsibility is to process the controlled context and instructions supplied by the application and generate a natural-language response.

Business calculations, inventory metrics, aggregations, extrema, tie handling and decision rules remain under deterministic application control and are not delegated to the external LLM.

### Local Development Environment

The local machine remains the primary development and engineering environment.

It is used for:

- source-code development;
- local application execution;
- automated testing;
- deterministic pipeline execution;
- project audit;
- debugging and validation before deployment.

The local environment is no longer required for the public application to remain available after deployment.    

---

## End-to-End Request Flow

A user interaction with the cloud-deployed Copilot follows the sequence below:

1. The user accesses the conversational interface hosted on Streamlit Community Cloud.

2. The user submits a natural-language Supply Chain question through the Streamlit frontend.

3. The frontend creates an HTTP request following the REST API contract and sends the question over HTTPS to the public FastAPI backend hosted on Render.

4. FastAPI receives the request through the `/copilot` endpoint and delegates processing to the AI service.

5. The application retrieves validated analytical information from the deterministic layers.

6. The context-preparation layer builds a structured and bounded business context, including deterministic calculations and aggregations required to answer the question.

7. When Real LLM Mode is enabled, the LLM client sends the controlled context and instructions to the OpenAI API.

8. The external LLM generates a natural-language response based on the supplied context.

9. The generated response returns to the application backend, which exposes the result through the REST API as a structured JSON response.

10. The Streamlit frontend receives the response and presents it to the user.

The complete flow can therefore be represented as:

`User → Streamlit Cloud → FastAPI / Render → deterministic analytics/context → AI Service → LLM Client → OpenAI API → FastAPI → Streamlit → User`

The REST API contract decouples the frontend from the backend implementation. As long as the agreed request and response structures remain compatible, the user interface can evolve or be replaced without requiring fundamental changes to the deterministic business and AI orchestration layers.

---

## Runtime Configuration and Environment Variables

The application separates source code from environment-specific runtime configuration.

This allows the same codebase to operate in local and cloud environments without requiring source-code modifications for each deployment target.

### Current Runtime Configuration

| Variable | Purpose | Local Example | Cloud |
|---|---|---|---|
| `API_BASE_URL` | Defines the FastAPI backend address consumed by the frontend | `http://127.0.0.1:8000` | Render public backend URL |
| `LLM_MODE` | Selects the Fake or Real LLM client | `fake` or `real` | `real` |
| `LLM_REAL_ENABLED` | Explicitly authorizes external LLM calls | `true` or `false` | `true` |
| `OPENAI_API_KEY` | Authenticates requests to the external LLM provider | Local environment secret | Backend secret |

### Frontend Backend Address

The Streamlit frontend obtains the backend address through `API_BASE_URL`.

During local execution:

`API_BASE_URL = http://127.0.0.1:8000`

During cloud execution, the same variable points to the public FastAPI service hosted on Render.

This prevents the backend location from being hardcoded into the frontend and allows the deployment target to change through configuration rather than source-code modification.

### LLM Runtime Control

`LLM_MODE` determines which LLM client implementation should be used.

The application supports:

- `fake` for development, automated testing and cost-free execution;
- `real` for communication with the external LLM provider.

`LLM_REAL_ENABLED` provides an additional explicit safeguard for external model calls. Selecting Real LLM Mode alone is therefore not sufficient to authorize external API consumption.

This separation reduces the risk of accidental API usage and associated costs.

### Configuration versus Source Code

Runtime configuration changes how the application behaves in a specific environment without changing its implementation.

Examples include:

- backend service address;
- LLM execution mode;
- authorization of real external LLM calls.

Application modules such as the FastAPI endpoints, AI service, LLM client and deterministic analytical functions remain part of the source code.

This separation supports portability between local and cloud environments and reduces environment-specific hardcoding.

---

## Secrets and Security

Sensitive credentials are treated separately from application source code and ordinary runtime configuration.

### OpenAI API Key

`OPENAI_API_KEY` is a secret credential used by the backend to authenticate requests to the external LLM provider.

The key must never be:

- hardcoded into Python source files;
- committed to Git or GitHub;
- exposed through the public repository;
- included in screenshots or documentation;
- sent to or stored in the Streamlit frontend.

In the cloud deployment, the credential is configured only in the backend environment that requires access to the OpenAI API.

The application reads the credential at runtime without requiring the secret value to be stored in the source code.

### Backend Secret Isolation

The Streamlit frontend does not require direct access to the OpenAI API credential.

The communication path is:

`Streamlit Frontend → FastAPI Backend → OpenAI API`

The frontend communicates only with the application's REST API. The backend is responsible for accessing the external LLM provider using the protected credential.

This prevents sensitive provider credentials from being unnecessarily distributed across application components.

### Configuration and Secret Separation

Although both configuration values and secrets may be supplied through environment-specific mechanisms, they represent different concerns.

Examples of ordinary runtime configuration include:

- `API_BASE_URL`;
- `LLM_MODE`;
- `LLM_REAL_ENABLED`.

An example of a secret is:

- `OPENAI_API_KEY`.

Configuration controls application behavior or service location. Secrets provide sensitive authentication information and therefore require stricter handling.

### Current Security Scope

The current v1.1.0 deployment implements credential isolation appropriate for the portfolio application, but it should not be interpreted as a complete enterprise security architecture.

Production hardening may include additional capabilities such as:

- centralized secrets management;
- authentication and authorization;
- access control;
- credential rotation;
- security monitoring and auditing;
- additional network and API protection mechanisms.

---

## Data and Persistence in Cloud

The current v1.1.0 deployment preserves SQLite as the application's relational persistence technology.

### Current Data Architecture

The current implementation contains two complementary data paths with different persistence and consumption responsibilities.

The **analytical inventory path** follows:

`Synthetic ERP Inventory → Deterministic Analytics → Business Rules / Decision Support → output/inventory_analysis.csv → REST API / Power BI / AI Context`

The analytical inventory dataset is processed directly by the deterministic analytics pipeline. Its consolidated output is materialized in `output/inventory_analysis.csv`, which serves as the current analytical artifact consumed by the application's analytical, API, Business Intelligence and AI capabilities.

The **relational data path** follows:

`Structured Data → ETL / Standardization → SQLite → Relational Consumers`

SQLite provides relational persistence for structured master and inventory-related entities. It is not the source of the current analytical inventory artifact consumed by the `/inventory` endpoint.

Deploying the application to the cloud preserves these logical data responsibilities rather than combining them into a single sequential pipeline.

### Application Data versus Cloud Service Storage

Application persistence and cloud service persistence are related but different concerns.

SQLite provides persistence at the application level by storing structured data in a database file.

However, the durability of that database file also depends on the storage characteristics of the environment in which the backend is running.

A database can therefore provide persistent storage from the application's perspective while still being hosted on infrastructure whose local filesystem may not provide the durability expected from a production database service.

### Current Deployment Limitation

The current cloud deployment should be treated as a portfolio-grade architecture rather than a production-grade data platform.

The application currently uses SQLite and synthetic data, which are appropriate for demonstrating the complete analytical and AI workflow but are not intended to represent the final persistence architecture of a scalable enterprise system.

For the current use case, the dataset is controlled and reproducible, and the application does not depend on continuous user-generated transactional writes.

### Future Persistence Evolution

A production-oriented evolution may replace SQLite with a managed relational database such as PostgreSQL.

This would provide a more appropriate foundation for capabilities such as:

- durable transactional persistence;
- concurrent access;
- centralized database management;
- backup and recovery;
- scalability;
- production monitoring;
- independent database lifecycle management.

Because the persistence layer is separated from the higher application layers, this evolution can be implemented without fundamentally redesigning the frontend, REST API or AI orchestration architecture.

---

## Local versus Cloud Execution

The AI Supply Chain Copilot is designed to support both local and cloud execution from the same source-code base.

The core application architecture does not change between environments. The main differences are the execution location and environment-specific runtime configuration.

| Component | Local Execution | Cloud Execution |
|---|---|---|
| Source Code | Local Git repository | Retrieved from GitHub |
| Streamlit Frontend | Local process | Streamlit Community Cloud |
| FastAPI Backend | Local Uvicorn process | Render Web Service |
| Backend Address | `http://127.0.0.1:8000` | Public Render URL |
| SQLite / Application Data | Local application environment | Backend cloud environment |
| LLM Provider | Fake or Real | Real |
| OpenAI Credential | Local environment secret | Backend cloud secret |
| Automated Tests | Local development environment | Validated before deployment |
| Project Audit | Local development environment | Validated before deployment |

### Local Execution

During development, the application components can run on the developer machine.

The Streamlit frontend communicates with the locally running FastAPI backend through:

`http://127.0.0.1:8000`

This environment supports development, debugging, automated testing, project auditing and controlled Real or Fake LLM execution.

### Cloud Execution

In the public deployment, the frontend and backend execute independently in cloud services.

The Streamlit frontend communicates with the public FastAPI backend hosted on Render through the configured `API_BASE_URL`.

The local development machine is not part of the runtime path of a public user request.

Therefore, the deployed application remains accessible even when the local development machine is turned off.

### Portability through Configuration

Environment-specific values are externalized from the source code wherever appropriate.

The deployment model therefore follows the principle:

`Same Code + Different Environment Configuration → Different Runtime Environment`

This avoids maintaining separate local and cloud versions of the application and reduces the risk of divergence between environments.

Changes to service addresses, execution modes or credentials can be handled through runtime configuration without modifying the application's core business logic.

---

## Deployment and Update Flow

The cloud deployment is integrated with the Git-based development workflow.

Application changes originate in the local development environment and are validated before becoming part of the public deployment.

The current workflow follows:

`Development → Local Validation → Commit → Push to GitHub → Cloud Deployment → End-to-End Validation`

### Development and Local Validation

Changes are initially implemented in the local development environment.

Before deployment, the project can be validated through:

- deterministic pipeline execution;
- automated tests with Pytest;
- automated project audit;
- local API and frontend execution when required.

This validation helps identify implementation or architectural issues before the updated source code becomes the deployment source.

### Version Control

After validation, the changes are committed to the local Git repository and pushed to GitHub.

GitHub acts as the version-controlled source used by the cloud services.

This creates a clear separation between:

- development and validation;
- source-code versioning;
- cloud execution.

### Cloud Deployment

Streamlit Community Cloud and Render use the GitHub repository as the source for their respective deployed components.

The deployment process creates or updates the running cloud services from the versioned source code while preserving environment-specific configuration outside the source code.

This means application code can evolve through Git without requiring cloud-specific values or sensitive credentials to be committed to the repository.

### Post-Deployment Validation

A successful deployment does not by itself guarantee that the complete distributed application is functioning correctly.

After deployment, the public application is validated end-to-end to confirm communication across the complete runtime path:

`User → Streamlit → FastAPI → deterministic analytics/context → AI Service → LLM Client → OpenAI API → FastAPI → Streamlit → User`

This validation complements, rather than replaces, the automated test suite.

Automated tests validate deterministic and integration behavior in a controlled and repeatable environment, while post-deployment validation confirms that the independently hosted cloud components are correctly connected and operational.

---

## Architectural Decisions and Trade-offs

The v1.1.0 cloud deployment was designed to extend the existing application architecture rather than redesign the application specifically for cloud hosting.

The following decisions define the current deployment strategy.

### Independent Frontend and Backend Deployment

The Streamlit frontend and FastAPI backend are deployed as independent services.

This preserves the separation between presentation and application responsibilities established in the logical architecture.

Benefits include:

- independent evolution of frontend and backend components;
- reduced coupling between presentation and business logic;
- preservation of the REST API as the integration boundary;
- ability to replace or evolve the frontend without fundamentally redesigning the backend.

The trade-off is additional distributed-system complexity, since communication between independently hosted services must be correctly configured and validated.

### REST API as the Integration Contract

The existing FastAPI REST interface was preserved as the communication contract between frontend and backend.

The frontend therefore depends on the API contract rather than on the internal implementation of the backend.

This allows internal analytical, decision-support and AI components to evolve while preserving compatibility with external consumers as long as the API contract remains stable.

### Environment-based Configuration

Environment-specific values are externalized instead of being hardcoded into the application.

This enables the same source code to support local and cloud execution while allowing service addresses, LLM execution modes and credentials to vary between environments.

The approach improves portability and reduces environment-specific source-code changes.

### Backend-controlled LLM Integration

The external LLM integration remains a backend responsibility.

The Streamlit frontend does not communicate directly with the OpenAI API and does not require access to the provider credential.

This preserves the existing AI orchestration architecture, centralizes external model access and reduces unnecessary exposure of sensitive credentials.

### SQLite Retained for v1.1.0

SQLite was intentionally retained for the current deployment rather than introducing a new database technology solely for the cloud milestone.

The objective of v1.1.0 is to validate cloud deployment, distributed integration and public accessibility while preserving previously validated deterministic application behavior.

For the current synthetic relational workload and portfolio scope, SQLite remains sufficient for the relational persistence responsibilities implemented in v1.1.0.

The trade-off is that the current persistence architecture is not intended to represent a scalable production-grade transactional database solution.

A managed relational database such as PostgreSQL remains a future production-hardening evolution.

### Managed Cloud Services

The deployment uses managed application-hosting services rather than introducing lower-level infrastructure management.

This keeps the project focused on application architecture, data, automation and AI while still demonstrating practical cloud deployment and distributed service integration.

The trade-off is reduced infrastructure-level control compared with architectures based on directly managed virtual machines, containers or more extensive cloud infrastructure.

For the current project objectives, this abstraction is intentional.

### Portfolio-grade versus Production-grade Architecture

The v1.1.0 deployment demonstrates a functional public cloud architecture but is deliberately classified as portfolio-grade rather than production-ready.

The current architecture prioritizes:

- functional end-to-end integration;
- architectural separation;
- reproducibility;
- maintainability;
- public demonstration;
- controlled LLM integration.

Production hardening would introduce additional concerns such as authentication, authorization, observability, scalable persistence, centralized secrets management, resilience and additional operational controls.

These capabilities can be introduced incrementally without fundamentally redesigning the current application architecture.

---

## Current Limitations and Future Evolution

The v1.1.0 cloud deployment establishes a functional distributed architecture and public end-to-end application flow.

However, the current deployment intentionally remains limited in areas that would require additional production hardening.

### Current Limitations

The current architecture does not yet include:

- production-grade managed database infrastructure;
- user authentication and authorization;
- role-based access control;
- centralized observability and monitoring;
- production-grade logging and alerting;
- centralized secrets management;
- automated CI/CD validation pipelines;
- explicit scalability and high-availability mechanisms;
- advanced API protection and rate limiting;
- comprehensive operational recovery procedures.

These limitations do not prevent the current application from fulfilling its portfolio and demonstration objectives, but they would become relevant requirements for a production enterprise deployment.

### Future Evolution

Potential production-hardening capabilities include:

#### Managed Relational Database

SQLite may be replaced by a managed relational database such as PostgreSQL to provide stronger durability, concurrent access, centralized management and production-oriented persistence.

#### Authentication and Authorization

Identity and access controls may be introduced to ensure that application capabilities and business information are available only to authorized users.

#### Observability

Structured logging, metrics, monitoring and alerting may be introduced to provide visibility into application health, failures, latency, external API consumption and operational behavior.

#### Centralized Secrets Management

Sensitive credentials may be migrated to a dedicated secrets-management service with capabilities such as controlled access, rotation and auditing.

#### Containerization

Application components may be containerized to improve environment consistency, portability and deployment reproducibility.

#### CI/CD Automation

The current Git-based deployment workflow may evolve toward automated pipelines that execute tests and engineering validations before deployment.

#### Scalability and Resilience

Future versions may introduce infrastructure and application mechanisms designed for increased traffic, concurrent users, fault tolerance and service availability.

#### AI Governance and Operational Controls

Additional controls may be introduced for model configuration, usage monitoring, token consumption, cost management, response traceability and model evaluation.

### Evolution Principle

Future infrastructure improvements should preserve the architectural boundaries already established in the application.

The objective is to evolve individual infrastructure capabilities without unnecessarily coupling the frontend, business logic, data layer and AI integration.

The current architecture therefore acts as a foundation for incremental production hardening rather than requiring a complete redesign.

---

## Deployment Summary

The v1.1.0 cloud deployment transforms the AI Supply Chain Copilot from a locally executed application into a publicly accessible distributed solution while preserving the architectural boundaries established during development.

The deployment separates frontend hosting, backend execution and external LLM inference across independent services connected through explicit interfaces and environment-based configuration.

The resulting runtime flow is:

`User → Streamlit Community Cloud → FastAPI on Render → deterministic analytics/context → AI Service → LLM Client → OpenAI API → FastAPI → Streamlit → User`

The deployment validates that the same application architecture can operate beyond the local development environment without embedding cloud-specific behavior into the core business logic.

The current implementation should be understood as a functional portfolio-grade cloud architecture. It demonstrates public deployment, distributed service integration, runtime configuration, secret isolation and end-to-end AI orchestration while maintaining a clear path toward future production hardening.

The primary architectural principle remains unchanged:

**Deterministic business logic remains under application control, while Generative AI is used for interpretation, synthesis and natural-language communication.**