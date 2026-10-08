import json

import pytest

import content
import llm
import verhaal

VOORBEELD = {
    "moment": "Donderdagavond, laatste ronde",
    "aanleiding": "De wonde van mevrouw Peeters ziet er anders uit dan gisteren. "
                  "De wondverpleegkundige is pas maandag terug.",
    "beeld": "een foto van de wonde van mevrouw Peeters",
    "beeldwoord": "foto",
    "vraag": "Is dit een infectie?",
    "betrokkene": "mevrouw Peeters",
    "herkenbare_details": "Een stukje van haar gezicht, haar polsbandje met naam en "
                          "informatie over haar gezondheid.",
    "categorieen": ["persoonsgegevens", "bijzondere_persoonsgegevens", "beroepsgeheim"],
    "inzet": "het vertrouwen van je patiënt en je beroepsgeheim",
    "plek": "de gang van de afdeling",
    "minimaliseer": "fotografeer alleen de wonde, zonder gezicht of polsbandje",
}
PROFIEL = {"naam": "", "werk": "verpleegkundige in een ziekenhuis", "intro": "",
           "kennisniveau": "maakt kennis"}


def _met(**wijziging):
    return {**VOORBEELD, **wijziging}


# --- valideer ---

def test_voorbeeld_en_fallback_zijn_geldig():
    assert verhaal.valideer(VOORBEELD, PROFIEL)
    assert verhaal.valideer(verhaal.FALLBACK, PROFIEL)


@pytest.mark.parametrize("velden", [
    {k: v for k, v in VOORBEELD.items() if k != "plek"},           # ontbrekend veld
    _met(extra="x"),                                                # extra veld
    _met(moment="x" * 51),                                          # te lang
    _met(beeldwoord="video"),                                       # onbekend beeldwoord
    _met(categorieen=[]),                                           # lege categorieën
    _met(categorieen=["geheim"]),                                   # onbekende categorie
    _met(inzet="je **beroepsgeheim**"),                             # opmaakteken
    _met(inzet="een boete van $500 tot $1000"),                     # wiskunde in st.markdown
    _met(aanleiding="Twee regels.\nNog een regel."),                # regeleinde
    _met(aanleiding="Zonder slotteken"),                            # geen punt
    _met(beeld="de foto van de wonde"),                             # begint niet met 'een '
    _met(plek="je bureau"),                                         # 'je' in plek
    _met(moment=""),                                                # leeg
    _met(vraag=42),                                                 # geen string
])
def test_valideer_verwerpt(velden):
    assert not verhaal.valideer(velden, PROFIEL)


def test_betrokkene_met_naam_van_gebruiker_wordt_verworpen():
    profiel = {**PROFIEL, "naam": "Sarah"}
    assert not verhaal.valideer(_met(betrokkene="mevrouw sarah Janssens"), profiel)
    assert not verhaal.valideer(_met(betrokkene="mevrouw Peeters"), {**PROFIEL, "naam": "Lies Peeters"})


def test_naam_en_plek_worden_als_heel_woord_vergeleken():
    # 'An' zit in 'klanten' en 'je' in 'bijeenkomst', maar niet als woord.
    assert verhaal.valideer(_met(betrokkene="je klanten"), {**PROFIEL, "naam": "An"})
    assert verhaal.valideer(_met(plek="de bijeenkomstruimte"), PROFIEL)


# --- normaliseer ---

def test_normaliseer_punten_en_aanhalingstekens():
    ruw = _met(moment="Donderdagavond, laatste ronde.", vraag='"Is dit een infectie?"',
               plek="  de gang van de afdeling. ", beeldwoord="Foto")
    velden = verhaal.normaliseer(ruw)
    assert velden["moment"] == "Donderdagavond, laatste ronde"
    assert velden["vraag"] == "Is dit een infectie?"
    assert velden["plek"] == "de gang van de afdeling"
    assert velden["beeldwoord"] == "foto"


@pytest.mark.parametrize("gekozen, verwacht", [
    (["bijzondere_persoonsgegevens"], ["persoonsgegevens", "bijzondere_persoonsgegevens"]),
    (["beroepsgeheim"], ["persoonsgegevens", "beroepsgeheim"]),
    (["beroepsgeheim", "bedrijfsgevoelig"], ["bedrijfsgevoelig", "beroepsgeheim"]),
    (["bedrijfsgevoelig"], ["bedrijfsgevoelig"]),
])
def test_normaliseer_vult_categorieen_aan(gekozen, verwacht):
    assert verhaal.normaliseer(_met(categorieen=gekozen))["categorieen"] == verwacht


# --- genereer ---

@pytest.fixture
def met_llm(monkeypatch):
    monkeypatch.setattr(llm, "available", lambda: True)

    def zet(antwoord):
        def complete(*args, **kwargs):
            if isinstance(antwoord, Exception):
                raise antwoord
            return antwoord
        monkeypatch.setattr(llm, "complete", complete)
    return zet


def test_genereer_geldig_antwoord(met_llm):
    met_llm("```json\n" + json.dumps(VOORBEELD, ensure_ascii=False) + "\n```")
    assert verhaal.genereer(PROFIEL) == VOORBEELD


@pytest.mark.parametrize("antwoord", [
    llm.LLMError("time-out"),
    "Hier is een gedicht over de lente.",
    "{dit is geen json}",
    json.dumps(_met(beeldwoord="video")),
])
def test_genereer_valt_terug_op_fallback(met_llm, antwoord):
    met_llm(antwoord)
    assert verhaal.genereer(PROFIEL) == verhaal.FALLBACK


def test_genereer_zonder_werk_en_intro_doet_geen_call(met_llm):
    met_llm(AssertionError("er mag geen call gebeuren"))
    assert verhaal.genereer({"naam": "", "werk": "", "intro": ""}) == verhaal.FALLBACK


def test_prompt_bevat_profiel_en_voorbeelden():
    prompt = verhaal._prompt(PROFIEL)
    assert "verpleegkundige in een ziekenhuis" in prompt
    assert "financieel analist" in prompt
    assert "{" in prompt  # de voorbeelden als JSON-regels


# --- afgeleide velden ---

@pytest.fixture
def module():
    return content.load_module()


def test_moment_klein_en_categorie_zinnen(module):
    velden = _met(categorieen=["beroepsgeheim", "persoonsgegevens"])
    afgeleid = verhaal.afgeleid(velden, module, None)
    assert afgeleid["moment_klein"] == "donderdagavond, laatste ronde"
    zinnen = module["categorie_zinnen"]
    assert afgeleid["categorie_zinnen"] == (
        zinnen["persoonsgegevens"].strip() + " " + zinnen["beroepsgeheim"].strip()
    )


@pytest.mark.parametrize("antwoord, variant, gedeeld", [
    ({"gedeeld": ["Een screenshot", "Code"], "gevoelig": None}, "beeld", None),
    ({"gedeeld": ["De tekst van een mail", "Code"], "gevoelig": None}, "andere",
     "de tekst van een mail en code"),
    ({"gedeeld": ["Code", "Nog niets"], "gevoelig": None}, "andere", "code"),
    ({"gedeeld": ["Nog niets"], "gevoelig": None}, "niets", None),
])
def test_eigen_gedrag_zin(module, antwoord, variant, gedeeld):
    verwacht = module["einde_eigen_gedrag"][variant].strip()
    if gedeeld:
        verwacht = verwacht.format(gedeeld=gedeeld)
    assert verhaal.eigen_gedrag_zin(antwoord, module) == verwacht


def test_eigen_gedrag_zin_met_gevoelig_en_leeg(module):
    zin = verhaal.eigen_gedrag_zin({"gedeeld": ["Een foto"], "gevoelig": "Ja"}, module)
    assert zin.endswith(module["einde_eigen_gedrag"]["met_gevoelig"].strip())
    assert verhaal.eigen_gedrag_zin(None, module) == ""
    assert verhaal.eigen_gedrag_zin({"gedeeld": [], "gevoelig": None}, module) == ""


# --- vul_in ---

def test_vul_in_ontbrekend_veld_gebruikt_fallback():
    assert verhaal.vul_in("Het is {moment}.", {}) == f"Het is {verhaal.FALLBACK['moment']}."


def test_vul_in_laat_geen_lege_alinea_achter():
    assert verhaal.vul_in("A\n\n{eigen_gedrag_zin}\n\nB", {"eigen_gedrag_zin": ""}) == "A\n\nB"


def test_vul_in_interpreteert_accolades_in_waarden_niet():
    assert verhaal.vul_in("{moment}", {"moment": "{beeld}"}) == "{beeld}"
