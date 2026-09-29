"""Chat-agent: vast paneel naast de slides, reactief op elke stap en leidend bij toepassing."""

import streamlit as st

import content
import llm

MAX_BEURTEN_PER_MODULE = 12
MAX_INVOER_TEKENS = 500

FALLBACK = (
    "De AI-coach is even niet beschikbaar. Je kan gewoon verder met de training "
    "en het later opnieuw proberen."
)


def _reset_voor_module(module_nr):
    """Gespreksgeschiedenis loopt per module en wordt gereset bij een modulewissel."""
    if st.session_state.get("chat_module") != module_nr:
        st.session_state.chat_module = module_nr
        st.session_state.chat_geschiedenis = []
        st.session_state.chat_beurten = 0
        st.session_state.chat_geopend = set()


def _system_prompt(stap, stappen, profiel, sectoren):
    basis = content.basisblok(profiel, sectoren)
    agent = content.load_prompt("chat_agent").format(
        module_titel=f"{stap['module']} — {content.MODULES[stap['module']]['titel']}",
        titel=stap["titel"],
        staptype=content.TYPE_LABELS[stap["type"]],
        stap_inhoud=content.stap_inhoud(stap),
        module_samenvatting=content.module_samenvatting(stappen),
    )
    delen = [basis, agent]
    if stap["type"] == "toepassing":
        delen.append(
            content.load_prompt("chat_toepassing").format(
                interactie=stap["interactie"].strip(),
                leerdoel=stap["leerdoel"],
            )
        )
    return "\n\n".join(delen)


def _genereer_opening(stap, stappen, profiel, sectoren):
    """Bij een toepassingsstap opent de agent zelf met het scenario."""
    sleutel = (stap["module"], stap["stap"])
    if sleutel in st.session_state.chat_geopend:
        return
    st.session_state.chat_geopend.add(sleutel)
    try:
        stroom = llm.stream(
            _system_prompt(stap, stappen, profiel, sectoren),
            st.session_state.chat_geschiedenis
            + [{"role": "user", "content": "Start de toepassingsoefening."}],
        )
        with st.chat_message("assistant"):
            tekst = st.write_stream(stroom)
    except Exception:
        tekst = FALLBACK
        with st.chat_message("assistant"):
            st.markdown(tekst)
    st.session_state.chat_geschiedenis.append({"role": "assistant", "content": tekst})


def render_chat(stap, stappen, profiel, sectoren):
    _reset_voor_module(stap["module"])

    st.markdown('<div class="chat-titel">💬 AI-coach</div>', unsafe_allow_html=True)
    st.caption(
        "Stel je vragen over deze module. En — tip uit de training zelf — "
        "typ hier geen echte gevoelige gegevens."
    )

    if not llm.available():
        st.info("De AI-coach is niet beschikbaar zonder geconfigureerde API-key.")
        return

    # Alle berichten komen in deze container, zodat het invoerveld eronder
    # altijd onder de conversatie blijft staan.
    gesprek = st.container()

    with gesprek:
        for bericht in st.session_state.chat_geschiedenis:
            with st.chat_message(bericht["role"]):
                st.markdown(bericht["content"])

        # Bij een toepassingsstap neemt de agent het initiatief.
        if stap["type"] == "toepassing":
            _genereer_opening(stap, stappen, profiel, sectoren)

    # Beurtenlimiet per module (kostenbeheersing).
    limiet_bereikt = st.session_state.chat_beurten >= MAX_BEURTEN_PER_MODULE
    if limiet_bereikt:
        st.info(
            "Je hebt het maximum aantal chatberichten voor deze module bereikt. "
            "In een volgende module kan je opnieuw chatten."
        )

    invoer = st.chat_input(
        "Typ je vraag of antwoord…",
        max_chars=MAX_INVOER_TEKENS,
        disabled=limiet_bereikt,
    )
    if not invoer:
        return

    st.session_state.chat_beurten += 1
    st.session_state.chat_geschiedenis.append({"role": "user", "content": invoer})
    with gesprek:
        with st.chat_message("user"):
            st.markdown(invoer)

        try:
            stroom = llm.stream(
                _system_prompt(stap, stappen, profiel, sectoren),
                st.session_state.chat_geschiedenis,
            )
            with st.chat_message("assistant"):
                antwoord = st.write_stream(stroom)
        except Exception:
            antwoord = FALLBACK
            with st.chat_message("assistant"):
                st.markdown(antwoord)
    st.session_state.chat_geschiedenis.append({"role": "assistant", "content": antwoord})
