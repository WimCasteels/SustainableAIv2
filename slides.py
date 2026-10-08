"""Slideweergave: stap-rendering, activeren-vragen, progressie-indicator en navigatie."""

import html

import streamlit as st

import chat
import content
import personalize
import quiz
import verhaal

LEEG_ANTWOORD = {"gedeeld": [], "gevoelig": None}


def _progressie(huidige_idx, totaal):
    html_ = '<div class="progress-container">'
    for i in range(totaal):
        cls = "progress-active" if i <= huidige_idx else "progress-inactive"
        html_ += f'<div class="progress-dot {cls}"></div>'
    html_ += "</div>"
    st.markdown(html_, unsafe_allow_html=True)


def opnieuw_beginnen():
    """Terug naar stap 1: profiel, verhaal en activeren-antwoorden blijven, quiz en chat niet."""
    quiz.reset(content.MODULE_NR)
    chat.reset()
    st.session_state.stap_idx = 0


# --- Activeren (stap 1) ---

def _antwoord():
    return st.session_state.setdefault("activeren_antwoord", dict(LEEG_ANTWOORD))


def _heeft_iets_gedeeld(gedeeld):
    return any(o != verhaal.OPTIE_NIETS for o in gedeeld)


def _bewaar_gedeeld():
    antwoord = _antwoord()
    antwoord["gedeeld"] = list(st.session_state.get("activeren_gedeeld") or [])
    # Zonder iets gedeeld verdwijnt de vervolgvraag, en dus ook het antwoord erop.
    if not _heeft_iets_gedeeld(antwoord["gedeeld"]):
        antwoord["gevoelig"] = None
        st.session_state.pop("activeren_gevoelig", None)


def _bewaar_gevoelig():
    _antwoord()["gevoelig"] = st.session_state.get("activeren_gevoelig")


def _render_activeren(stap):
    blok = stap["activeren"]
    antwoord = _antwoord()
    # Streamlit wist de state van widgets die niet getoond worden; daarom komt
    # de beginwaarde uit activeren_antwoord, zodat terugbladeren niets leegmaakt.
    st.pills(
        blok["vraag"],
        blok["opties"],
        selection_mode="multi",
        default=[o for o in antwoord["gedeeld"] if o in blok["opties"]],
        key="activeren_gedeeld",
        on_change=_bewaar_gedeeld,
    )
    if _heeft_iets_gedeeld(antwoord["gedeeld"]):
        opties = blok["vervolgopties"]
        st.radio(
            blok["vervolgvraag"],
            opties,
            index=opties.index(antwoord["gevoelig"]) if antwoord["gevoelig"] in opties else None,
            horizontal=True,
            key="activeren_gevoelig",
            on_change=_bewaar_gevoelig,
        )


# --- Stap ---

def render_stap(stappen, profiel, velden):
    """`stappen` zijn ingevuld met de verhaalvelden (titel, verhaal, einde)."""
    idx = st.session_state.stap_idx
    stap = stappen[idx]

    _progressie(idx, len(stappen))
    st.markdown(
        f'<div class="slide-counter">{html.escape(content.MODULES[stap["module"]]["titel"])}'
        f' · stap {idx + 1} van {len(stappen)}'
        f'<span class="stap-badge stap-badge-{stap["type"]}">'
        f'{content.TYPE_LABELS[stap["type"]]}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="page-title">{html.escape(stap["titel"])}</div>',
                unsafe_allow_html=True)

    # Afbeelding alleen tonen als het bestand beschikbaar is.
    afbeelding = content.image_path(stap)
    if afbeelding:
        st.image(str(afbeelding), width="stretch")

    personalize.toon_verhaal(stap["verhaal"], stap["stap"])

    zichtbaar = bool(stap.get("content_zichtbaar") and stap.get("content"))
    if zichtbaar:
        st.markdown(stap["content"], unsafe_allow_html=True)

    if stap["type"] == "activeren":
        _render_activeren(stap)
    elif stap["type"] == "quiz_verankering":
        quiz.render_quiz(stap, profiel, velden)
    else:
        personalize.render_context(stap, profiel, velden)

    with st.expander("🎯 Leerdoel en extra info"):
        st.markdown(f"**Leerdoel:** {stap['leerdoel']}")
        if stap.get("content") and not zichtbaar:
            st.markdown(stap["content"], unsafe_allow_html=True)

    # Navigatie: vorige/volgende, stap-slider, opnieuw beginnen na de laatste stap.
    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if idx > 0 and st.button("< Vorige", width="stretch"):
            st.session_state.stap_idx -= 1
            st.rerun()

    with col3:
        if idx < len(stappen) - 1:
            if st.button("Volgende >", width="stretch"):
                st.session_state.stap_idx += 1
                st.rerun()
        elif st.button("Opnieuw beginnen", width="stretch"):
            opnieuw_beginnen()
            st.rerun()

    with col2:
        gekozen = st.select_slider(
            "Ga naar stap",
            options=list(range(len(stappen))),
            value=idx,
            format_func=lambda i: f"Stap {i + 1}",
            label_visibility="collapsed",
        )
        if gekozen != idx:
            st.session_state.stap_idx = gekozen
            st.rerun()
