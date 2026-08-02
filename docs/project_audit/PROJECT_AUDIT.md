# Project Audit

Gerado em: 02/08/2026 02:16:52

> Este arquivo é gerado automaticamente. Não edite manualmente.

## 1. Resumo executivo

- Arquivos Python: **13**
- Linhas totais: **1124**
- Linhas efetivas de código: **844**
- Funções: **39**
- Classes: **0**
- Imports internos: **9**
- Imports externos: **9**
- Imports da biblioteca padrão: **8**
- TODOs/FIXMEs em comentários: **0**
- Funções sem docstring: **0**
- Arquivos com erro de sintaxe: **0**

## 2. Como usar as opções True e False

As variáveis abaixo ficam no início de `project_audit.py`:

```python
INCLUIR_CODIGO_FONTE = False
INCLUIR_FERRAMENTAS_AUDITORIA = False
```

- `False`: mantém a opção desativada.
- `True`: ativa a opção.
- Para o checkpoint normal, mantenha as duas como `False`.
- Ative `INCLUIR_CODIGO_FONTE` somente quando precisar enviar todo o código para revisão.
- Ative `INCLUIR_FERRAMENTAS_AUDITORIA` somente quando quiser auditar também o próprio auditor.

## 3. Pipeline principal

```text
analyze_inventory.py
↓
inventory_validation.py
↓
inventory_metrics.py
↓
inventory_scoring.py
↓
inventory_decision.py
↓
inventory_reporting.py
↓
inventory_export.py
```

## 4. Project Health

> Notas heurísticas calculadas automaticamente.

| Dimensão | Nota |
|---|---:|
| Modularização | 10.0/10 |
| Cobertura de docstrings | 10.0/10 |
| Complexidade estrutural | 10.0/10 |
| Integridade sintática | 10.0/10 |
| Saúde geral | **10.0/10** |

## 5. Estrutura do projeto

```text
ai-supply-chain-copilot/
├── .gitignore
├── assets/
│   ├── .gitkeep
│   ├── images/
│   │   └── .gitkeep
│   └── screenshots/
│       └── .gitkeep
├── backend/
│   └── .gitkeep
├── data/
│   ├── processed/
│   │   └── .gitkeep
│   ├── raw/
│   │   ├── depositos.csv
│   │   └── produtos.csv
│   └── synthetic/
│       └── .gitkeep
├── database/
│   └── inventory.db
├── docs/
│   ├── architecture/
│   │   ├── 01_system_overview.md
│   │   ├── 02_current_architecture.md
│   │   ├── 03_data_model.md
│   │   └── 04_decision_log.md
│   ├── decisions/
│   │   └── .gitkeep
│   ├── diagrams/
│   │   └── .gitkeep
│   ├── milestones
│   ├── project_audit/
│   │   └── PROJECT_AUDIT.md
│   └── roadmap/
│       ├── AI_Supply_Chain_Copilot_Gantt_v0.2.0.xlsx
│       └── roadmap.md
├── frontend/
│   └── .gitkeep
├── notebooks/
│   └── .gitkeep
├── output/
│   └── inventory_analysis.csv
├── README.md
├── requirements.txt
├── sample_data/
│   └── erp_inventory.csv
├── scripts/
│   ├── analyze_inventory.py
│   ├── database_setup.py
│   ├── inventory_decision.py
│   ├── inventory_export.py
│   ├── inventory_metrics.py
│   ├── inventory_reporting.py
│   ├── inventory_scoring.py
│   ├── inventory_validation.py
│   └── project_audit.py
├── src/
│   ├── analysis
│   ├── database/
│   │   ├── connection.py
│   │   └── create_tables.py
│   ├── etl/
│   │   ├── load_products.py
│   │   └── load_warehouses.py
│   ├── main.py
│   └── utils/
│       └── .gitkeep
└── tests/
    └── .gitkeep
```

## 6. Arquivos Python

| Arquivo | Linhas | Funções | Classes | TODOs |
|---|---:|---:|---:|---:|
| `scripts/analyze_inventory.py` | 39 | 1 | 0 | 0 |
| `scripts/database_setup.py` | 12 | 0 | 0 | 0 |
| `scripts/inventory_decision.py` | 100 | 5 | 0 | 0 |
| `scripts/inventory_export.py` | 40 | 1 | 0 | 0 |
| `scripts/inventory_metrics.py` | 106 | 5 | 0 | 0 |
| `scripts/inventory_reporting.py` | 228 | 5 | 0 | 0 |
| `scripts/inventory_scoring.py` | 129 | 6 | 0 | 0 |
| `scripts/inventory_validation.py` | 78 | 2 | 0 | 0 |
| `src/database/connection.py` | 18 | 1 | 0 | 0 |
| `src/database/create_tables.py` | 121 | 5 | 0 | 0 |
| `src/etl/load_products.py` | 129 | 4 | 0 | 0 |
| `src/etl/load_warehouses.py` | 124 | 4 | 0 | 0 |
| `src/main.py` | 0 | 0 | 0 | 0 |

## 7. Funções e classes

### `scripts/analyze_inventory.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `main` | 17–35 | `—` | SIM |

### `scripts/database_setup.py`

- Nenhuma função ou classe encontrada.

### `scripts/inventory_decision.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `aplicar_decisoes` | 4–13 | `df` | SIM |
| `calcular_acao_recomendada` | 16–31 | `df` | SIM |
| `calcular_prioridade` | 34–59 | `df` | SIM |
| `gerar_grupo_gerencial` | 62–100 | `df` | SIM |
| `classificar_grupo_gerencial` | 68–95 | `linha` | SIM |

### `scripts/inventory_export.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `exportar_resultados` | 14–40 | `df, caminho_saida` | SIM |

### `scripts/inventory_metrics.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `calcular_metricas` | 4–17 | `df` | SIM |
| `calcular_valor_estoque` | 20–28 | `df` | SIM |
| `calcular_cobertura_e_risco` | 31–64 | `df` | SIM |
| `calcular_quantidades_e_valores` | 67–93 | `df` | SIM |
| `calcular_valor_acao` | 96–106 | `df` | SIM |

### `scripts/inventory_reporting.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `exibir_relatorio` | 4–15 | `df` | SIM |
| `exibir_exploracao` | 18–37 | `df` | SIM |
| `exibir_acoes_recomendadas` | 40–77 | `df` | SIM |
| `exibir_distribuicao_das_acoes` | 80–103 | `df` | SIM |
| `exibir_resumo_executivo` | 106–228 | `df` | SIM |

### `scripts/inventory_scoring.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `calcular_scores` | 4–19 | `df` | SIM |
| `calcular_score_financeiro` | 22–49 | `df` | SIM |
| `calcular_score_classe_abc` | 52–73 | `df` | SIM |
| `calcular_score_risco_ruptura` | 76–89 | `df` | SIM |
| `calcular_score_lead_time` | 92–114 | `df` | SIM |
| `calcular_score_prioridade` | 117–129 | `df` | SIM |

### `scripts/inventory_validation.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `validar_dados` | 17–41 | `df` | SIM |
| `detalhar_problemas` | 44–78 | `df` | SIM |

### `src/database/connection.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `conectar_banco` | 9–18 | `—` | SIM |

### `src/database/create_tables.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `criar_tabela_produtos` | 4–20 | `cursor` | SIM |
| `criar_tabela_depositos` | 23–37 | `cursor` | SIM |
| `criar_tabela_parametros_estoque` | 40–66 | `cursor` | SIM |
| `criar_tabela_movimentacoes_estoque` | 69–94 | `cursor` | SIM |
| `criar_tabelas` | 97–117 | `—` | SIM |

### `src/etl/load_products.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `extrair_produtos` | 11–21 | `—` | SIM |
| `transformar_produtos` | 24–93 | `df` | SIM |
| `carregar_produtos` | 96–114 | `df` | SIM |
| `main` | 117–125 | `—` | SIM |

### `src/etl/load_warehouses.py`

| Função | Linhas | Argumentos | Docstring |
|---|---:|---|---|
| `extrair_depositos` | 11–21 | `—` | SIM |
| `transformar_depositos` | 24–88 | `df` | SIM |
| `carregar_depositos` | 91–109 | `df` | SIM |
| `main` | 112–120 | `—` | SIM |

### `src/main.py`

- Nenhuma função ou classe encontrada.

## 8. Dependências

### Dependências internas

| Origem | Destino |
|---|---|
| `scripts.analyze_inventory` | `scripts.inventory_validation` |
| `scripts.analyze_inventory` | `scripts.inventory_metrics` |
| `scripts.analyze_inventory` | `scripts.inventory_scoring` |
| `scripts.analyze_inventory` | `scripts.inventory_decision` |
| `scripts.analyze_inventory` | `scripts.inventory_reporting` |
| `scripts.analyze_inventory` | `scripts.inventory_export` |
| `src.database.create_tables` | `src.database.connection` |
| `src.etl.load_products` | `src.database.connection` |
| `src.etl.load_warehouses` | `src.database.connection` |

### Dependências externas

- `pandas`

### Grafo de dependências internas

```mermaid
flowchart LR
    scripts_analyze_inventory["scripts.analyze_inventory"] --> scripts_inventory_decision["scripts.inventory_decision"]
    scripts_analyze_inventory["scripts.analyze_inventory"] --> scripts_inventory_export["scripts.inventory_export"]
    scripts_analyze_inventory["scripts.analyze_inventory"] --> scripts_inventory_metrics["scripts.inventory_metrics"]
    scripts_analyze_inventory["scripts.analyze_inventory"] --> scripts_inventory_reporting["scripts.inventory_reporting"]
    scripts_analyze_inventory["scripts.analyze_inventory"] --> scripts_inventory_scoring["scripts.inventory_scoring"]
    scripts_analyze_inventory["scripts.analyze_inventory"] --> scripts_inventory_validation["scripts.inventory_validation"]
    src_database_create_tables["src.database.create_tables"] --> src_database_connection["src.database.connection"]
    src_etl_load_products["src.etl.load_products"] --> src_database_connection["src.database.connection"]
    src_etl_load_warehouses["src.etl.load_warehouses"] --> src_database_connection["src.database.connection"]
```

## 9. Observações automáticas do repositório

- Nenhuma observação de padronização encontrada.

## 10. Pendências e erros

### TODOs e FIXMEs

- Nenhum TODO ou FIXME encontrado em comentários.

### Erros de sintaxe

- Nenhum erro de sintaxe encontrado.
