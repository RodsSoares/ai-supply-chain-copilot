# AI Supply Chain Copilot — Product Backlog

> Registro estruturado das oportunidades de evolução identificadas durante o desenvolvimento do AI Supply Chain Copilot.
>
> **Importante:** este documento não representa entregas comprometidas. Itens somente passam a fazer parte do escopo quando são formalmente priorizados e movidos para o **Roadmap**.

---

# Objetivo

O backlog existe para preservar oportunidades de evolução do produto sem comprometer o escopo das releases atuais.

Ao final de cada release, itens implementados devem ser removidos do backlog ou registrados como concluídos na documentação de versão. Novas oportunidades identificadas durante o desenvolvimento podem ser adicionadas e posteriormente repriorizadas.

---

# Regras

- O **Roadmap** contém entregas comprometidas.
- O **Backlog** contém possibilidades futuras.
- Novas ideias não alteram automaticamente o escopo da release atual.
- Itens podem ser reavaliados, repriorizados, divididos ou descartados.
- Itens implementados deixam de representar backlog.
- Projetos derivados permanecem separados do produto principal.
- O backlog deve permanecer simples, rastreável e de fácil manutenção.

---

# Entregas removidas do backlog na v1.0.0

Durante a revisão da release **v1.0.0 — Functional AI Copilot**, os seguintes itens deixaram de representar trabalho futuro:

| ID | Entrega | Status |
| :--- | :--- | :---: |
| QA-001 | Testes automatizados do motor e da integração AI | ✅ v1.0.0 |
| AI-003 | Copiloto de Supply Chain com perguntas em linguagem natural | ✅ v1.0.0 |

A evolução conversacional **multi-turn**, com manutenção de contexto entre interações, permanece como uma capacidade futura e foi registrada como um novo item específico no backlog.

---

# Resumo do backlog

- Total de itens: **18**
- Prioridade P1: **5**
- Prioridade P2: **8**
- Prioridade P3: **5**
- Projetos derivados: **3**

---

# Backlog

| Nº | ID | Epic | Melhoria | Prioridade | Release Alvo |
| :-: | :--- | :--- | :--- | :---: | :---: |
| 01 | DATA-001 | Data Governance | Data Quality Score | 🔴 P1 | Onda 1 |
| 02 | DATA-002 | Data Governance | Data Lineage | 🟡 P2 | Onda 2 |
| 03 | RULE-001 | Decision Engine | Versionamento das Business Rules | 🔴 P1 | Onda 1 |
| 04 | RULE-002 | Decision Engine | Registro estruturado da explicação das decisões | 🔴 P1 | Onda 1 |
| 05 | OPS-001 | Observability | Logs estruturados de processamento | 🔴 P1 | Onda 1 |
| 06 | OPS-002 | Observability | Monitoramento da API e processamento | 🟡 P2 | Onda 2 |
| 07 | AI-001 | Explainable AI | Explainable AI e rastreabilidade das interpretações | 🔴 P1 | Onda 2 |
| 08 | AI-002 | AI Governance | Guardrails de conteúdo e validação das respostas da IA | 🟡 P2 | Onda 2 |
| 09 | AI-004 | AI Copilot | Consulta RAG a políticas e procedimentos internos | 🟡 P2 | Onda 3 |
| 10 | AI-005 | AI Reliability | Resiliência e tratamento de erros do provedor LLM | 🟡 P2 | Onda 2 |
| 11 | AI-006 | AI Copilot | Conversação multi-turn com memória de contexto | 🟢 P3 | Onda 3 |
| 12 | ARCH-001 | Infrastructure | Docker | 🟡 P2 | Onda 2 |
| 13 | ARCH-002 | Infrastructure | Avaliação de migração para PostgreSQL | 🟢 P3 | Onda 3 |
| 14 | BIZ-001 | Business Analytics | Simulações "What-if" | 🟡 P2 | Onda 3 |
| 15 | BIZ-002 | Business Analytics | Simulação de impacto financeiro | 🟡 P2 | Onda 3 |
| 16 | EXP-001 | Portfolio Labs | LinkedIn Content Agent | 🟢 P3 | Projeto derivado |
| 17 | EXP-002 | Portfolio Labs | Gerador inteligente de documentação | 🟢 P3 | Projeto derivado |
| 18 | EXP-003 | Portfolio Labs | Assistente inteligente da auditoria | 🟢 P3 | Projeto derivado |

---

# Detalhamento de itens AI

## AI-001 — Explainable AI

Evoluir a explicabilidade das análises produzidas pelo Copilot, permitindo maior rastreabilidade entre dados de origem, regras determinísticas, contexto enviado ao LLM e interpretação apresentada ao usuário.

---

## AI-002 — AI Guardrails

Implementar mecanismos adicionais de governança das respostas geradas pelo LLM, incluindo validação de conteúdo, restrições de comportamento e controles para reduzir respostas incompatíveis com o contexto analítico fornecido pela aplicação.

Os safeguards operacionais já existentes — como ativação explícita do Real LLM, contexto controlado e limites de resposta — permanecem independentes deste item.

---

## AI-004 — RAG

Permitir que o Copilot consulte documentação corporativa, políticas, procedimentos e conhecimento não estruturado através de uma arquitetura de **Retrieval-Augmented Generation (RAG)**.

A evolução deverá preservar a separação entre:

- dados estruturados e regras determinísticas;
- conhecimento documental recuperado;
- interpretação probabilística realizada pelo LLM.

---

## AI-005 — AI Reliability

Aprimorar a resiliência da integração com provedores externos de LLM.

Possíveis evoluções incluem:

- tratamento específico de timeout;
- rate limits;
- indisponibilidade do provedor;
- falhas de autenticação;
- respostas inválidas ou inesperadas;
- políticas controladas de retry;
- estratégias futuras de fallback.

---

## AI-006 — Multi-turn Conversation

Evoluir o endpoint atual de perguntas independentes para uma experiência conversacional capaz de preservar contexto entre múltiplas interações.

Este item não substitui o Copilot funcional entregue na v1.0.0. Representa uma evolução da experiência de interação e gerenciamento de contexto.

---

# Ondas sugeridas

## Onda 1 — Confiabilidade do motor

Prioridade para fortalecer governança, rastreabilidade e observabilidade das camadas determinísticas.

- Data Quality Score
- Versionamento das Business Rules
- Registro estruturado das decisões
- Logs estruturados de processamento

---

## Onda 2 — Governança, infraestrutura e confiabilidade AI

Prioridade para fortalecer a aplicação antes de ampliar significativamente as capacidades do Copilot.

- Data Lineage
- Monitoramento da API e processamento
- Explainable AI
- Guardrails de conteúdo e validação
- Resiliência do provedor LLM
- Docker

---

## Onda 3 — Evolução do produto

Capacidades que ampliam a experiência e o valor analítico da solução.

- RAG para políticas e procedimentos internos
- Conversação multi-turn com memória de contexto
- Simulações "What-if"
- Simulação de impacto financeiro
- Avaliação de migração para PostgreSQL

---

# Projetos derivados

Itens classificados como **Portfolio Labs** permanecem fora do escopo principal do AI Supply Chain Copilot e poderão originar repositórios independentes.

Projetos atualmente registrados:

- **EXP-001 — LinkedIn Content Agent**
- **EXP-002 — Gerador inteligente de documentação**
- **EXP-003 — Assistente inteligente da auditoria**

Esses projetos podem reutilizar conceitos, padrões arquiteturais ou componentes desenvolvidos no Copilot, mas possuem objetivos independentes.

---

# Revisão do backlog

Ao final de cada release:

1. Revisar todos os itens existentes.
2. Identificar itens entregues e removê-los do backlog ativo.
3. Registrar novas oportunidades identificadas durante o desenvolvimento.
4. Reavaliar prioridade e release alvo.
5. Mover para o Roadmap apenas itens formalmente aprovados.
6. Manter o restante como registro estruturado de oportunidades futuras.

---

# Princípio do projeto

**O Roadmap representa compromissos de entrega.**

**O Backlog representa oportunidades futuras.**

Nenhum item do backlog altera automaticamente o escopo de uma release sem priorização formal.