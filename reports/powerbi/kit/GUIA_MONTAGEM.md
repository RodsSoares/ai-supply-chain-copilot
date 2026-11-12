# Kit Power BI · HUD V6 — Guia de Montagem

Kit para transformar o `AI_Supply_Chain_Copilot.pbix` no dashboard futurista do mockup
(`reports/powerbi/mockups/command_center_mockup.png`), mantendo a identidade visual dos vídeos.

**Princípio:** o PNG de fundo desenha as molduras, os brilhos e os títulos. Os visuais do Power BI
ficam **transparentes** por cima, nas posições exatas listadas abaixo.

```
kit/
├── backgrounds/   bg_command_center.png · bg_inventory.png · bg_transportation.png · layout.json
├── theme/         ai_supply_chain_hud_v6.json
├── data/          fato_estoque · fato_viagens · fato_demanda · dim_rotas · dim_veiculos · dim_semana · copilot_insights (.csv)
├── dax/           medidas.dax
└── deneb/         rede_transporte.json · custo_semanal.json · acoes_prioridade.json
```

Para regenerar os dados: `python scripts/export_powerbi_kit.py`.
Para regenerar os fundos: `node reports/powerbi/kit/backgrounds/src/render.js`.

---

## 0. Pré-requisitos (uma vez)

1. Power BI Desktop atualizado.
2. **Arquivo → Opções e configurações → Opções → Configurações regionais (arquivo atual)**:
   *Português (Brasil)*. Os CSVs usam `;` e vírgula decimal.
3. Visuais personalizados (**Página Inicial → Mais visuais → Do AppSource**):
   - **HTML Content** (Daniel Marsh-Patrick). Use a versão completa, não a *lite*: ela é que permite animações CSS.
   - **Deneb** (Declarative Visualization in Power BI).

## 1. Página e tema

1. Comece pela cópia do `.pbix` atual (ex.: `AI_Supply_Chain_Copilot_HUD.pbix`).
2. **Exibição → Temas → Procurar temas** → `theme/ai_supply_chain_hud_v6.json`.
3. Em cada página: **Formatar página → Configurações da tela → Tipo: Personalizado, 1920 × 1080**.
4. **Formatar página → Plano de fundo da tela → Imagem** → o PNG da página;
   **Ajuste da imagem: Ajustar**; **Transparência: 0%**.
5. Mesmo PNG em **Papel de parede** com transparência 0% (evita bordas claras fora da tela).

## 2. Dados e modelo

**Obter dados → Texto/CSV** para cada arquivo de `data/` (delimitador `;`).

Relacionamentos (**Exibição de modelo**), todos *muitos para um*, filtro único:

| De (muitos) | Para (um) |
|---|---|
| `fato_viagens[rota]` | `dim_rotas[rota]` |
| `fato_viagens[semana_inicio]` | `dim_semana[semana_inicio]` |
| `fato_viagens[veiculo]` | `dim_veiculos[veiculo]` |
| `fato_demanda[rota]` | `dim_rotas[rota]` |
| `fato_demanda[semana_inicio]` | `dim_semana[semana_inicio]` |

`fato_estoque` e `copilot_insights` ficam soltas. Confira se `semana_inicio` está como **Data** nas três tabelas.

Depois crie a tabela `_Medidas` (**Inserir dados → OK**) e cole as medidas de `dax/medidas.dax`
na ordem do arquivo. As medidas HTML dependem das anteriores.

## 3. Montagem — página **Command Center**

Use **Formatar → Geral → Propriedades → Tamanho e posição** para digitar os valores exatos (px).

| Painel | Visual | X | Y | Largura | Altura | Campos |
|---|---|---:|---:|---:|---:|---|
| `kpi_1` | HTML Content | 36 | 108 | 288 | 142 | medida `HTML KPI Estoque` |
| `kpi_2` | HTML Content | 348 | 108 | 288 | 142 | medida `HTML KPI Reposicao` |
| `kpi_3` | HTML Content | 660 | 108 | 288 | 142 | medida `HTML KPI Excesso` |
| `kpi_4` | HTML Content | 972 | 108 | 288 | 142 | medida `HTML KPI Acao` |
| `kpi_5` | HTML Content | 1284 | 108 | 288 | 142 | medida `HTML KPI Custo Transporte` |
| `kpi_6` | HTML Content | 1596 | 108 | 288 | 142 | medida `HTML KPI Utilizacao` |
| `rede_transporte` | Deneb · `deneb/rede_transporte.json` | 44 | 316 | 736 | 412 | dim_rotas: `rota`, `origem`, `origem_x`, `origem_y`, `destino_x`, `destino_y` (todas **Não resumir**) + medidas `Custo Planejado`, `Cor Rota`, `Rank Custo Rota` |
| `copilot_insight` | HTML Content | 820 | 316 | 554 | 412 | medida `HTML Copilot Insight` |
| `utilizacao_rotas` | HTML Content | 1414 | 316 | 462 | 412 | medida `HTML Medidores Rotas` |
| `custo_semanal` | Deneb · `deneb/custo_semanal.json` | 44 | 802 | 537 | 244 | dim_semana: `semana_label`, `semana_ordem` (Não resumir) + medida `Custo Mil` |
| `acoes_prioridade` | Deneb · `deneb/acoes_prioridade.json` | 621 | 802 | 537 | 244 | fato_estoque: `acao_recomendada`, `prioridade` + medida `SKUs` |
| `rotas_destaque` | Tabela nativa | 1198 | 802 | 678 | 244 | dim_rotas: `rota`, `origem`, `distancia_km` + medidas `Custo Planejado`, `Utilizacao` |

**Abas de navegação:** **Inserir → Botões → Navegador → Navegador de páginas**,
em X 760 · Y 30 · L 640 · A 48. O tema V6 já aplica o estilo (aba ativa em ciano).

**Status no cabeçalho** (opcional): caixa de texto em X 1420 · Y 38, com
"● API RENDER ONLINE · HORIZONTE 8 SEMANAS" (11 pt, `#94A3B8`).

### Detalhes por tipo de visual

**HTML Content**
- Arraste **apenas uma** medida HTML para *Values*.
- Se aparecer barra de rolagem, aumente 4–8 px a altura do visual. As medidas usam `height:100vh` para ocupar o visual inteiro.
- Se aparecer fundo branco, confira **Geral → Efeitos → Plano de fundo: desativado**. O tema já faz isso, mas visuais personalizados às vezes ignoram o tema.

**Deneb**
1. Adicione o visual e os campos indicados. Colunas numéricas: clique na seta do campo → **Não resumir**.
2. **Editar especificação → Criar → Vega-Lite → Vazio**.
3. Apague o conteúdo do editor *Specification* e cole o JSON do arquivo correspondente → **Aplicar**.
4. No editor *Config*, deixe `{}` (a configuração visual já está dentro da spec).

**Tabela `rotas_destaque`**
- **Filtros deste visual → `rota` → Tipo: N superior → Superior 6 por `Custo Planejado`.**
- Em `Utilizacao`: **Formatação condicional → Barras de dados**. Ou, para seguir o semáforo do mockup,
  use **Cor da fonte → Valor do campo → `Cor Utilizacao`**.
- Formato: `Custo Planejado` como moeda R$ sem casas; `Utilizacao` como % com 1 casa.

## 4. Páginas **Inventory** e **Transportation**

Os fundos (`bg_inventory.png`, `bg_transportation.png`) e as posições (`backgrounds/layout.json`)
já estão prontos. Os visuais dessas páginas entram na próxima etapa do kit. Até lá, dá para
reaproveitar os visuais do `.pbix` atual, encaixando-os nos painéis com a mesma regra:
**X + 12, Y + 44, largura − 24, altura − 56**. Cartões KPI: **X + 4, Y + 4, largura − 8, altura − 8**.

## 5. Publicar e verificar o "Publicar na web"

1. **Página Inicial → Publicar** → entre com a conta (o Power BI Service exige **conta corporativa ou de estudante**; e-mail pessoal não é aceito) → escolha *Meu workspace*.
2. Abra o relatório em **app.powerbi.com**.
3. **Arquivo → Inserir relatório → Publicar na Web (público)**.
   - Abriu a tela "Criar código de inserção": **liberado**. Gere e guarde o link/iframe para embutir no Streamlit.
   - Mensagem pedindo para contatar o administrador, ou opção desabilitada: o administrador precisa ativar em **Portal de administração → Configurações do locatário → Publicar na Web**.
4. O conteúdo de "Publicar na Web" fica **público**. Aqui não há problema, porque os dados do projeto são sintéticos.

**Plano B (sem Publicar na web):** exportar cada página em PNG (**Arquivo → Exportar → PDF** ou captura em 1920×1080)
e gravar um GIF navegando entre as páginas para o README.

## 6. Checklist final

- [ ] Fundo HUD aparece sem bordas brancas (papel de parede configurado).
- [ ] Todos os visuais estão sem fundo, sem borda e sem cabeçalho.
- [ ] KPIs batem com o mockup: R$ 34,59 Mi · R$ 3,28 Mi · R$ 11,65 Mi · R$ 14,93 Mi · R$ 99,6 mil · 76,6%.
- [ ] Mapa de rede com R012 e R011 em magenta.
- [ ] Navegador de páginas funcionando entre as 3 páginas.
