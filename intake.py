"""Intake: korte, gestructureerde profielbepaling plus transparantieverklaring."""

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

SECTOREN = {
    "Zorg": "zorg",
    "Overheid": "overheid",
    "Financieel": "financieel",
    "Onderwijs": "onderwijs",
    "Juridisch": "juridisch",
    "IT": "it",
    "Anders": "anders",
}

TRANSPARANTIE = """
**Wat gebeurt er met jouw gegevens?** Deze app doet zelf wat ze predikt.
We vragen alleen wat de personalisatie nodig heeft — geen e-mailadres, geen tracking.
Je profiel, chatberichten en quizscores leven uitsluitend in deze sessie en
verdwijnen wanneer je het venster sluit; de app slaat niets op.

Om de teksten te personaliseren sturen we je antwoorden mee naar een taalmodel
van **Mistral** (een Europese aanbieder). Die aanroep verloopt via **OpenRouter**,
een Amerikaanse tussenpartij, en de app draait op Streamlit Community Cloud
(Amerikaanse infrastructuur). We hebben de routing zo strikt mogelijk ingesteld
(geen logging of training door tussenliggende providers), maar wees je hiervan
bewust — en deel hier dus geen echte gevoelige gegevens. Zie de
verwerkingsvoorwaarden van [OpenRouter](https://openrouter.ai/privacy) en
[Mistral](https://mistral.ai/terms/).
"""


def render_intake():
    st.markdown(
        """
        <div class="context-box" style="text-align: center;">
            <h2 style="margin: 0 0 0.5rem 0; color: #1e293b;">Elke prompt is een potentieel datalek</h2>
            <p style="color: #64748b; margin: 0;">Een korte training over de gevaren van het delen
            van data met AI-tools. Vertel eerst iets over jezelf, dan passen we de training aan jou aan.
            Alles is optioneel.</p>
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
        sector_label = st.selectbox(
            "In welke sector werk of studeer je?",
            list(SECTOREN),
            index=list(SECTOREN.values()).index(bestaand["sector_code"])
            if bestaand.get("sector_code") in SECTOREN.values() else 6,
        )
        sector_anders = st.text_input(
            "Bij 'Anders': in welke sector dan?",
            value=bestaand.get("sector_anders", ""),
            placeholder="Vrij in te vullen (optioneel)",
        )
        intro = st.text_area(
            "Vertel kort iets over jezelf en waarom je hier bent",
            value=bestaand.get("intro", ""),
            placeholder="Bijv. Ik werk als data-analist en wil weten wat ik veilig met AI-tools kan delen. (optioneel)",
            height=100,
        )
        gestart = st.form_submit_button("Start de training", width="stretch")

    with st.expander("Wat gebeurt er met jouw gegevens?", expanded=False):
        st.markdown(TRANSPARANTIE)

    if gestart:
        sector_code = SECTOREN[sector_label]
        sector = sector_anders.strip() if sector_code == "anders" and sector_anders.strip() else sector_label
        st.session_state.profiel = {
            "naam": naam.strip(),
            "kennisniveau": KENNISNIVEAUS[kennis_label],
            "gevoelige_data": gevoelig.lower(),
            "sector_code": sector_code,
            "sector": sector,
            "sector_anders": sector_anders.strip(),
            "intro": intro.strip(),
        }
        # Nieuw profiel: personalisatiecache en gespreksstate opruimen.
        st.session_state.pers_cache = {}
        for key in [k for k in st.session_state if str(k).startswith(("chat_", "quiz_"))]:
            del st.session_state[key]
        st.session_state.pagina = "overzicht"
        st.rerun()
