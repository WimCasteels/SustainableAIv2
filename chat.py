"""Chat-agent: vast paneel naast de slides, reactief op elke stap en leidend bij toepassing.

Berichten in de geschiedenis kunnen een markering dragen:
- `verborgen`: gaat mee naar de API, maar wordt niet getoond (startbericht van
  de toepassingsoefening, zodat de geschiedenis met een user-bericht begint);
- `lokaal`: wordt getoond, maar gaat niet mee naar de API (mislukte beurten).
"""

import streamlit as st

import content
import llm
import verhaal

MAX_BEURTEN = 12  # voor de hele sessie; reset bij "Opnieuw beginnen" en een nieuw profiel
MAX_INVOER_TEKENS = 500
GESPREK_HOOGTE = 480  # px; daarboven scrolt het gesprek binnen het paneel
STARTBERICHT = "Start de toepassingsoefening."

FALLBACK = (
    "De AI-coach is even niet beschikbaar. Je kan gewoon verder met de training "
    "en het later opnieuw proberen."
)


def reset():
    for sleutel in [k for k in st.session_state if str(k).startswith("chat_")]:
        del st.session_state[sleutel]


def _init():
    st.session_state.setdefault("chat_geschiedenis", [])
    st.session_state.setdefault("chat_beurten", 0)
    st.session_state.setdefault("chat_geopend", set())


def _voor_api():
    return [b for b in st.session_state.chat_geschiedenis if not b.get("lokaal")]


def activeren_regel():
    """Eén regel over wat de gebruiker in stap 1 aangaf; leeg als niet beantwoord."""
    antwoord = st.session_state.get("activeren_antwoord") or {}
    gedeeld = verhaal.gedeelde_opties(antwoord)
    if not gedeeld:
        return ""
    if gedeeld == [verhaal.OPTIE_NIETS]:
        return "De gebruiker gaf aan de afgelopen maand nog niets in AI-tools te hebben gezet."
    regel = ("De gebruiker gaf aan al het volgende in AI-tools te hebben gezet: "
             f"{verhaal.opsomming([verhaal.klein(o) for o in gedeeld])}.")
    if antwoord.get("gevoelig"):
        regel += (" Op de vraag of daar een naam, een gezicht of klantgegevens in "
                  f"stond, antwoordde de gebruiker: {antwoord['gevoelig']}.")
    return regel


def _system_prompt(stap, stappen, profiel, velden):
    basis = content.basisblok(profiel, velden)
    agent = content.load_prompt("chat_agent").format(
        module_titel=content.MODULES[stap["module"]]["titel"],
        titel=stap["titel"],
        staptype=content.TYPE_LABELS[stap["type"]],
        stap_inhoud=content.stap_inhoud(stap),
        module_samenvatting=content.module_samenvatting(stappen),
        activeren_regel=activeren_regel(),
    )
    delen = [basis, agent.rstrip()]
    if stap["type"] == "toepassing":
        delen.append(
            content.load_prompt("chat_toepassing").format(
                interactie=stap["interactie"].strip(),
                leerdoel=stap["leerdoel"],
            )
        )
    return "\n\n".join(delen)


def _genereer_opening(stap, stappen, profiel, velden):
    """Bij een toepassingsstap opent de agent zelf met het scenario."""
    sleutel = (stap["module"], stap["stap"])
    if sleutel in st.session_state.chat_geopend:
        return
    st.session_state.chat_geopend.add(sleutel)
    start = {"role": "user", "content": STARTBERICHT, "verborgen": True}
    try:
        stroom = llm.stream(
            _system_prompt(stap, stappen, profiel, velden),
            _voor_api() + [start],
        )
        with st.chat_message("assistant"):
            tekst = st.write_stream(stroom)
    except Exception:
        with st.chat_message("assistant"):
            st.markdown(FALLBACK)
        st.session_state.chat_geschiedenis.append(
            {"role": "assistant", "content": FALLBACK, "lokaal": True}
        )
        return
    st.session_state.chat_geschiedenis += [start, {"role": "assistant", "content": tekst}]


def render_chat(stap, stappen, profiel, velden):
    """`stap` en `stappen` zijn ingevuld (titels en verhaal met de verhaalvelden)."""
    _init()

    st.markdown('<div class="chat-titel">💬 AI-coach</div>', unsafe_allow_html=True)
    st.caption(
        "Stel je vragen over deze training. En — tip uit de training zelf — "
        "typ hier geen echte gevoelige gegevens."
    )

    if not llm.available():
        st.info("De AI-coach is niet beschikbaar zonder geconfigureerde API-key.")
        return

    # Alle berichten komen in deze container met vaste hoogte: het gesprek
    # scrolt binnen het paneel en het invoerveld blijft er altijd onder staan.
    gesprek = st.container(height=GESPREK_HOOGTE)

    with gesprek:
        for bericht in st.session_state.chat_geschiedenis:
            if bericht.get("verborgen"):
                continue
            with st.chat_message(bericht["role"]):
                st.markdown(bericht["content"])

        # Bij een toepassingsstap neemt de agent het initiatief.
        if stap["type"] == "toepassing":
            _genereer_opening(stap, stappen, profiel, velden)

    # Beurtenlimiet voor de hele sessie (kostenbeheersing).
    limiet_bereikt = st.session_state.chat_beurten >= MAX_BEURTEN
    if limiet_bereikt:
        st.info("Je hebt het maximum aantal chatberichten voor deze training bereikt.")

    invoer = st.chat_input(
        "Typ je vraag of antwoord…",
        max_chars=MAX_INVOER_TEKENS,
        disabled=limiet_bereikt,
    )
    if not invoer:
        return

    st.session_state.chat_beurten += 1
    vraag = {"role": "user", "content": invoer}
    st.session_state.chat_geschiedenis.append(vraag)
    with gesprek:
        with st.chat_message("user"):
            st.markdown(invoer)

        try:
            stroom = llm.stream(
                _system_prompt(stap, stappen, profiel, velden),
                _voor_api(),
            )
            with st.chat_message("assistant"):
                antwoord = st.write_stream(stroom)
        except Exception:
            # Een mislukte beurt blijft zichtbaar, maar gaat niet mee naar de API,
            # zodat er geen twee user-berichten na elkaar staan.
            vraag["lokaal"] = True
            with st.chat_message("assistant"):
                st.markdown(FALLBACK)
            st.session_state.chat_geschiedenis.append(
                {"role": "assistant", "content": FALLBACK, "lokaal": True}
            )
            return
    st.session_state.chat_geschiedenis.append({"role": "assistant", "content": antwoord})
