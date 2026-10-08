"""Adaptieve leerapp 'Elke prompt is een potentieel datalek' — versie 3.

Routing en layout; zie design-document-v3.md voor het volledige ontwerp.
"""

import streamlit as st

import chat
import content
import intake
import slides
import verhaal

st.set_page_config(
    page_title="Elke prompt is een potentieel datalek",
    page_icon="🔒",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    .stApp { font-family: 'DM Sans', sans-serif; }

    .page-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.3rem;
        line-height: 1.3;
    }
    .page-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 1.2rem;
    }
    .context-box {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-top: 1rem;
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.8;
        border: 1px solid #e2e8f0;
    }
    .context-box p { margin: 0 0 0.6rem 0; }
    .context-box p:last-child { margin-bottom: 0; }
    .context-box ul, .context-box ol { margin: 0.4rem 0 0.8rem 0; padding-left: 1.3rem; }
    .context-box li { margin-bottom: 0.3rem; }
    .context-box strong { color: #1e293b; }
    .slide-counter {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 0.5rem;
    }

    /* Progressie-indicator */
    .progress-container { display: flex; gap: 4px; margin-bottom: 1rem; }
    .progress-dot { height: 4px; border-radius: 2px; flex: 1; transition: background 0.3s; }
    .progress-active { background: #818cf8; }
    .progress-inactive { background: #e2e8f0; }

    /* Staptype-badge */
    .stap-badge {
        display: inline-block;
        margin-left: 0.6rem;
        padding: 0.1rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #ede9fe;
        color: #6d28d9;
        border: 1px solid #ddd6fe;
    }
    .stap-badge-toepassing { background: #fef3c7; color: #92400e; border-color: #fde68a; }
    .stap-badge-quiz_verankering { background: #dcfce7; color: #166534; border-color: #bbf7d0; }

    /* Vaste slide-content (HTML-blokken uit de YAML) */
    .slide-content ul { color: #334155; line-height: 1.9; }
    .slide-highlight {
        background: #ede9fe;
        border: 1px solid #ddd6fe;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.8rem 0;
        color: #4c1d95;
        line-height: 1.7;
    }
    .slide-warning {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.8rem 0;
        color: #991b1b;
        line-height: 1.7;
    }
    .flow-steps {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    .flow-step {
        background: #ede9fe;
        border: 1px solid #c4b5fd;
        color: #4c1d95;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .flow-arrow { color: #8b5cf6; font-weight: 700; }
    .slide-columns { display: flex; gap: 1rem; flex-wrap: wrap; margin: 0.8rem 0; }
    .slide-columns > div { flex: 1; min-width: 230px; border-radius: 12px; padding: 1rem 1.5rem; }
    .slide-col-red { background: #fef2f2; border: 1px solid #fecaca; color: #7f1d1d; }
    .slide-col-green { background: #f0fdf4; border: 1px solid #bbf7d0; color: #14532d; }
    .slide-col-red h4, .slide-col-green h4 { margin: 0 0 0.5rem 0; }
    .slide-col-red ul, .slide-col-green ul { margin: 0; padding-left: 1.2rem; line-height: 1.8; }

    /* Verhaaltekst (containers met key verhaal_<stap> en verhaal_einde) */
    [class*="st-key-verhaal_"] {
        border-left: 4px solid #818cf8;
        padding: 0.4rem 0 0.4rem 1.2rem;
        margin: 1rem 0 1.2rem 0;
        font-size: 1.08rem;
        line-height: 1.85;
        color: #1e293b;
    }
    [class*="st-key-verhaal_"] p { margin: 0 0 0.8rem 0; font-size: inherit; line-height: inherit; }
    [class*="st-key-verhaal_"] p:last-child { margin-bottom: 0; }

    .chat-titel { font-weight: 700; color: #1e293b; font-size: 1.1rem; margin-bottom: 0.2rem; }
</style>
""", unsafe_allow_html=True)


try:
    MODULE = content.load_module()
    content.valideer_prompts()
except ValueError as fout:
    st.error(f"Contentfout bij het opstarten: {fout}")
    st.stop()

# --- Session state ---
st.session_state.setdefault("pagina", "intake")
st.session_state.setdefault("profiel", None)
st.session_state.setdefault("stap_idx", 0)

# --- Routing ---
if st.session_state.profiel is None or st.session_state.pagina == "intake":
    intake.render_intake()
    st.stop()

profiel = st.session_state.profiel

# --- Moduleweergave: slides links, chat-agent rechts ---
if st.button("Profiel aanpassen"):
    st.session_state.pagina = "intake"
    st.rerun()

# Eén LLM-call per profiel (gecachet); bij de eerste weergave met een spinner.
velden = verhaal.velden(profiel)
stappen = verhaal.vul_stappen(MODULE["stappen"], velden)
huidige_stap = stappen[st.session_state.stap_idx]

kolom_slide, kolom_chat = st.columns([2, 1], gap="large")
with kolom_slide:
    slides.render_stap(stappen, profiel, velden)
with kolom_chat:
    chat.render_chat(huidige_stap, stappen, profiel, velden)
