from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import content
import llm

APP = str(Path(__file__).parent.parent / "slides-app.py")
TIMEOUT = 30


@pytest.fixture(autouse=True)
def zonder_api_key(monkeypatch):
    monkeypatch.setattr(llm, "api_key", lambda: "")


def _knop(at, label):
    return next(b for b in at.button if b.label == label)


def _klik(at, label):
    """Klik en run. AppTest laat na een st.rerun() de elementen van de vorige run
    staan; een tweede run ruimt die op, zodat de volgende zoektocht klopt."""
    _knop(at, label).click()
    at.run()
    at.run()
    assert not at.exception


def _markdown(at):
    return "\n".join(m.value for m in at.markdown)


PROFIEL = {"naam": "Sam", "kennisniveau": "maakt kennis", "gevoelige_data": "Ja",
           "werk": "boekhouder bij een kmo", "intro": ""}


def _start(pagina="module", **profiel):
    """App met een ingevuld profiel, rechtstreeks in de sessie gezet: na de
    intake laat AppTest de formulierelementen staan, wat volgende runs verstoort."""
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.session_state["profiel"] = {**PROFIEL, **profiel}
    at.session_state["pagina"] = pagina
    at.run()
    assert not at.exception
    return at


def test_volledige_doorloop_zonder_api_key():
    at = _start()
    titels = content.load_module()["stappen"]

    # Stap 1: hook-verhaal (fallback) en de activeren-vragen.
    assert "Tien seconden later" in _markdown(at)
    at.get("button_group")[0].set_value(["Een foto"]).run()
    next(r for r in at.radio if r.key == "activeren_gevoelig").set_value("Ja").run()
    assert at.session_state["activeren_antwoord"] == {"gedeeld": ["Een foto"], "gevoelig": "Ja"}

    for _ in range(len(titels) - 1):
        _klik(at, "Volgende >")
    assert at.session_state["stap_idx"] == 5

    # Drie vragen: telkens het juiste antwoord, ongeacht de geschudde volgorde.
    for i, vraag in enumerate(titels[5]["quiz"]):
        radio = next(r for r in at.radio if r.key == f"quizkeuze_1_{i}")
        radio.set_value(vraag["correct"])
        _klik(at, "Bevestig antwoord")
        _klik(at, "Bekijk je score" if i == 2 else "Volgende vraag")

    tekst = _markdown(at)
    assert "Je score: 3 van 3" in tekst
    assert "Nog even herhalen" not in tekst
    assert "Elke prompt is een potentieel datalek" in tekst
    assert "foto of screenshot" in tekst  # eigen gedrag uit stap 1
    assert not any("{" in m.value for m in at.markdown if "<style>" not in m.value)

    # Opnieuw beginnen: terug naar stap 1, quiz gewist, antwoorden uit stap 1 bewaard.
    _klik(at, "Opnieuw beginnen")
    assert at.session_state["stap_idx"] == 0
    assert "quiz_1" not in at.session_state
    assert at.session_state["activeren_antwoord"]["gedeeld"] == ["Een foto"]


def test_lage_score_geeft_herhaling():
    at = _start()
    at.session_state["stap_idx"] = 5
    at.run()
    for i, vraag in enumerate(content.load_module()["stappen"][5]["quiz"]):
        radio = next(r for r in at.radio if r.key == f"quizkeuze_1_{i}")
        radio.set_value((vraag["correct"] + 1) % len(vraag["opties"]))
        _klik(at, "Bevestig antwoord")
        _klik(at, "Bekijk je score" if i == 2 else "Volgende vraag")
    tekst = _markdown(at)
    assert "Je score: 0 van 3" in tekst
    assert "Nog even herhalen" in tekst
    assert "Elke prompt is een potentieel datalek" in tekst


def test_feedback_blijft_tot_volgende_vraag():
    at = _start()
    at.session_state["stap_idx"] = 5
    at.run()
    at.radio[0].set_value(0)
    _klik(at, "Bevestig antwoord")
    # Na de bevestiging: feedback zichtbaar, nog geen tweede vraag.
    assert "Vraag 2 van 3" not in _markdown(at)
    assert "Volgende vraag" in [b.label for b in at.button]
    at.run()  # een gewone rerun verandert niets
    assert "Vraag 2 van 3" not in _markdown(at)
    _klik(at, "Volgende vraag")
    assert "Vraag 2 van 3" in _markdown(at)


def test_activeren_antwoorden_blijven_bij_terugbladeren():
    at = _start()
    at.get("button_group")[0].set_value(["Een foto"]).run()
    next(r for r in at.radio if r.key == "activeren_gevoelig").set_value("Ja").run()
    _klik(at, "Volgende >")
    _klik(at, "< Vorige")
    assert at.get("button_group")[0].value == ["Een foto"]
    assert next(r for r in at.radio if r.key == "activeren_gevoelig").value == "Ja"


def test_vervolgvraag_vervalt_bij_nog_niets():
    at = _start()
    at.get("button_group")[0].set_value(["Een foto"]).run()
    next(r for r in at.radio if r.key == "activeren_gevoelig").set_value("Ja").run()
    at.get("button_group")[0].set_value(["Nog niets"]).run()
    assert at.session_state["activeren_antwoord"] == {"gedeeld": ["Nog niets"], "gevoelig": None}
    assert "activeren_gevoelig" not in [r.key for r in at.radio]


def test_intake_slaat_profiel_op():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    at.text_input[0].input("Sam")
    at.text_input[1].input("advocaat")
    at.radio[1].set_value("Nee")
    # Eén run: een tweede zou de achtergebleven formulierelementen uitlezen.
    _knop(at, "Start de training").click()
    at.run()
    assert at.session_state["profiel"] == {
        "naam": "Sam", "kennisniveau": "maakt kennis", "gevoelige_data": "Nee",
        "werk": "advocaat", "intro": "",
    }
    assert at.session_state["pagina"] == "module"


def test_profiel_aanpassen_behoudt_antwoorden():
    at = _start()
    _klik(at, "Profiel aanpassen")
    assert at.session_state["pagina"] == "intake"
    # Een nieuwe sessie op de intake met het opgeslagen profiel (zie _start).
    at = _start(pagina="intake", gevoelige_data="Nee", werk="advocaat")
    assert at.text_input[0].value == "Sam"
    assert at.text_input[1].value == "advocaat"
    assert at.radio[1].value == "Nee"  # bugfix 10.1
