"""Quizflow: drie vaste vragen, gepersonaliseerde feedback en een score-afhankelijke samenvatting."""

import streamlit as st

import content
import llm
import personalize


def _state(module_nr):
    sleutel = f"quiz_{module_nr}"
    if sleutel not in st.session_state:
        st.session_state[sleutel] = {
            "vraag_idx": 0,        # eerstvolgende onbeantwoorde vraag
            "antwoorden": [],      # gekozen optie-index per vraag
            "feedback": [],        # gegenereerde feedbacktekst per vraag
            "samenvatting": None,
        }
    return st.session_state[sleutel]


def _score(stap, state):
    return sum(
        1 for i, keuze in enumerate(state["antwoorden"])
        if keuze == stap["quiz"][i]["correct"]
    )


def _feedback_prompt(stap, vraag, keuze, profiel, sectoren):
    basis = content.basisblok(profiel, sectoren)
    taak = content.load_prompt("quiz_feedback").format(
        titel=stap["titel"],
        vraag=vraag["vraag"],
        gekozen_optie=vraag["opties"][keuze],
        correcte_optie=vraag["opties"][vraag["correct"]],
        feedback_basis=vraag["feedback_basis"].strip(),
    )
    return f"{basis}\n\n{taak}"


def _samenvatting_prompt(stap, state, profiel, sectoren):
    basis = content.basisblok(profiel, sectoren)
    score = _score(stap, state)
    gemist = [
        stap["quiz"][i] for i, keuze in enumerate(state["antwoorden"])
        if keuze != stap["quiz"][i]["correct"]
    ]
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
        score=score,
        gemiste_leerdoelen=gemiste_leerdoelen,
        context=stap["context"].strip(),
    )
    return f"{basis}\n\n{taak}"


def _genereer(systeem):
    """Eén niet-interactieve generatie met streaming; raise bij falen."""
    stroom = llm.stream(systeem, [{"role": "user", "content": "Schrijf de tekst."}])
    return personalize.stream_tekst(stroom)


def _toon_beantwoord(stap, state, tot_en_met):
    for i in range(tot_en_met):
        vraag = stap["quiz"][i]
        keuze = state["antwoorden"][i]
        juist = keuze == vraag["correct"]
        icoon = "✅" if juist else "❌"
        st.markdown(f"**Vraag {i + 1}. {vraag['vraag']}**")
        st.markdown(f"{icoon} Jouw antwoord: *{vraag['opties'][keuze]}*")
        if not juist:
            st.markdown(f"Correct antwoord: *{vraag['opties'][vraag['correct']]}*")
        personalize.toon_tekst(state["feedback"][i])
        st.markdown("---")


def render_quiz(stap, profiel, sectoren):
    state = _state(stap["module"])
    vragen = stap["quiz"]
    idx = state["vraag_idx"]

    _toon_beantwoord(stap, state, min(idx, len(vragen)))

    # Nog vragen open: toon de huidige vraag.
    if idx < len(vragen):
        vraag = vragen[idx]
        st.markdown(f"**Vraag {idx + 1} van {len(vragen)}. {vraag['vraag']}**")
        keuze_label = st.radio(
            "Kies je antwoord",
            vraag["opties"],
            index=None,
            key=f"quizkeuze_{stap['module']}_{idx}",
            label_visibility="collapsed",
        )
        if st.button("Bevestig antwoord", disabled=keuze_label is None):
            keuze = vraag["opties"].index(keuze_label)
            state["antwoorden"].append(keuze)
            juist = keuze == vraag["correct"]
            st.markdown("✅ **Juist!**" if juist else "❌ **Niet juist.**")
            if llm.available():
                try:
                    feedback = _genereer(_feedback_prompt(stap, vraag, keuze, profiel, sectoren))
                except Exception:
                    feedback = vraag["feedback_basis"].strip()
                    st.markdown(feedback)
            else:
                feedback = vraag["feedback_basis"].strip()
                st.markdown(feedback)
            state["feedback"].append(feedback)
            state["vraag_idx"] += 1
            if st.button("Verder"):
                st.rerun()
        return

    # Alle vragen beantwoord: score en samenvatting.
    score = _score(stap, state)
    st.markdown(f"### Je score: {score} van {len(vragen)}")

    if state["samenvatting"] is None:
        if llm.available():
            try:
                state["samenvatting"] = _genereer(
                    _samenvatting_prompt(stap, state, profiel, sectoren)
                )
                st.rerun()
            except Exception:
                state["samenvatting"] = stap["context"].strip()
        else:
            state["samenvatting"] = stap["context"].strip()

    if state["samenvatting"] is not None:
        personalize.toon_tekst(state["samenvatting"])

    if st.button("Quiz opnieuw maken"):
        del st.session_state[f"quiz_{stap['module']}"]
        for sleutel in [k for k in st.session_state if str(k).startswith(f"quizkeuze_{stap['module']}_")]:
            del st.session_state[sleutel]
        st.rerun()
