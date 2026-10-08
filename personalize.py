"""Personalisatie van contextteksten: promptopbouw per staptype en streaming naar de UI.

De LLM genereert Markdown (korte alinea's, hoogstens drie bullets — zie de
prompt-templates) die in een omkaderd vak gerenderd wordt. De verhaaltekst
staat erboven in een eigen stijl en wordt nooit door de LLM herschreven.
"""

import streamlit as st

import content
import llm

# Alleen deze staptypes hebben een personalisatietemplate; bij toepassing is de
# chat-agent de gepersonaliseerde laag en blijft de contexttekst vast, bij de
# quiz wordt de contexttekst gebruikt voor de herhaling bij een lage score.
PERSONALISEERBAAR = {"kern", "verdieping"}


def toon_verhaal(tekst, sleutel):
    """Render ingevulde verhaaltekst in de `.verhaal-box`-stijl. De CSS richt
    zich op de containerkey (`st-key-verhaal_…`); de tekst zelf gaat zonder
    unsafe_allow_html door st.markdown."""
    with st.container(key=f"verhaal_{sleutel}"):
        st.markdown(tekst)


def toon_tekst(tekst):
    """Render een (Markdown-)tekst in een omkaderd vak, zodat opmaak zoals
    vet en bullets effectief gerenderd wordt."""
    with st.container(border=True):
        st.markdown(tekst)


def stream_tekst(stroom):
    """Stream een completion in een omkaderd vak en geef de volledige tekst terug.
    Faalt de stream halverwege, dan verdwijnt de halve tekst en gaat de fout
    naar de aanroeper, die de originele tekst toont."""
    plaats = st.empty()
    try:
        with plaats.container(border=True):
            tekst = st.write_stream(stroom)
        if not isinstance(tekst, str) or not tekst.strip():
            raise llm.LLMError("Leeg antwoord van het taalmodel.")
        return tekst
    except Exception:
        plaats.empty()
        raise


def _system_prompt(stap, profiel, velden):
    basis = content.basisblok(profiel, velden)
    template = content.load_prompt(stap["type"])
    taak = template.format(titel=stap["titel"], context=stap["context"].strip())
    return f"{basis}\n\n{taak}"


def _toon_origineel(stap, melding=None):
    toon_tekst(stap["context"].strip())
    if melding:
        st.caption(melding)


def render_context(stap, profiel, velden):
    """Toon de contexttekst van een stap: gepersonaliseerd waar het kan,
    origineel waar het moet (graceful degradation)."""
    if stap["type"] not in PERSONALISEERBAAR:
        _toon_origineel(stap)
        return

    if not llm.available():
        _toon_origineel(stap, "Personalisatie is niet beschikbaar; je ziet de standaardtekst.")
        return

    cache = st.session_state.setdefault("pers_cache", {})
    sleutel = (content.profiel_hash(profiel), stap["module"], stap["stap"])
    if sleutel in cache:
        toon_tekst(cache[sleutel])
        return

    try:
        stroom = llm.stream(
            _system_prompt(stap, profiel, velden),
            [{"role": "user", "content": "Schrijf de tekst."}],
        )
        tekst = stream_tekst(stroom)
    except Exception:
        _toon_origineel(stap, "Personalisatie lukte even niet; je ziet de standaardtekst.")
        return

    cache[sleutel] = tekst
