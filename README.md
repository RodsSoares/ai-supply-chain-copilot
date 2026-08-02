# AI Supply Chain Copilot

> **End-to-end AI, Data Engineering and Decision Support platform for Supply Chain operations.**

An enterprise-inspired software engineering project that simulates a real Supply Chain environment using synthetic ERP data.

Rather than presenting isolated programming exercises, this repository evolves as a complete business application through incremental development sprints, demonstrating practical skills in Data Engineering, Software Engineering, Analytics and Artificial Intelligence.

---

# Overview

The objective of this project is to demonstrate how modern Supply Chain problems can be solved through software engineering and AI.

The application is being developed around a realistic inventory management scenario, combining:

- Python
- ETL Pipelines
- SQLite
- Data Analytics
- Business Rules
- Software Engineering
- AI-ready Architecture

All datasets are synthetic and inspired by real business processes, ensuring complete confidentiality while preserving realistic operational scenarios.

---

# Current Status

| Module | Status |
|----------|--------|
| Project Architecture | ✅ |
| Synthetic ERP Dataset | ✅ |
| Inventory Analytics | ✅ |
| Business Rules Engine | ✅ |
| ETL Pipeline | ✅ |
| SQLite Database | ✅ |
| Automated Project Audit | ✅ |
Configurable Business Rules | ✅ |
| SQL Analytics | 🚧 |
| KPI Engine | 🚧 |
| REST API | ⏳ |
| Dashboard | ⏳ |
| AI Copilot | ⏳ |
| Cloud Deployment | ⏳ |

---

# Main Objectives

This repository demonstrates practical implementation of:

- Data Engineering
- Software Engineering
- AI-ready Architecture
- Supply Chain Analytics
- Business Process Automation
- Decision Support Systems

The focus is not simply learning programming syntax, but designing maintainable business software following professional engineering practices.

---

# Technology Stack

| Category | Technologies |
|----------|--------------|
| Language | Python |
| Data Processing | Pandas |
| Configuration | JSON |
| Database | SQLite |
| Version Control | Git / GitHub |
| IDE | Visual Studio Code |
| Documentation | Markdown |

Future planned technologies include:

- FastAPI
- PostgreSQL
- Docker
- Power BI
- Azure AI Services
- Large Language Models (LLMs)

---

# High-Level Architecture

                     business_rules.json
                              │
                              ▼
Synthetic ERP Dataset → Validation → Metrics
                               │
                               ▼
                         Business Scoring
                               │
                               ▼
                         Decision Engine
                               │
                               ▼
                      Reporting / Export
                               │
                               ▼
                            SQLite
                               │
                               ▼
                         Future REST API
                               │
                               ▼
                      AI Supply Chain Copilot
```

---

# Project Structure

```text
AI-SUPPLY-CHAIN-COPILOT/

├── config/
│   └── business_rules.json
│
├── data/
├── database/
├── docs/
├── output/
├── sample_data/
├── scripts/
├── src/
├── tests/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Getting Started

Clone the repository:

```bash
git clone <repository-url>
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Execute the inventory analysis:

```bash
python scripts/analyze_inventory.py
```

The generated analysis will be available in:

```text
output/inventory_analysis.csv
```

---

# Automated Project Audit

To ensure architectural consistency throughout the project lifecycle, the repository includes an automated auditing tool.

Run:

```bash
python scripts/project_audit.py
```

The auditor automatically generates:

- Project Health score
- Architecture overview
- Pipeline overview
- Python module inventory
- Function catalog
- Internal dependency graph
- Repository consistency checks
- Syntax validation
- Documentation coverage
- TODO / FIXME detection

Output:

```text
docs/project_audit/PROJECT_AUDIT.md
```

Instead of relying on manually maintained technical documentation, the project continuously documents itself through automated analysis, helping keep documentation synchronized with the implementation.

---

# Engineering Practices

This project follows a set of engineering principles intended to support long-term maintainability.

- Modular Architecture
- Separation of Responsibilities
- Business-driven Development
- Synthetic Enterprise Dataset
- Automated Project Audit
- Continuous Refactoring
- Incremental Delivery
- Technical Documentation
- Version Control
- AI-ready Design

## Business Rules Configuration

Business parameters are centralized in a dedicated configuration layer (`config/business_rules.json`).

This approach separates business rules from application logic, allowing thresholds, scoring weights and operational parameters to evolve without modifying the Python implementation.

Current configurable parameters include:

- Inventory conversion parameters
- Financial scoring thresholds
- ABC classification weights
- Stockout risk scoring
- Lead time scoring
- Priority thresholds

This design prepares the application for future administrative interfaces and REST APIs while keeping the core business logic modular and maintainable.

---

# Development Workflow

```text
Develop Feature

        │

        ▼

Execute Pipeline

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
```

---

# Roadmap

| Milestone | Status |
|-----------|--------|
| Project Setup | ✅ |
| Inventory Analytics MVP | ✅ |
| Business Rules Engine | ✅ |
| Automated Project Audit | ✅ |
| SQL Analytics | 🚧 |
| KPI Engine | 🚧 |
| REST API | ⏳ |
| Dashboard | ⏳ |
| AI Copilot | ⏳ |
| Cloud Deployment | ⏳ |

---

# Why this project?

Modern Supply Chain organizations increasingly rely on automation, analytics and AI-assisted decision making.

This project demonstrates how software engineering, data engineering and artificial intelligence can be integrated to build maintainable business solutions inspired by realistic enterprise workflows while preserving corporate confidentiality through fully synthetic datasets.

---

# Repository Purpose

This repository serves as a long-term engineering portfolio focused on building an end-to-end Supply Chain application instead of isolated programming exercises.

Every sprint adds a production-inspired capability while preserving architecture quality, documentation and maintainability.

---

# License

This repository is intended for educational and portfolio purposes.

All datasets, business rules and scenarios are fictional or synthetically generated and do not contain confidential corporate information.