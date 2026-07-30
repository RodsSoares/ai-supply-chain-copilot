# AI Supply Chain Copilot

> Um projeto de automação de Supply Chain desenvolvido em Python para demonstrar como análise de dados, regras de negócio e Inteligência Artificial podem apoiar decisões de gestão de estoque.

---

# Objetivo

O **AI Supply Chain Copilot** é um projeto de portfólio desenvolvido para simular um sistema corporativo de apoio à decisão em Supply Chain.

O objetivo é demonstrar a aplicação prática de Python, Pandas, arquitetura de software e, futuramente, Inteligência Artificial, em problemas reais de gestão de estoques.

Todo o projeto utiliza **dados sintéticos**, preservando integralmente a confidencialidade de informações corporativas.

---

# Problema de Negócio

Uma empresa precisa responder diariamente perguntas como:

- Quais produtos precisam ser repostos?
- Quais produtos possuem excesso de estoque?
- Qual o impacto financeiro de cada decisão?
- Quais itens possuem maior prioridade?
- Como priorizar ações quando existem centenas de SKUs?

Responder essas perguntas manualmente é lento e sujeito a erros.

Este projeto automatiza todo esse processo.

---

# Funcionalidades

Atualmente o sistema realiza automaticamente:

- Importação de dados do ERP (CSV)
- Validação da qualidade dos dados
- Cálculo do valor do estoque
- Cálculo da cobertura de estoque
- Identificação de risco de ruptura
- Identificação de excesso de estoque
- Cálculo do impacto financeiro
- Score multicritério de priorização
- Classificação automática das prioridades
- Agrupamento gerencial
- Relatório executivo
- Exportação dos resultados

---

# Arquitetura

O projeto foi estruturado em módulos independentes, seguindo o princípio de **Responsabilidade Única (Single Responsibility Principle)**.

```
                 ERP CSV
                    │
                    ▼
        inventory_validation
                    │
                    ▼
         inventory_metrics
                    │
                    ▼
         inventory_scoring
                    │
                    ▼
         inventory_decision
                    │
                    ▼
        inventory_reporting
                    │
                    ▼
          inventory_export
                    │
                    ▼
             CSV Final
```

Cada módulo possui uma única responsabilidade, tornando o projeto mais organizado, reutilizável e fácil de evoluir.

---

# Estrutura do Projeto

```
AI-Supply-Chain-Copilot/

│
├── sample_data/
│
├── output/
│
├── scripts/
│   ├── analyze_inventory.py
│   ├── inventory_validation.py
│   ├── inventory_metrics.py
│   ├── inventory_scoring.py
│   ├── inventory_decision.py
│   ├── inventory_reporting.py
│   └── inventory_export.py
│
├── requirements.txt
│
└── README.md
```

---

# Tecnologias Utilizadas

- Python
- Pandas
- NumPy
- CSV
- Git
- GitHub
- Visual Studio Code

Planejado para as próximas versões:

- SQLite
- FastAPI
- Streamlit
- OpenAI API
- Azure AI Foundry

---

# Como Executar

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
python scripts/analyze_inventory.py
```

Os resultados serão exportados automaticamente para a pasta de saída do projeto.

---

# Roadmap

## Sprint 1 — Fundamentos

- Leitura do CSV
- Exploração dos dados
- Estrutura inicial

**Status:** ✅ Concluída

---

## Sprint 2 — Motor de Análise

- Indicadores
- Cobertura
- Valor financeiro
- Reposição
- Excesso
- Score
- Priorização

**Status:** ✅ Concluída

---

## Sprint 2.5 — Arquitetura Modular

- Separação por módulos
- Pipeline de processamento
- Organização do projeto
- Exportação automatizada
- Relatórios

**Status:** ✅ Concluída

---

## Sprint 3

- Banco de Dados SQLite
- Persistência dos dados
- Camada de acesso aos dados

**Status:** 🔜 Planejada

---

## Sprint 4

- Testes automatizados
- Pytest

**Status:** 🔜 Planejada

---

## Sprint 5

- Dashboard interativo
- Streamlit

**Status:** 🔜 Planejada

---

## Sprint 6

- IA Generativa
- Assistente para Supply Chain
- Consultas em linguagem natural
- Recomendações inteligentes

**Status:** 🔜 Planejada

---

# Aprendizados Aplicados

Durante o desenvolvimento deste projeto foram praticados conceitos de:

- Programação em Python
- Pandas
- Estruturas de Dados
- Modularização
- Organização em camadas
- Single Responsibility Principle
- Regras de Negócio
- Análise de Dados
- Automação
- Engenharia de Software
- Versionamento com Git

---

# Próximos Objetivos

O objetivo final deste projeto é evoluir de um motor de análise de estoque para um **Copilot de Supply Chain**, capaz de:

- interpretar indicadores automaticamente;
- responder perguntas em linguagem natural;
- sugerir ações para o gestor;
- gerar relatórios executivos;
- apoiar decisões utilizando Inteligência Artificial.

---

# Autor

Desenvolvido por **Rodrigo Soares** como projeto de portfólio para transição de carreira para **IA, Automação e Data Analytics**, aplicando experiência em Supply Chain, Planejamento Operacional e Inteligência de Negócios.

---

## Versão

**v0.3.0**

**Sprint 2.5 concluída** ✅