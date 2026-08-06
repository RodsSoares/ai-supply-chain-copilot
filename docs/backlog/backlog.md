# AI Supply Chain Copilot — Product Backlog

> Registro das melhorias identificadas durante o desenvolvimento.
>
> **Importante:** este documento **não altera o escopo do MVP**. Apenas
> registra oportunidades para futuras evoluções.

---

# Objetivo

O backlog existe para preservar ideias sem comprometer o cronograma
atual.

Um item somente deixa este documento quando for explicitamente
priorizado e incluído no **Roadmap**.

---

# Regras

-   O **Roadmap** contém entregas comprometidas.
-   O **Backlog** contém possibilidades futuras.
-   Novas ideias **não alteram** o escopo congelado do MVP.
-   Itens podem ser reavaliados, repriorizados ou descartados.
-   O backlog deve permanecer simples e de fácil manutenção.

---

## Resumo do backlog

- Total de itens: **19**
- Prioridade P1: **5**
- Prioridade P2: **8**
- Prioridade P3: **6**
- Projetos derivados: **3**

---

# Backlog

|  Nº | ID       | Epic               | Melhoria                                 | Prioridade |   Release Alvo   |
| :-: | :------- | :----------------- | :--------------------------------------- | :--------: | :--------------: |
|  01 | DATA-001 | Data Governance    | Data Quality Score                       |    🔴 P1   |      Onda 1      |
|  02 | DATA-002 | Data Governance    | Data Lineage                             |    🟡 P2   |      Onda 2      |
|  03 | RULE-001 | Decision Engine    | Versionamento das Business Rules         |    🔴 P1   |      Onda 1      |
|  04 | RULE-002 | Decision Engine    | Registro da explicação das decisões      |    🔴 P1   |      Onda 1      |
|  05 | QA-001   | Reliability        | Testes automatizados do motor de decisão |    🔴 P1   |      Onda 1      |
|  06 | OPS-001  | Observability      | Logs estruturados de processamento       |    🔴 P1   |      Onda 1      |
|  07 | OPS-002  | Observability      | Monitoramento da API e processamento     |    🟡 P2   |      Onda 2      |
|  08 | AI-001   | Explainable AI     | Explainable AI                           |    🔴 P1   |      Onda 2      |
|  09 | AI-002   | Explainable AI     | Guardrails para respostas da IA          |    🟡 P2   |      Onda 2      |
|  10 | AI-003   | AI Copilot         | Copiloto conversacional de Supply Chain  |    🟢 P3   |      Onda 3      |
|  11 | ARCH-001 | Infrastructure     | Docker                                   |    🟡 P2   |      Onda 2      |
|  12 | ARCH-002 | Infrastructure     | Avaliação de migração para PostgreSQL    |    🟢 P3   |      Onda 3      |
|  13 | BIZ-001  | Business Analytics | Simulações "What-if"                     |    🟡 P2   |      Onda 3      |
|  14 | BIZ-002  | Business Analytics | Simulação de impacto financeiro          |    🟡 P2   |      Onda 3      |
|  15 | PROD-001 | Product Management | Geração automática do PROJECT_STATUS.md  |    🟡 P2   |      Onda 1      |
|  16 | EXP-001  | Portfolio Labs     | LinkedIn Content Agent                   |    🟢 P3   | Projeto derivado |
|  17 | EXP-002  | Portfolio Labs     | Gerador inteligente de documentação      |    🟢 P3   | Projeto derivado |
|  18 | EXP-003  | Portfolio Labs     | Assistente inteligente da auditoria      |    🟢 P3   | Projeto derivado |
|  19 | AI-004 | AI Copilot | Consulta RAG a políticas e procedimentos internos  |    🟡 P2   |      Onda 3      |

---

# Ondas sugeridas

## Onda 1 --- Confiabilidade

-   Data Quality Score
-   Versionamento das regras
-   Registro das decisões
-   Testes automatizados
-   Logs estruturados
-   PROJECT_STATUS automático

## Onda 2 --- Governança e IA

-   Data Lineage
-   Monitoramento
-   Explainable AI
-   Guardrails
-   Docker

## Onda 3 --- Evolução do produto

-   Copiloto conversacional
-   Simulações de negócio
-   Avaliação PostgreSQL

## Projetos derivados

Itens classificados como **Experimento** deverão permanecer fora do
escopo do AI Supply Chain Copilot e poderão originar repositórios
independentes.

Exemplo:

-   LinkedIn Content Agent
-   Gerador inteligente de documentação
-   Assistente inteligente da auditoria

---

# Revisão

Ao final de cada release:

1.  Revisar este backlog.
2.  Repriorizar os itens quando necessário.
3.  Mover para o Roadmap apenas melhorias aprovadas.
4.  Manter o restante como registro de evolução do produto.

---

Princípio do projeto

O Roadmap representa compromissos de entrega.
O Backlog representa oportunidades futuras.
Nenhum item do backlog altera o escopo do MVP sem priorização formal.