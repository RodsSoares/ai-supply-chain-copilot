import os
from typing import Any

import requests
import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# Configuração
# =========================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

API_URL = f"{API_BASE_URL}/copilot"
HEALTH_URL = f"{API_BASE_URL}/health"
DASHBOARD_URL = f"{API_BASE_URL}/dashboard"

MAX_PERGUNTA_CHARS = 1000
MAX_MESSAGES = 20

DOMAIN_CONFIG = {
    "inventory": {
        "label": "Inventory",
        "eyebrow": "INVENTORY INTELLIGENCE",
        "title": "Inventory Decision Intelligence",
        "subtitle": (
            "Transforme posição de estoque, cobertura, risco e valor "
            "em prioridades claras para decisão."
        ),
        "context": "Inventory context active",
        "tags": ["Stock", "Coverage", "Risk", "Prioritization"],
        "placeholder": "Pergunte sobre estoque, SKUs, cobertura, risco e fornecedores...",
        "suggestions": [
            (
                "⚠",
                "Prioridades críticas",
                "Identifique os itens que exigem atenção primeiro.",
                "Quais produtos apresentam prioridade alta?",
            ),
            (
                "△",
                "Risco de ruptura",
                "Encontre produtos com maior exposição a stockout.",
                "Quais produtos apresentam risco de ruptura?",
            ),
            (
                "▣",
                "SKU mais crítico",
                "Vá direto ao item de maior criticidade operacional.",
                "Qual o SKU mais crítico?",
            ),
            (
                "◎",
                "Fornecedores",
                "Investigue onde a operação exige maior atenção.",
                "Quais fornecedores exigem maior atenção?",
            ),
        ],
    },
    "transportation": {
        "label": "Transportation",
        "eyebrow": "TRANSPORTATION INTELLIGENCE",
        "title": "Transportation Decision Intelligence",
        "subtitle": (
            "Entenda a rede, explique mudanças operacionais e acompanhe "
            "capacidade, utilização e custo."
        ),
        "context": "Transportation context active",
        "tags": ["Network", "Capacity", "Utilization", "Cost"],
        "placeholder": "Pergunte sobre rotas, capacidade, utilização, viagens e custos...",
        "suggestions": [
            (
                "⌁",
                "Visão executiva da rede",
                "Leia o comportamento consolidado da operação.",
                "Como está a operação de transporte da rede?",
            ),
            (
                "↗",
                "Tendência recente",
                "Acompanhe a evolução recente de uma rota.",
                "Qual foi a tendência recente da rota R005?",
            ),
            (
                "⇄",
                "Mudanças operacionais",
                "Compare veículo, capacidade, viagens e custo.",
                "O que mudou na operação da rota R001 entre as semanas?",
            ),
            (
                "◇",
                "Explicar custo",
                "Investigue por que o custo por peça se alterou.",
                (
                    "Por que o custo por peça da rota R001 aumentou "
                    "na semana de 2026-10-12 em relação à semana anterior?"
                ),
            ),
        ],
    },
}


def mensagem_inicial(dominio: str) -> str:
    nome = DOMAIN_CONFIG[dominio]["label"]
    return (
        f"**{nome} context ready.** "
        "Selecione uma análise sugerida ou faça uma pergunta sobre sua operação."
    )


# =========================================================
# Página
# =========================================================

st.set_page_config(
    page_title="AI Supply Chain Copilot",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# Design System
# =========================================================

st.markdown(
    """
<style>
:root {
    --bg-0: #020914;
    --bg-1: #06111f;
    --bg-2: #0a1728;
    --panel: rgba(8, 24, 42, 0.78);
    --panel-strong: rgba(10, 29, 49, 0.94);
    --line: rgba(47, 184, 255, 0.22);
    --line-strong: rgba(47, 184, 255, 0.55);
    --cyan: #20c8ff;
    --blue: #2f7dff;
    --white: #f5f9ff;
    --text: #d8e4f2;
    --muted: #8294aa;
    --green: #26d99a;
    --amber: #ffc857;
    --orange: #ff8b3d;
    --red: #ff5c6c;
    --violet: #9b7cff;
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
                 "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 82% 4%, rgba(20, 105, 190, 0.18), transparent 27rem),
        radial-gradient(circle at 48% 110%, rgba(0, 178, 255, 0.10), transparent 34rem),
        linear-gradient(145deg, var(--bg-0) 0%, var(--bg-1) 48%, #071423 100%);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: rgba(4, 15, 28, 0.98) !important;
    border-bottom: 1px solid rgba(47, 184, 255, 0.10);
}

[data-testid="stToolbar"] {
    background: transparent !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stAppViewContainer"] > .main {
    background-image:
        linear-gradient(rgba(31, 146, 210, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(31, 146, 210, 0.025) 1px, transparent 1px);
    background-size: 48px 48px;
}

.block-container {
    max-width: 1380px;
    padding-top: 2.0rem;
    padding-bottom: 8rem;
    padding-left: 2.2rem;
    padding-right: 2.2rem;
}

section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(4, 15, 28, 0.99), rgba(5, 18, 32, 0.98));
    border-right: 1px solid rgba(47, 184, 255, 0.16);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.25rem;
}

section[data-testid="stSidebar"] * {
    color: var(--text);
}

h1, h2, h3, h4, h5, h6 {
    color: var(--white) !important;
    letter-spacing: -0.02em;
}

p, li {
    color: var(--text);
}

[data-testid="stCaptionContainer"] {
    color: var(--muted);
}

hr {
    border-color: rgba(47, 184, 255, 0.13);
}

/* Brand */
.rs-brand {
    padding: 0.35rem 0 0.75rem 0;
}
.rs-brand-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    margin-right: 10px;
    border: 1px solid rgba(32, 200, 255, 0.55);
    border-radius: 9px;
    background: linear-gradient(145deg, rgba(47,125,255,.22), rgba(32,200,255,.06));
    box-shadow: 0 0 22px rgba(32,200,255,.10);
    color: #8de7ff;
    font-weight: 800;
}
.rs-brand-name {
    font-size: 1.02rem;
    font-weight: 800;
    color: var(--white);
}
.rs-brand-sub {
    margin-top: .45rem;
    color: var(--muted);
    font-size: .76rem;
    letter-spacing: .04em;
}

/* Sidebar labels */
.side-label {
    margin-top: 1.0rem;
    margin-bottom: .35rem;
    color: #6fa7c8;
    font-size: .66rem;
    font-weight: 800;
    letter-spacing: .16em;
}
.system-card {
    border: 1px solid rgba(47,184,255,.15);
    border-radius: 10px;
    padding: .72rem .8rem;
    background: rgba(8,25,43,.55);
    margin: .35rem 0 .75rem 0;
}
.system-line {
    display:flex;
    align-items:center;
    gap:.5rem;
    font-size:.78rem;
}
.dot-online {
    width:8px;
    height:8px;
    border-radius:50%;
    background:var(--green);
    box-shadow:0 0 12px rgba(38,217,154,.65);
}
.dot-offline {
    width:8px;
    height:8px;
    border-radius:50%;
    background:var(--red);
    box-shadow:0 0 12px rgba(255,92,108,.55);
}
.side-foot {
    color:#60758d;
    font-size:.66rem;
    letter-spacing:.08em;
    line-height:1.6;
    margin-top:1rem;
}

/* Radio = domain navigation */
section[data-testid="stSidebar"] [role="radiogroup"] {
    gap: .45rem;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(8, 25, 43, 0.58);
    border: 1px solid rgba(47, 184, 255, 0.12);
    border-radius: 10px;
    padding: .58rem .65rem;
    transition: .18s ease;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    border-color: rgba(32, 200, 255, 0.42);
    background: rgba(10, 34, 57, 0.82);
}

/* Top hero */
.hero {
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(47,184,255,.20);
    border-radius: 18px;
    padding: 1.65rem 1.8rem 1.55rem 1.8rem;
    background:
        radial-gradient(circle at 90% 15%, rgba(31, 155, 255, .16), transparent 22rem),
        linear-gradient(135deg, rgba(7,24,42,.92), rgba(6,18,32,.74));
    box-shadow: inset 0 1px 0 rgba(255,255,255,.025);
    margin-bottom: 1.05rem;
}
.hero:after {
    content:"";
    position:absolute;
    width:280px;
    height:280px;
    border:1px solid rgba(32,200,255,.08);
    border-radius:50%;
    right:-120px;
    top:-145px;
}
.eyebrow {
    color: var(--cyan);
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .18em;
    margin-bottom: .6rem;
}
.hero-title {
    color: var(--white);
    font-size: clamp(1.65rem, 3vw, 2.55rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -.035em;
}
.hero-title .accent {
    background: linear-gradient(90deg, #53d8ff, #278dff);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.hero-subtitle {
    max-width: 820px;
    margin-top: .7rem;
    color: #a9bbcd;
    font-size: .96rem;
    line-height: 1.55;
}
.tag-row {
    display:flex;
    gap:.45rem;
    flex-wrap:wrap;
    margin-top:1rem;
}
.tag {
    border:1px solid rgba(32,200,255,.17);
    background:rgba(7,30,49,.72);
    color:#91cde9;
    border-radius:999px;
    padding:.27rem .58rem;
    font-size:.68rem;
    letter-spacing:.03em;
}


/* Persistent domain identity */
.stElementContainer:has(.sticky-domain-bar) {
    position: sticky;
    top: 3.65rem;
    z-index: 900;
    margin-top: -0.15rem;
    margin-bottom: 0.8rem;
}

.sticky-domain-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    min-height: 46px;
    padding: .55rem .85rem;
    border: 1px solid rgba(47,184,255,.24);
    border-radius: 12px;
    background:
        linear-gradient(90deg, rgba(5,20,35,.97), rgba(7,30,49,.95));
    box-shadow:
        0 12px 28px rgba(0,0,0,.24),
        inset 0 1px 0 rgba(255,255,255,.025);
    backdrop-filter: blur(14px);
}

.sticky-domain-name {
    color: var(--white);
    font-size: .86rem;
    font-weight: 800;
    white-space: nowrap;
}

.sticky-domain-name .accent {
    color: var(--cyan);
}

.sticky-domain-tags {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: .35rem;
    flex-wrap: wrap;
}

.sticky-domain-tag {
    border: 1px solid rgba(32,200,255,.16);
    border-radius: 999px;
    padding: .18rem .46rem;
    background: rgba(7,30,49,.72);
    color: #91cde9;
    font-size: .62rem;
    letter-spacing: .025em;
}

/* Section titles */
.section-kicker {
    color: var(--cyan);
    font-size:.64rem;
    font-weight:800;
    letter-spacing:.17em;
    margin-top:.55rem;
}
.section-title {
    color:var(--white);
    font-size:1.18rem;
    font-weight:760;
    margin:.12rem 0 .65rem 0;
}
.section-copy {
    color:var(--muted);
    font-size:.82rem;
    margin-top:-.35rem;
    margin-bottom:.75rem;
}

/* Native metric */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(8,27,47,.88), rgba(7,20,35,.78));
    border: 1px solid rgba(47,184,255,.16);
    border-radius: 13px;
    padding: .8rem .9rem;
    min-height: 112px;
}
[data-testid="stMetricLabel"] {
    color:#88a4bb !important;
}
[data-testid="stMetricValue"] {
    color:var(--white) !important;
    font-weight:760;
    font-size: clamp(1.35rem, 2.1vw, 2.05rem) !important;
    line-height: 1.08 !important;
    white-space: nowrap !important;
    overflow: visible !important;
}
[data-testid="stMetricValue"] > div {
    overflow: visible !important;
    text-overflow: clip !important;
}
[data-testid="stMetricDelta"] {
    font-size:.72rem;
}

/* Buttons / capability cards */
.stButton > button {
    min-height: 3.15rem;
    border-radius: 11px;
    border: 1px solid rgba(47,184,255,.22);
    background: linear-gradient(145deg, rgba(8,29,49,.90), rgba(7,22,39,.78));
    color: #dff5ff;
    font-weight: 650;
    transition: all .18s ease;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.018);
}
.stButton > button:hover {
    border-color: rgba(32,200,255,.70);
    color: #ffffff;
    background: linear-gradient(145deg, rgba(9,39,65,.98), rgba(7,27,47,.95));
    box-shadow: 0 0 24px rgba(32,200,255,.07);
    transform: translateY(-1px);
}
.stButton > button:focus {
    box-shadow: 0 0 0 1px rgba(32,200,255,.45);
}

/* Copilot panel labels */
.copilot-head {
    margin-top:1.35rem;
    border-top:1px solid rgba(47,184,255,.13);
    padding-top:1.25rem;
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:1rem;
}
.copilot-title {
    color:var(--white);
    font-size:1.15rem;
    font-weight:800;
}
.context-pill {
    display:inline-flex;
    align-items:center;
    gap:.42rem;
    border:1px solid rgba(155,124,255,.28);
    background:rgba(77,54,130,.14);
    color:#cbbcff;
    border-radius:999px;
    padding:.3rem .58rem;
    font-size:.68rem;
}
.context-dot {
    width:7px;
    height:7px;
    border-radius:50%;
    background:var(--violet);
    box-shadow:0 0 10px rgba(155,124,255,.7);
}

/* Chat */
[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, rgba(8,26,45,.84), rgba(7,20,35,.76));
    border: 1px solid rgba(47,184,255,.14);
    border-radius: 13px;
    padding: .72rem .9rem;
    margin-bottom: .7rem;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong {
    color: #eaf3fb !important;
}
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {
    color:#ffffff !important;
}
[data-testid="stChatMessage"] table {
    width:100%;
    border-collapse:collapse;
    margin:.8rem 0;
    background:rgba(3,14,25,.55);
}
[data-testid="stChatMessage"] th {
    color:#bdeeff !important;
    background:rgba(11,43,70,.88);
    border:1px solid rgba(47,184,255,.20);
    padding:.62rem .7rem;
}
[data-testid="stChatMessage"] td {
    color:#dce9f4 !important;
    border:1px solid rgba(47,184,255,.12);
    padding:.58rem .7rem;
}

/* Chat composer / fixed bottom area */
[data-testid="stBottomBlockContainer"] {
    background:
        linear-gradient(
            180deg,
            rgba(4,15,28,0.00) 0%,
            rgba(4,15,28,0.94) 24%,
            rgba(4,15,28,0.99) 100%
        ) !important;
    border-top: 1px solid rgba(47,184,255,.10) !important;
    padding-top: .85rem !important;
    padding-bottom: .85rem !important;
}

[data-testid="stBottomBlockContainer"] > div {
    background: transparent !important;
}

[data-testid="stChatInput"] {
    border:1px solid rgba(32,200,255,.34) !important;
    border-radius:14px !important;
    background:rgba(6,22,38,.98) !important;
    box-shadow:
        0 0 30px rgba(32,200,255,.06),
        inset 0 1px 0 rgba(255,255,255,.02) !important;
}

[data-testid="stChatInput"] textarea {
    color:#eef8ff !important;
    background:transparent !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color:#7189a1 !important;
    opacity:1;
}

[data-testid="stChatInput"] button {
    color:#8edfff !important;
}

/* Prevent accidental bright inline-code/math fragments in Copilot answers */
[data-testid="stChatMessage"] code {
    color:#9fe8ff !important;
    background:rgba(13,44,69,.78) !important;
    border:1px solid rgba(47,184,255,.12);
    border-radius:5px;
    padding:.08rem .28rem;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius:11px;
    background:rgba(8,25,43,.90);
}

/* Footer */
.product-footer {
    margin-top:2.0rem;
    padding-top:1rem;
    border-top:1px solid rgba(47,184,255,.12);
    display:flex;
    justify-content:space-between;
    gap:1rem;
    color:#60758d;
    font-size:.68rem;
    letter-spacing:.05em;
}

/* Hide Streamlit chrome where possible */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}

@media (max-width: 900px) {
    .block-container {
        padding-left:1rem;
        padding-right:1rem;
    }
    .hero {
        padding:1.25rem;
    }
    .sticky-domain-bar {
        align-items:flex-start;
        flex-direction:column;
    }
    .sticky-domain-tags {
        justify-content:flex-start;
    }
    .product-footer {
        flex-direction:column;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# API
# =========================================================

@st.cache_data(ttl=10, show_spinner=False)
def api_esta_online() -> bool:
    try:
        resposta = requests.get(HEALTH_URL, timeout=3)
        return resposta.status_code == 200
    except requests.RequestException:
        return False


@st.cache_data(ttl=30, show_spinner=False)
def obter_dashboard_inventory() -> dict[str, Any] | None:
    try:
        resposta = requests.get(DASHBOARD_URL, timeout=5)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados if isinstance(dados, dict) else None
    except (requests.RequestException, ValueError):
        return None


def consultar_copilot(pergunta: str, dominio: str) -> str:
    try:
        resposta_api = requests.post(
            API_URL,
            json={
                "pergunta": pergunta,
                "dominio": dominio,
            },
            timeout=60,
        )
        resposta_api.raise_for_status()

        try:
            dados = resposta_api.json()
        except requests.exceptions.JSONDecodeError:
            return (
                "O Copilot recebeu uma resposta inválida da API.\n\n"
                "A resposta não pôde ser interpretada como JSON."
            )

        if not isinstance(dados, dict):
            return (
                "O Copilot recebeu uma resposta inesperada da API.\n\n"
                "Tente novamente em alguns instantes."
            )

        resposta = dados.get("resposta")
        if not isinstance(resposta, str) or not resposta.strip():
            return (
                "A API respondeu corretamente, mas não retornou "
                "o conteúdo esperado do Copilot."
            )

        return resposta.strip()

    except requests.Timeout:
        return (
            "A análise excedeu o tempo limite de resposta.\n\n"
            "Tente novamente em alguns instantes."
        )
    except requests.ConnectionError:
        return (
            "Não foi possível conectar ao backend do Copilot.\n\n"
            "Verifique se a API está disponível."
        )
    except requests.HTTPError as erro:
        status_code = erro.response.status_code if erro.response else None

        if status_code == 429:
            return (
                "O limite temporário de utilização foi atingido.\n\n"
                "Tente novamente em alguns instantes."
            )
        if status_code and 500 <= status_code < 600:
            detalhe = ""
            try:
                corpo = erro.response.json()
                if isinstance(corpo, dict):
                    detalhe = str(corpo.get("detail", "")).strip()
            except ValueError:
                pass

            if detalhe:
                return detalhe

            return (
                "O serviço está temporariamente indisponível.\n\n"
                "Tente novamente em alguns instantes."
            )

        return (
            "Não foi possível processar a solicitação.\n\n"
            "Revise a pergunta e tente novamente."
        )
    except requests.RequestException:
        return (
            "Não foi possível consultar o Copilot neste momento.\n\n"
            "Tente novamente em alguns instantes."
        )


# =========================================================
# Helpers de apresentação
# =========================================================

def formatar_inteiro(valor: Any) -> str:
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "—"


def preparar_markdown_copilot(texto: str) -> str:
    """
    Protege valores monetários em R$ contra interpretação acidental
    como delimitadores matemáticos do Markdown.
    """
    return texto.replace("$", r"\$")


def formatar_brl(valor: Any) -> str:
    """
    Formata valores monetários para cards executivos sem truncar a UI.
    Mantém precisão suficiente para leitura operacional.
    """
    try:
        numero = float(valor)

        if abs(numero) >= 1_000_000:
            return f"R$ {numero / 1_000_000:.2f} mi".replace(".", ",")

        if abs(numero) >= 1_000:
            return f"R$ {numero / 1_000:.1f} mil".replace(".", ",")

        return f"R$ {numero:.2f}".replace(".", ",")

    except (TypeError, ValueError):
        return "—"


def solicitar_scroll_topo() -> None:
    """Marca que o próximo rerun deve iniciar no topo."""
    st.session_state.scroll_to_top = True


def executar_scroll_topo_pendente() -> None:
    """
    Faz scroll ao topo somente após navegação explícita.
    Não interfere nos reruns normais provocados pelo chat.
    """
    if not st.session_state.pop("scroll_to_top", False):
        return

    components.html(
        """
        <script>
        const w = window.parent;
        const d = w.document;

        function goTop() {
            w.scrollTo(0, 0);

            [
                d.querySelector('[data-testid="stAppViewContainer"]'),
                d.querySelector('[data-testid="stMain"]'),
                d.querySelector('.main')
            ].forEach((el) => {
                if (el) el.scrollTop = 0;
            });
        }

        requestAnimationFrame(() => {
            goTop();
            setTimeout(goTop, 60);
            setTimeout(goTop, 180);
        });
        </script>
        """,
        height=0,
        width=0,
    )


def resetar_conversa(dominio: str) -> None:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": mensagem_inicial(dominio),
        }
    ]
    st.session_state.processando = False


def renderizar_metricas_inventory() -> None:
    dados = obter_dashboard_inventory()

    if not dados:
        st.caption(
            "KPIs executivos indisponíveis no momento. "
            "O Copilot continua disponível para análise."
        )
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "SKUs",
            formatar_inteiro(dados.get("total_skus")),
            help="Quantidade de SKUs distintos no dataset analítico.",
        )
    with col2:
        st.metric(
            "Valor em estoque",
            formatar_brl(dados.get("valor_total_estoque")),
            help="Valor total de estoque consolidado.",
        )
    with col3:
        st.metric(
            "Reposição",
            formatar_brl(dados.get("valor_total_reposicao")),
            help="Valor total associado à necessidade de reposição.",
        )
    with col4:
        st.metric(
            "Excesso",
            formatar_brl(dados.get("valor_total_excesso")),
            help="Valor total associado a excesso de estoque.",
        )


def renderizar_escopo_transportation() -> None:
    """
    Transportation ainda não possui endpoint REST dedicado a KPIs executivos.
    Em vez de inventar números no frontend, mostramos o escopo analítico real.
    """
    col1, col2, col3, col4 = st.columns(4)

    cards = [
        ("NETWORK", "Rede", "Visão consolidada"),
        ("CAPACITY", "Capacidade", "Oferta e utilização"),
        ("COST", "Custos", "Custo total e unitário"),
        ("TREND", "Evolução", "Comparação semanal"),
    ]

    for coluna, (rotulo, titulo, descricao) in zip(
        [col1, col2, col3, col4],
        cards,
    ):
        with coluna:
            st.markdown(
                f"""
                <div style="
                    min-height:112px;
                    border:1px solid rgba(47,184,255,.16);
                    border-radius:13px;
                    padding:.82rem .9rem;
                    background:linear-gradient(
                        145deg,
                        rgba(8,27,47,.88),
                        rgba(7,20,35,.78)
                    );
                ">
                    <div style="
                        color:#20c8ff;
                        font-size:.61rem;
                        font-weight:800;
                        letter-spacing:.14em;
                    ">{rotulo}</div>
                    <div style="
                        color:#f5f9ff;
                        font-size:1.05rem;
                        font-weight:760;
                        margin-top:.28rem;
                    ">{titulo}</div>
                    <div style="
                        color:#8294aa;
                        font-size:.72rem;
                        margin-top:.30rem;
                    ">{descricao}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# Estado da sessão
# =========================================================

if "dominio" not in st.session_state:
    st.session_state.dominio = "inventory"

if "messages" not in st.session_state:
    resetar_conversa(st.session_state.dominio)

if "processando" not in st.session_state:
    st.session_state.processando = False

if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False


# =========================================================
# Sidebar
# =========================================================

online = api_esta_online()

with st.sidebar:
    st.markdown(
        """
        <div class="rs-brand">
            <div>
                <span class="rs-brand-mark">RS</span>
                <span class="rs-brand-name">AI Supply Chain Copilot</span>
            </div>
            <div class="rs-brand-sub">
                Decision Intelligence for Operations
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">DOMAINS</div>', unsafe_allow_html=True)

    rotulo_dominio = st.radio(
        "Domínio operacional",
        options=["Inventory", "Transportation"],
        index=0 if st.session_state.dominio == "inventory" else 1,
        label_visibility="collapsed",
    )

    dominio_selecionado = (
        "inventory"
        if rotulo_dominio == "Inventory"
        else "transportation"
    )

    if dominio_selecionado != st.session_state.dominio:
        st.session_state.dominio = dominio_selecionado
        resetar_conversa(dominio_selecionado)
        solicitar_scroll_topo()
        st.rerun()

    st.markdown(
        '<div class="side-label">INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**◉ AI Copilot**")
    st.caption("Explain • Analyze • Recommend")

    st.markdown(
        '<div class="side-label">SYSTEM</div>',
        unsafe_allow_html=True,
    )

    status_class = "dot-online" if online else "dot-offline"
    status_text = "API online" if online else "API offline"

    st.markdown(
        f"""
        <div class="system-card">
            <div class="system-line">
                <span class="{status_class}"></span>
                <span>{status_text}</span>
            </div>
            <div style="
                color:#60758d;
                font-size:.68rem;
                margin-top:.42rem;
            ">
                Domain routing: deterministic
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("＋ Nova conversa", use_container_width=True):
        resetar_conversa(st.session_state.dominio)
        solicitar_scroll_topo()
        st.rerun()

    st.markdown(
        """
        <div class="side-foot">
            DATA → ANALYTICS → DECISION → AI<br>
            Designed & engineered by Rodrigo Soares
        </div>
        """,
        unsafe_allow_html=True,
    )


executar_scroll_topo_pendente()


# =========================================================
# Hero do domínio
# =========================================================

config = DOMAIN_CONFIG[st.session_state.dominio]
tags_html = "".join(
    f'<span class="tag">{tag}</span>'
    for tag in config["tags"]
)

st.markdown(
    f"""
    <div class="hero">
        <div class="eyebrow">{config["eyebrow"]}</div>
        <div class="hero-title">
            {config["title"].replace("Decision Intelligence", '<span class="accent">Decision Intelligence</span>')}
        </div>
        <div class="hero-subtitle">{config["subtitle"]}</div>
        <div class="tag-row">{tags_html}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

sticky_tags_html = "".join(
    f'<span class="sticky-domain-tag">{tag}</span>'
    for tag in config["tags"]
)

st.markdown(
    f"""
    <div class="sticky-domain-bar">
        <div class="sticky-domain-name">
            <span class="accent">{config["label"]}</span> · Decision Intelligence
        </div>
        <div class="sticky-domain-tags">{sticky_tags_html}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Operational Intelligence
# =========================================================

st.markdown(
    '<div class="section-kicker">OPERATIONAL INTELLIGENCE</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-title">Sua operação em contexto</div>',
    unsafe_allow_html=True,
)

if st.session_state.dominio == "inventory":
    renderizar_metricas_inventory()
else:
    renderizar_escopo_transportation()


# =========================================================
# Capabilities / Suggested questions
# =========================================================

st.markdown(
    '<div class="section-kicker" style="margin-top:1.25rem;">EXPLORE</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-title">Explore sua operação</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-copy">'
    'Atalhos para perguntas que o domínio já está preparado para analisar.'
    '</div>',
    unsafe_allow_html=True,
)

pergunta_sugerida = None
col1, col2 = st.columns(2)

for indice, (icone, titulo, descricao, pergunta) in enumerate(
    config["suggestions"]
):
    coluna = col1 if indice % 2 == 0 else col2
    with coluna:
        if st.button(
            f"{icone}  {titulo}  ·  {descricao}",
            key=f"suggestion_{st.session_state.dominio}_{indice}",
            use_container_width=True,
            disabled=st.session_state.processando,
        ):
            pergunta_sugerida = pergunta


# =========================================================
# AI Copilot
# =========================================================

st.markdown(
    f"""
    <div class="copilot-head">
        <div>
            <div class="section-kicker">DECISION SUPPORT</div>
            <div class="copilot-title">AI Copilot</div>
        </div>
        <div class="context-pill">
            <span class="context-dot"></span>
            {config["context"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "O Copilot interpreta contexto analítico determinístico e explica "
    "o que os dados suportam — sem inventar causas ausentes."
)

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(preparar_markdown_copilot(message["content"]))


# =========================================================
# Input
# =========================================================

pergunta_digitada = st.chat_input(
    config["placeholder"],
    disabled=st.session_state.processando or not online,
)

pergunta = pergunta_digitada or pergunta_sugerida

if pergunta:
    pergunta = pergunta.strip()

    if not pergunta:
        st.warning("Digite uma pergunta válida.")
        pergunta = None
    elif len(pergunta) > MAX_PERGUNTA_CHARS:
        st.warning(
            f"A pergunta é muito longa. "
            f"Use no máximo {MAX_PERGUNTA_CHARS} caracteres."
        )
        pergunta = None


# =========================================================
# Consulta
# =========================================================

if pergunta:
    st.session_state.processando = True

    st.session_state.messages.append(
        {
            "role": "user",
            "content": pergunta,
        }
    )

    with st.chat_message("user", avatar="👤"):
        st.markdown(pergunta)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner(
            "Lendo contexto operacional e preparando a análise..."
        ):
            resposta = consultar_copilot(
                pergunta,
                dominio=st.session_state.dominio,
            )
        st.markdown(preparar_markdown_copilot(resposta))

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resposta,
        }
    )

    if len(st.session_state.messages) > MAX_MESSAGES:
        st.session_state.messages = (
            [st.session_state.messages[0]]
            + st.session_state.messages[-(MAX_MESSAGES - 1):]
        )

    st.session_state.processando = False
    st.rerun()


# =========================================================
# Footer
# =========================================================

st.markdown(
    """
    <div class="product-footer">
        <span>AI SUPPLY CHAIN COPILOT · DECISION INTELLIGENCE</span>
        <span>RODRIGO SOARES · AI SOLUTIONS & AUTOMATION</span>
    </div>
    """,
    unsafe_allow_html=True,
)
