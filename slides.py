"""Slideweergave: stap-rendering, progressie-indicator en navigatie binnen een module."""

import streamlit as st

import content
import personalize
import quiz


def _progressie(huidige_idx, totaal=5):
    html = '<div class="progress-container">'
    for i in range(totaal):
        cls = "progress-active" if i <= huidige_idx else "progress-inactive"
        html += f'<div class="progress-dot {cls}"></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_stap(stappen, profiel, sectoren):
    idx = st.session_state.stap_idx
    stap = stappen[idx]
    module_nr = stap["module"]

    _progressie(idx)
    st.markdown(
        f'<div class="slide-counter">Module {module_nr} — '
        f'{content.MODULES[module_nr]["titel"]} · stap {idx + 1} van {len(stappen)}'
        f'<span class="stap-badge stap-badge-{stap["type"]}">'
        f'{content.TYPE_LABELS[stap["type"]]}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="page-title">{stap["titel"]}</div>', unsafe_allow_html=True)

    # Afbeelding alleen tonen als het bestand beschikbaar is.
    afbeelding = content.image_path(stap)
    if afbeelding:
        st.image(str(afbeelding), width="stretch")

    # De gepersonaliseerde tekst (of de quiz) staat bovenaan; het leerdoel en de
    # extra inhoudsblokken zijn uitklapbaar daaronder.
    if stap["type"] == "quiz_verankering":
        quiz.render_quiz(stap, profiel, sectoren)
    else:
        personalize.render_context(stap, profiel, sectoren)

    with st.expander("🎯 Leerdoel en extra info"):
        st.markdown(f"**Leerdoel:** {stap['leerdoel']}")
        if stap.get("content"):
            st.markdown(stap["content"], unsafe_allow_html=True)

    # Navigatie: vorige/volgende, stap-slider, terug naar het overzicht via app.py.
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
        elif st.button("Naar overzicht ✓", width="stretch"):
            st.session_state.pagina = "overzicht"
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
