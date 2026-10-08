"""Intake: korte profielbepaling plus transparantieverklaring."""

import streamlit as st

KENNISNIVEAUS = {
    "Ik maak kennis met AI": "maakt kennis",
    "Ik werk er al mee": "werkt ermee",
    "Ik wil verdiepen": "wil verdiepen",
}

GEVOELIGE_DATA = [
    "Ja",
    "Nee",
    "Ik weet niet wat gevoelige data is",
]

MAX_WERK_TEKENS = 120
MAX_INTRO_TEKENS = 500

TRANSPARANTIE = """
**Wat gebeurt er met jouw gegevens?** Deze app doet zelf wat ze predikt. We
vragen alleen wat de personalisatie nodig heeft: geen e-mailadres, geen
tracking. Je profiel, je antwoorden, chatberichten en quizscores leven
uitsluitend in deze sessie en verdwijnen wanneer je het venster sluit. De app
slaat niets op.

Om het verhaal en de teksten op jouw werk af te stemmen, sturen we je antwoorden
mee naar een taalmodel van **Mistral** (een Europese aanbieder). Die aanroep
verloopt via **OpenRouter**, een Amerikaanse tussenpartij, en de app draait op
Streamlit Community Cloud (Amerikaanse infrastructuur). We hebben de routing zo
strikt mogelijk ingesteld (geen logging of training door tussenliggende
providers), maar wees je hiervan bewust. Een algemene omschrijving van je werk
volstaat, en deel hier geen echte gevoelige gegevens. Zie de
verwerkingsvoorwaarden van [OpenRouter](https://openrouter.ai/privacy) en
[Mistral](https://mistral.ai/terms/).
"""

# Sessiestatus die bij een nieuw profiel opnieuw moet beginnen.
RESET_SLEUTELS = ("pers_cache", "verhaal_cache", "activeren_antwoord")
RESET_PREFIXEN = ("chat_", "quiz_", "quizkeuze_", "activeren_")


def render_intake():
    st.markdown(
        """
        <div class="context-box" style="text-align: center;">
            <h2 style="margin: 0 0 0.5rem 0; color: #1e293b;">Elke prompt is een potentieel datalek</h2>
            <p style="color: #64748b; margin: 0;">Een korte training van een kwartier over wat er
            gebeurt met wat je in een AI-tool zet. Vertel eerst iets over jezelf, dan maken we het
            verhaal op jouw maat. Alles is optioneel.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    bestaand = st.session_state.get("profiel") or {}

    with st.form("intake"):
        naam = st.text_input(
            "Hoe wil je aangesproken worden?",
            value=bestaand.get("naam", ""),
            placeholder="Bijv. Jan (optioneel)",
        )
        kennis_label = st.radio(
            "Wat is je kennisniveau van AI?",
            list(KENNISNIVEAUS),
            index=list(KENNISNIVEAUS.values()).index(bestaand["kennisniveau"])
            if bestaand.get("kennisniveau") in KENNISNIVEAUS.values() else 0,
        )
        gevoelig = st.radio(
            "Werk je met gevoelige data?",
            GEVOELIGE_DATA,
            index=GEVOELIGE_DATA.index(bestaand["gevoelige_data"])
            if bestaand.get("gevoelige_data") in GEVOELIGE_DATA else 0,
        )
        werk = st.text_input(
            "Wat doe je, en waar?",
            value=bestaand.get("werk", ""),
            placeholder="Bv. verpleegkundige in een ziekenhuis, leerkracht in het secundair, "
                        "student rechten (optioneel)",
            help="Een algemene omschrijving volstaat. Vermeld geen namen van collega's, "
                 "klanten of je werkgever.",
            max_chars=MAX_WERK_TEKENS,
        )
        intro = st.text_area(
            "Vertel kort iets over jezelf en waarom je hier bent",
            value=bestaand.get("intro", ""),
            placeholder="Bijv. Ik werk als data-analist en wil weten wat ik veilig met AI-tools kan delen. (optioneel)",
            height=100,
            max_chars=MAX_INTRO_TEKENS,
        )
        gestart = st.form_submit_button("Start de training", width="stretch")

    with st.expander("Wat gebeurt er met jouw gegevens?", expanded=False):
        st.markdown(TRANSPARANTIE)

    if gestart:
        st.session_state.profiel = {
            "naam": naam.strip(),
            "kennisniveau": KENNISNIVEAUS[kennis_label],
            "gevoelige_data": gevoelig,
            "werk": werk.strip(),
            "intro": intro.strip(),
        }
        # Nieuw profiel: caches, activeren-antwoorden, quiz- en gespreksstate opruimen.
        for key in [k for k in st.session_state
                    if k in RESET_SLEUTELS or str(k).startswith(RESET_PREFIXEN)]:
            del st.session_state[key]
        st.session_state.pagina = "module"
        st.session_state.stap_idx = 0
        st.rerun()
