import random

import content
import quiz


def _state():
    return {"antwoorden": [], "feedback": [], "volgorde": {}, "wacht_op_verder": False,
            "samenvatting": None}


def test_permutatie_blijft_gelijk_bij_rerun():
    state = _state()
    eerste = quiz.volgorde(state, 0, 4, rng=random.Random(1))
    # Een rerun met een andere random-bron verandert de bewaarde volgorde niet.
    assert quiz.volgorde(state, 0, 4, rng=random.Random(99)) == eerste
    assert sorted(eerste) == [0, 1, 2, 3]


def test_permutaties_verschillen_tussen_sessies():
    volgordes = {tuple(quiz.volgorde(_state(), 0, 4, rng=random.Random(s))) for s in range(20)}
    assert len(volgordes) > 1


def test_score_met_geschudde_volgorde():
    stap = content.load_module()["stappen"][5]
    state = _state()
    for i, vraag in enumerate(stap["quiz"]):
        perm = quiz.volgorde(state, i, len(vraag["opties"]), rng=random.Random(i))
        # De radio geeft de waarde op de gekozen positie terug: de oorspronkelijke index.
        positie_juist = perm.index(vraag["correct"])
        state["antwoorden"].append(perm[positie_juist])
    assert quiz.score(stap, state) == 3

    state["antwoorden"][1] = (stap["quiz"][1]["correct"] + 1) % 4
    assert quiz.score(stap, state) == 2
