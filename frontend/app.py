import os

import requests
import streamlit as st


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

API_URL = f"{API_BASE_URL}/copilot"
HEALTH_URL = f"{API_BASE_URL}/health"

MENSAGEM_INICIAL = (
    "Olá! Sou o **AI Supply Chain Copilot**. "
    "Posso ajudar a analisar sua operação e identificar prioridades "
    "para tomada de decisão."
)


# ---------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Supply Chain Copilot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Identidade visual
# ---------------------------------------------------------

st.markdown(
    """
<style>
/* Fundo geral */
.stApp {
    background: linear-gradient(
        135deg,
        #111827 0%,
        #172033 55%,
        #111827 100%
    );
    color: #f1f5f9;
}

/* Área principal */
.block-container {
    max-width: 920px;
    padding-top: 3.5rem;
    padding-bottom: 7rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #131c2d;
    border-right: 1px solid rgba(148, 163, 184, 0.18);
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

/* Textos */
p, li {
    color: #e2e8f0;
}

h1, h2, h3, h4, h5 {
    color: #f8fafc !important;
}

[data-testid="stCaptionContainer"] {
    color: #a8b3c7;
}

/* Mensagens do chat */
[data-testid="stChatMessage"] {
    background: rgba(30, 41, 59, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 14px;
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.8rem;
}

/* Texto dentro das mensagens */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong {
    color: #f1f5f9 !important;
}

/* Campo de pergunta */
[data-testid="stChatInput"] {
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 14px;
}

/* Área interna de digitação */
[data-testid="stChatInput"] textarea {
    color: #111827 !important;
    background-color: #f8fafc !important;
}

/* Placeholder */
[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
    opacity: 1;
}

/* Botões */
.stButton > button {
    border-radius: 10px;
    border: 1px solid rgba(56, 189, 248, 0.35);
    background: rgba(30, 41, 59, 0.65);
    color: #f1f5f9;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    border-color: #38bdf8;
    color: #38bdf8;
    background: rgba(30, 41, 59, 0.95);
}

/* Status */
div[data-testid="stAlert"] {
    border-radius: 10px;
}

/* Linha divisória */
hr {
    border-color: rgba(148, 163, 184, 0.18);
}

/* Tabelas dentro das respostas do Copilot */
[data-testid="stChatMessage"] table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    background: rgba(15, 23, 42, 0.72);
    border-radius: 10px;
    overflow: hidden;
}

[data-testid="stChatMessage"] thead tr {
    background: rgba(30, 41, 59, 0.95);
}

[data-testid="stChatMessage"] th {
    color: #f8fafc !important;
    font-weight: 700;
    text-align: left;
    padding: 0.75rem 0.9rem;
    border: 1px solid rgba(148, 163, 184, 0.22);
}

[data-testid="stChatMessage"] td {
    color: #e2e8f0 !important;
    padding: 0.7rem 0.9rem;
    border: 1px solid rgba(148, 163, 184, 0.16);
}

[data-testid="stChatMessage"] tbody tr {
    background: rgba(15, 23, 42, 0.55);
}

[data-testid="stChatMessage"] tbody tr:nth-child(even) {
    background: rgba(30, 41, 59, 0.55);
}

[data-testid="stChatMessage"] tbody tr:hover {
    background: rgba(56, 189, 248, 0.10);
}

</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Integração com API
# ---------------------------------------------------------

def api_esta_online() -> bool:
    try:
        resposta = requests.get(
            HEALTH_URL,
            timeout=3,
        )
        return resposta.status_code == 200

    except requests.RequestException:
        return False


def consultar_copilot(pergunta: str) -> str:
    try:
        resposta_api = requests.post(
            API_URL,
            json={"pergunta": pergunta},
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


# ---------------------------------------------------------
# Estado da sessão
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": MENSAGEM_INICIAL,
        }
    ]

if "processando" not in st.session_state:
    st.session_state.processando = False

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.markdown("## ◈ AI Supply Chain")
    st.markdown("### Copilot")

    st.caption("Decision Intelligence for Operations")

    st.divider()

    if api_esta_online():
        st.success("● Sistema online")
    else:
        st.error("● Sistema offline")

    st.markdown("##### MÓDULOS")

    st.markdown("📦 **Inventory**")
    st.caption("Analytics & Decision Support")

    st.markdown("🤖 **AI Copilot**")
    st.caption("LLM-powered analysis")

    st.divider()

    if st.button(
        "＋ Nova conversa",
        use_container_width=True,
    ):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": MENSAGEM_INICIAL,
            }
        ]

        st.rerun()

    st.caption("AI Supply Chain Copilot · MVP")


# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------

st.markdown(
    '<div style="color:#38bdf8;'
    'font-size:0.80rem;'
    'font-weight:700;'
    'letter-spacing:0.14em;'
    'margin-bottom:0.5rem;">'
    'DECISION INTELLIGENCE'
    '</div>',
    unsafe_allow_html=True,
)

st.title("AI Supply Chain Copilot")

st.markdown(
    '<div style="color:#b8c4d6;'
    'font-size:1rem;'
    'margin-top:-0.5rem;'
    'margin-bottom:2rem;">'
    'Dados operacionais transformados em decisões.'
    '</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Histórico da conversa
# ---------------------------------------------------------

for message in st.session_state.messages:

    avatar = (
        "🤖"
        if message["role"] == "assistant"
        else "👤"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar,
    ):
        st.markdown(
            message["content"]
        )


# ---------------------------------------------------------
# Sugestões iniciais
# ---------------------------------------------------------

pergunta_sugerida = None


if len(st.session_state.messages) == 1:

    st.markdown("### Explore sua operação")

    coluna_1, coluna_2 = st.columns(2)

    with coluna_1:

        if st.button(
            "⚠️ Prioridades críticas",
            use_container_width=True,
        ):
            pergunta_sugerida = (
                "Quais produtos apresentam prioridade alta?"
            )

        if st.button(
            "📦 SKU mais crítico",
            use_container_width=True,
        ):
            pergunta_sugerida = (
                "Qual o SKU mais crítico?"
            )

    with coluna_2:

        if st.button(
            "🚨 Risco de ruptura",
            use_container_width=True,
        ):
            pergunta_sugerida = (
                "Quais produtos apresentam risco de ruptura?"
            )

        if st.button(
            "🏭 Performance de fornecedores",
            use_container_width=True,
        ):
            pergunta_sugerida = (
                "Quais fornecedores exigem maior atenção?"
            )


# ---------------------------------------------------------
# Campo de entrada
# ---------------------------------------------------------

pergunta_digitada = st.chat_input(
    "Pergunte sobre sua operação...",
    disabled=st.session_state.processando,
)

pergunta = (
    pergunta_digitada
    or pergunta_sugerida
)

MAX_PERGUNTA_CHARS = 1000

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



# ---------------------------------------------------------
# Consulta ao Copilot
# ---------------------------------------------------------

if pergunta:

    st.session_state.processando = True

    st.session_state.messages.append(
        {
            "role": "user",
            "content": pergunta,
        }
    )

    with st.chat_message(
        "user",
        avatar="👤",
    ):
        st.markdown(pergunta)

    with st.chat_message(
        "assistant",
        avatar="🤖",
    ):

        with st.spinner(
            "Analisando dados operacionais..."
        ):
            resposta = consultar_copilot(
                pergunta
            )

        st.markdown(resposta)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resposta,
        }
    )

MAX_MESSAGES = 20

if len(st.session_state.messages) > MAX_MESSAGES:
    st.session_state.messages = (
        [st.session_state.messages[0]]
        + st.session_state.messages[-(MAX_MESSAGES - 1):]
    )

    st.session_state.processando = False

    st.rerun()
    