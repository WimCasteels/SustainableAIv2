"""Quizflow: drie situatievragen met geschudde opties, gepersonaliseerde feedback,
een herhaling bij een lage score en daarna het verhaaleinde."""

import random

import streamlit as st

import content
import llm
import personalize

# Bij deze score of lager volgt een korte herhaling van de gemiste punten.
MAX_SCORE_HERHALING = 1


def _state(module_nr):
    sleutel = f"quiz_{module_nr}"
    if sleutel not in st.session_state:
        st.session_state[sleutel] = {
            "antwoorden": [],          # gekozen (oorspronkelijke) optie-index per vraag
            "feedback": [],            # feedbacktekst per vraag
            "volgorde": {},            # vraagindex -> permutatie van de optie-indexen
            "wacht_op_verder": False,  # feedback staat er, wacht op "Volgende vraag"
            "samenvatting": None,
        }
    return st.session_state[sleutel]


def reset(module_nr):
    """Wis de quizstatus, inclusief de permutaties en de radio-keuzes."""
    st.session_state.pop(f"quiz_{module_nr}", None)
    for sleutel in [k for k in st.session_state if str(k).startswith(f"quizkeuze_{module_nr}_")]:
        del st.session_state[sleutel]


def volgorde(state, i, aantal, rng=random):
    """Permutatie van de opties van vraag i; één keer bepaald en daarna bewaard."""
    if i not in state["volgorde"]:
        perm = list(range(aantal))
        rng.shuffle(perm)
        state["volgorde"][i] = perm
    return state["volgorde"][i]


def score(stap, state):
    return sum(
        1 for i, keuze in enumerate(state["antwoorden"])
        if keuze == stap["quiz"][i]["correct"]
    )


def _gemist(stap, state):
    return [
        stap["quiz"][i] for i, keuze in enumerate(state["antwoorden"])
        if keuze != stap["quiz"][i]["correct"]
    ]


def _feedback_prompt(stap, vraag, keuze, profiel, velden):
    basis = content.basisblok(profiel, velden)
    taak = content.load_prompt("quiz_feedback").format(
        titel=stap["titel"],
        vraag=vraag["vraag"],
        gekozen_optie=vraag["opties"][keuze],
        correcte_optie=vraag["opties"][vraag["correct"]],
        feedback_basis=vraag["feedback_basis"].strip(),
    )
    return f"{basis}\n\n{taak}"


def _samenvatting_prompt(stap, state, profiel, velden):
    basis = content.basisblok(profiel, velden)
    gemist = _gemist(stap, state)
    if gemist:
        vragen = "; ".join(v["vraag"] for v in gemist)
        kernen = " ".join(v["feedback_basis"].strip() for v in gemist)
        gemiste_leerdoelen = (
            f"De volgende vragen werden fout beantwoord: {vragen} "
            f"De bijhorende kernpunten: {kernen}"
        )
    else:
        gemiste_leerdoelen = ""
    taak = content.load_prompt("quiz_samenvatting").format(
        score=score(stap, state),
        gemiste_leerdoelen=gemiste_leerdoelen,
        context=stap["context"].strip(),
    )
    return f"{basis}\n\n{taak}"


def _genereer(systeem):
    """Eén niet-interactieve generatie met streaming; raise bij falen."""
    stroom = llm.stream(systeem, [{"role": "user", "content": "Schrijf de tekst."}])
    return personalize.stream_tekst(stroom)


def _toon_beantwoord(stap, state):
    for i, keuze in enumerate(state["antwoorden"]):
        vraag = stap["quiz"][i]
        juist = keuze == vraag["correct"]
        icoon = "✅" if juist else "❌"
        st.markdown(f"**Vraag {i + 1}. {vraag['vraag']}**")
        st.markdown(f"{icoon} Jouw antwoord: *{vraag['opties'][keuze]}*")
        if not juist:
            st.markdown(f"Correct antwoord: *{vraag['opties'][vraag['correct']]}*")
        personalize.toon_tekst(state["feedback"][i])
        st.markdown("---")


def _toon_vraag(stap, state, idx, profiel, velden):
    vragen = stap["quiz"]
    vraag = vragen[idx]
    st.markdown(f"**Vraag {idx + 1} van {len(vragen)}. {vraag['vraag']}**")
    # De radio toont de opties geschud, maar geeft de oorspronkelijke index terug.
    keuze = st.radio(
        "Kies je antwoord",
        volgorde(state, idx, len(vraag["opties"])),
        format_func=lambda j: vraag["opties"][j],
        index=None,
        key=f"quizkeuze_{stap['module']}_{idx}",
        label_visibility="collapsed",
    )
    if not st.button("Bevestig antwoord", disabled=keuze is None):
        return

    feedback = vraag["feedback_basis"].strip()
    if llm.available():
        try:
            feedback = _genereer(_feedback_prompt(stap, vraag, keuze, profiel, velden))
        except Exception:
            pass
    state["antwoorden"].append(keuze)
    state["feedback"].append(feedback)
    state["wacht_op_verder"] = True
    st.rerun()


def _toon_herhaling(stap, state, profiel, velden):
    """Korte herhaling van de gemiste punten, alleen bij een lage score."""
    if state["samenvatting"] is None:
        terugval = "\n\n".join(v["feedback_basis"].strip() for v in _gemist(stap, state))
        tekst = None
        if llm.available():
            try:
                tekst = _genereer(_samenvatting_prompt(stap, state, profiel, velden))
            except Exception:
                pass
        state["samenvatting"] = tekst or terugval
        if tekst:
            # De gestreamde tekst staat er al; rerun voor een rustige eindweergave.
            st.rerun()
    st.markdown("**Nog even herhalen**")
    personalize.toon_tekst(state["samenvatting"])


def render_quiz(stap, profiel, velden):
    """Quiz van stap 6; `stap` is ingevuld (titel, verhaal, einde)."""
    state = _state(stap["module"])
    vragen = stap["quiz"]
    idx = len(state["antwoorden"])

    _toon_beantwoord(stap, state)

    if state["wacht_op_verder"]:
        laatste = idx >= len(vragen)
        if st.button("Bekijk je score" if laatste else "Volgende vraag"):
            state["wacht_op_verder"] = False
            st.rerun()
        return

    if idx < len(vragen):
        _toon_vraag(stap, state, idx, profiel, velden)
        return

    # Alle vragen beantwoord: score, eventueel herhaling, en het einde.
    behaald = score(stap, state)
    st.markdown(f"### Je score: {behaald} van {len(vragen)}")
    if behaald <= MAX_SCORE_HERHALING:
        _toon_herhaling(stap, state, profiel, velden)

    personalize.toon_verhaal(stap["einde"], "einde")

    if st.button("Quiz opnieuw maken"):
        reset(stap["module"])
        st.rerun()
