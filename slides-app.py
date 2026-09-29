"""Adaptieve leerapp 'De gevaren van het delen van data met AI-tools' — versie 2.

Routing en layout; zie design-document.md voor het volledige ontwerp.
"""

import streamlit as st

import chat
import content
import intake
import slides

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

    /* Modulekaarten op het overzicht */
    .module-kaart {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.4rem;
        min-height: 7.5rem;
    }
    .module-kaart h4 { margin: 0 0 0.4rem 0; color: #1e293b; }
    .module-kaart p { margin: 0; color: #64748b; font-size: 0.88rem; line-height: 1.6; }

    .chat-titel { font-weight: 700; color: #1e293b; font-size: 1.1rem; margin-bottom: 0.2rem; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def laad_content():
    return content.load_modules(), content.load_sectoren()


try:
    MODULES, SECTOREN = laad_content()
except ValueError as fout:
    st.error(f"Contentfout bij het opstarten: {fout}")
    st.stop()

# --- Session state ---
st.session_state.setdefault("pagina", "intake")
st.session_state.setdefault("profiel", None)
st.session_state.setdefault("module_nr", None)
st.session_state.setdefault("stap_idx", 0)

# --- Routing ---
if st.session_state.profiel is None or st.session_state.pagina == "intake":
    intake.render_intake()
    st.stop()

profiel = st.session_state.profiel

# --- Moduleoverzicht ---
if st.session_state.pagina == "overzicht":
    naam = f", {profiel['naam']}" if profiel.get("naam") else ""
    st.markdown(
        f"""
        <div class="context-box" style="text-align: center;">
            <h2 style="margin: 0 0 0.5rem 0; color: #1e293b;">Welkom{naam} 👋</h2>
            <p style="color: #64748b; margin: 0;">Vijf modules over de gevaren van het delen van
            data met AI-tools. Volg ze op volgorde of kies wat jou interesseert.
            Kernboodschap: <strong>elke prompt is een potentieel datalek.</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    kolommen = st.columns(len(content.MODULES))
    for kolom, (nummer, meta) in zip(kolommen, content.MODULES.items()):
        with kolom:
            st.markdown(
                f"""
                <div class="module-kaart">
                    <h4>Module {nummer}</h4>
                    <p><strong>{meta["titel"]}</strong></p>
                    <p style="margin-top: 0.4rem;">{meta["modeldoel"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Start module", key=f"start_{nummer}", width="stretch"):
                st.session_state.module_nr = nummer
                st.session_state.stap_idx = 0
                st.session_state.pagina = "module"
                st.rerun()

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
    if st.button("Profiel aanpassen"):
        st.session_state.pagina = "intake"
        st.rerun()
    st.stop()

# --- Moduleweergave: slides links, chat-agent rechts ---
if st.button("< Terug naar overzicht"):
    st.session_state.pagina = "overzicht"
    st.rerun()

stappen = MODULES[st.session_state.module_nr]
huidige_stap = stappen[st.session_state.stap_idx]

kolom_slide, kolom_chat = st.columns([2, 1], gap="large")
with kolom_slide:
    slides.render_stap(stappen, profiel, SECTOREN)
with kolom_chat:
    chat.render_chat(huidige_stap, stappen, profiel, SECTOREN)
