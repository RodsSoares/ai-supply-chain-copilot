# 🤖 AI Supply Chain Copilot

> End-to-end Supply Chain automation and decision-support project built with Python and Artificial Intelligence.

# ==========================================
# AI Supply Chain Copilot
#
# Version: v0.2.0
#
# Inventory Analytics MVP
# ==========================================

## 📌 About the Project

The **AI Supply Chain Copilot** is a portfolio project that simulates a corporate Supply Chain environment and progressively transforms operational ERP data into actionable business recommendations.

The project is inspired by real Supply Chain challenges, especially inventory planning, demand variability, operational risk and decision support.

All datasets used in this repository are **fictional and synthetically generated**. No confidential corporate information is included.

Rather than using isolated programming exercises, the project applies Python and AI concepts directly to realistic business processes involving:

- Inventory management
- Procurement
- Logistics
- Demand planning
- Operational analytics
- Decision automation

---

## 🎯 Project Goals

The project will progressively evolve into an AI-powered Supply Chain assistant capable of:

- Reading operational ERP files
- Validating and cleaning business data
- Calculating inventory and Supply Chain KPIs
- Identifying stock shortages and excess inventory
- Estimating the financial impact of recommended actions
- Detecting stockout risks
- Prioritizing operational decisions
- Forecasting demand
- Detecting anomalies
- Answering business questions using natural language
- Generating automated operational recommendations

---

## ✅ Current Capabilities

The current version already provides a functional inventory analytics pipeline.

### Data ingestion

- Reads synthetic ERP inventory data from CSV
- Handles Brazilian-compatible CSV exports
- Produces a consolidated enriched dataset

### Data validation

- Counts total records
- Identifies missing SKU values
- Identifies duplicated SKUs
- Checks missing values in critical fields
- Displays problematic records for investigation

### Inventory analytics

- Calculates total inventory value
- Calculates stock coverage in months
- Converts supplier lead time from days to months
- Identifies potential stockout risk
- Calculates replenishment quantities
- Calculates excess inventory quantities

### Financial analysis

- Estimates replenishment cost
- Estimates the financial value of excess inventory
- Consolidates the financial impact of each recommended action

### Decision support

Each SKU receives two independent classifications:

- `acao_recomendada`: what should be done
- `prioridade`: how important the action is

Current actions:

- `REPOR`
- `TRATAR EXCESSO`
- `SEM AÇÃO`

Current priority levels:

- `ALTA`
- `MÉDIA`
- `BAIXA`
- `SEM AÇÃO`

### Output

The pipeline exports a single consolidated file:

```text
output/inventory_analysis.csv
```

This dataset can be consumed by:

- Microsoft Excel
- Power Query
- Power BI
- Python
- Databases
- Future application interfaces

---

## 🔄 Current Data Pipeline

```text
Synthetic ERP Inventory CSV
            │
            ▼
      Pandas DataFrame
            │
            ▼
   Data Quality Validation
            │
            ▼
 Inventory KPI Calculation
            │
            ▼
 Coverage and Stockout Risk
            │
            ▼
 Recommended Business Action
            │
            ▼
 Financial Impact and Priority
            │
            ▼
 Consolidated Analytical CSV
```

---

## 🏗 Target Architecture

```text
       ERP Files / Invoices / Operational Data
                        │
                        ▼
             Data Extraction and Validation
                        │
                        ▼
                 Structured Database
                        │
                        ▼
              Business Rules and KPIs
                        │
                        ▼
           Decision and Prioritization Engine
                        │
                        ▼
              Dashboard / Web Interface
                        │
                        ▼
             AI Supply Chain Copilot
                        │
                        ▼
       Natural-Language Business Recommendations
```

---

## 🚀 Technologies

### Currently in use

- Python
- Pandas
- Git
- GitHub
- Visual Studio Code
- CSV
- Microsoft Excel

### Planned evolution

- NumPy
- SQLite
- Streamlit
- FastAPI
- Power BI
- Machine Learning
- Azure AI
- Azure OpenAI or OpenAI API
- Microsoft Semantic Kernel

The final technology stack may evolve according to the needs identified during development.

---

## 📂 Project Structure

```text
ai-supply-chain-copilot/
│
├── assets/          # Images and visual project assets
├── backend/         # Future application and API logic
├── database/        # Future database files and scripts
├── docs/            # Technical and business documentation
├── frontend/        # Future user interface
├── notebooks/       # Exploratory analysis and experiments
├── output/          # Consolidated analytical outputs
├── sample_data/     # Fictional ERP datasets
├── scripts/         # Data-processing and analytical scripts
├── tests/           # Future automated tests
│
├── .gitignore
├── README.md
└── requirements.txt
```

Current main files:

```text
sample_data/erp_inventory.csv
scripts/analyze_inventory.py
output/inventory_analysis.csv
```

---

## ▶️ Running the Current Pipeline

From the project root directory, activate the virtual environment and run:

```bash
python scripts/analyze_inventory.py
```

The script will:

1. Read the synthetic ERP dataset
2. Explore and validate the data
3. Calculate inventory indicators
4. Identify recommended actions
5. Classify priorities
6. Display an executive summary
7. Export the consolidated analytical dataset

Generated output:

```text
output/inventory_analysis.csv
```

> The output CSV must be closed in Excel before rerunning the script, otherwise Windows may prevent Python from replacing the file.

---

## 🗺 Roadmap

### Phase 1 — Project Foundations

- [x] Create the project structure
- [x] Configure the Python virtual environment
- [x] Configure Git
- [x] Publish the GitHub repository
- [x] Create the initial documentation
- [x] Configure project dependencies

### Phase 2 — Synthetic ERP Simulation

- [x] Create the synthetic inventory dataset
- [x] Read ERP data with Pandas
- [x] Explore dataset structure and data types
- [x] Validate missing and duplicated SKUs
- [x] Export an enriched consolidated dataset
- [ ] Add inventory movement history
- [ ] Add purchase-order data
- [ ] Add demand forecast data
- [ ] Add synthetic invoice extraction

### Phase 3 — Supply Chain Analytics

- [x] Calculate inventory value
- [x] Identify replenishment requirements
- [x] Identify excess inventory
- [x] Calculate replenishment financial impact
- [x] Calculate excess inventory financial impact
- [x] Calculate stock coverage
- [x] Compare coverage against supplier lead time
- [x] Identify potential stockout risk
- [x] Generate recommended actions
- [x] Generate financial priority levels
- [ ] Develop a multicriteria priority score
- [ ] Include ABC classification in prioritization
- [ ] Calculate inventory turnover
- [ ] Calculate safety stock
- [ ] Calculate forecast accuracy

### Phase 4 — Decision Engine

- [ ] Combine financial impact, ABC class, coverage and lead time
- [ ] Generate explainable SKU recommendations
- [ ] Detect operational exceptions and anomalies
- [ ] Produce automated management summaries
- [ ] Add business rules configuration

### Phase 5 — Artificial Intelligence

- [ ] Create natural-language queries
- [ ] Connect an LLM to the analytical dataset
- [ ] Generate contextual business explanations
- [ ] Create an AI Supply Chain assistant
- [ ] Add demand forecasting models
- [ ] Add recommendation traceability

### Phase 6 — Application and Deployment

- [ ] Build a web interface
- [ ] Create interactive dashboards
- [ ] Develop a backend API
- [ ] Add automated tests
- [ ] Deploy the application
- [ ] Publish the final portfolio case

---

## 📈 Current Status

```text
Version: v0.2.0
Milestone: Inventory Analytics MVP
Status: Functional
```

Current workflow:

```text
ERP data
→ validation
→ inventory analytics
→ operational risk
→ recommended action
→ financial priority
→ consolidated export
```

The project has moved beyond its initial setup and now contains a functional analytical module capable of transforming raw inventory data into operational decision-support information.

---

## 🔐 Data Confidentiality

This project is inspired by realistic Supply Chain processes, but all data, companies, suppliers, products and operational scenarios are fictional.

No proprietary or confidential corporate information is used or published.

---

## 👨‍💻 Author

**Rodrigo Soares**

- Mechanical Engineer
- Supply Chain and Operational Planning Professional
- AI Automation Specialist in development

---

## 📄 License

This project is intended for educational and portfolio purposes.