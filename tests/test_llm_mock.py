"""Bugfixes met een gemockt taalmodel: 10.2 (half gestreamde tekst) en 10.4
(chatgeschiedenis die met een assistant-bericht begint)."""

from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

import chat
import llm

TIMEOUT = 30


def _halve_stroom(*args, **kwargs):
    def tokens():
        yield "HALVE"
        yield "TEKST"
        raise RuntimeError("verbinding verbroken")
    return tokens()


def _markdown(at):
    return "\n".join(m.value for m in at.markdown)


def _context_script():
    import content
    import personalize
    import verhaal

    stap = content.load_module()["stappen"][1]
    personalize.render_context(stap, {"naam": "", "werk": "advocaat"}, verhaal.FALLBACK)


def _feedback_script():
    import streamlit as st

    import content
    import quiz
    import verhaal

    stap = content.load_module()["stappen"][5]
    st.session_state.setdefault("quiz_1", {
        "antwoorden": [], "feedback": [], "volgorde": {0: [0, 1, 2, 3]},
        "wacht_op_verder": False, "samenvatting": None,
    })
    quiz.render_quiz(stap, {"naam": ""}, verhaal.FALLBACK)


def _chat_script():
    import chat
    import content
    import verhaal

    stappen = verhaal.vul_stappen(content.load_module()["stappen"], verhaal.FALLBACK)
    chat.render_chat(stappen[4], stappen, {"naam": ""}, verhaal.FALLBACK)


def test_halve_stream_toont_alleen_originele_tekst(monkeypatch):
    monkeypatch.setattr(llm, "available", lambda: True)
    monkeypatch.setattr(llm, "stream", _halve_stroom)
    at = AppTest.from_function(_context_script, default_timeout=TIMEOUT).run()
    assert not at.exception
    tekst = _markdown(at)
    assert "HALVE" not in tekst
    assert "De AVG noemt alles wat naar een persoon te herleiden is" in tekst


def test_halve_stream_bij_quizfeedback_toont_feedback_basis(monkeypatch):
    monkeypatch.setattr(llm, "available", lambda: True)
    monkeypatch.setattr(llm, "stream", _halve_stroom)
    at = AppTest.from_function(_feedback_script, default_timeout=TIMEOUT).run()
    at.radio[0].set_value(2)
    next(b for b in at.button if b.label == "Bevestig antwoord").click()
    at.run()
    at.run()
    assert not at.exception
    tekst = _markdown(at)
    assert "HALVE" not in tekst
    assert "Wat je uploadt, wordt bewaard in logbestanden" in tekst


class _NepClient:
    """Vangt de berichten op die naar de API gaan en streamt een vast antwoord."""

    def __init__(self, oproepen):
        self.oproepen = oproepen
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.oproepen.append(kwargs["messages"])
        delta = SimpleNamespace(content="Het is opnieuw dinsdag. Wat doe je nu?")
        return iter([SimpleNamespace(choices=[SimpleNamespace(delta=delta)])])


@pytest.fixture
def oproepen(monkeypatch):
    lijst = []
    monkeypatch.setattr(llm, "api_key", lambda: "test-key")
    monkeypatch.setattr(llm, "_client", lambda *a, **k: _NepClient(lijst))
    return lijst


def test_chatgeschiedenis_begint_met_user_bericht(oproepen):
    at = AppTest.from_function(_chat_script, default_timeout=TIMEOUT).run()
    assert not at.exception
    # De opening is zichtbaar, het verborgen startbericht niet.
    assert [m.name for m in at.chat_message] == ["assistant"]

    at.chat_input[0].set_value("Ik snijd de foto bij en gebruik de goedgekeurde tool.").run()
    assert not at.exception

    assert len(oproepen) == 2
    for berichten in oproepen:
        assert berichten[0]["role"] == "system"
        assert berichten[1]["role"] == "user"
        assert all(set(b) == {"role", "content"} for b in berichten)
    assert oproepen[1][1]["content"] == chat.STARTBERICHT
    assert [b["role"] for b in oproepen[1][1:]] == ["user", "assistant", "user"]


def test_mislukte_beurt_gaat_niet_mee_naar_de_api(oproepen, monkeypatch):
    at = AppTest.from_function(_chat_script, default_timeout=TIMEOUT).run()

    def kapot(**kwargs):
        raise RuntimeError("time-out")
    monkeypatch.setattr(llm, "_client", lambda *a, **k: SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=kapot))))
    at.chat_input[0].set_value("Eerste poging").run()
    assert chat.FALLBACK in _markdown(at)

    monkeypatch.setattr(llm, "_client", lambda *a, **k: _NepClient(oproepen))
    at.chat_input[0].set_value("Tweede poging").run()
    rollen = [b["role"] for b in oproepen[-1][1:]]
    assert rollen == ["user", "assistant", "user"]
    assert oproepen[-1][-1]["content"] == "Tweede poging"
