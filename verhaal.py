"""Verhaalvelden: genereren, valideren en invullen van het verhaal van de gebruiker.

De verhaaltekst in de YAML is een vast skelet met invulvelden. De LLM levert
alleen de velden (één call per profiel); de tekst zelf wordt nooit herschreven.
Zie design-document-v3.md §5.
"""

import hashlib
import json
import logging
import re

import streamlit as st

import content
import llm

log = logging.getLogger(__name__)

# Vaste volgorde: ook de volgorde van de categoriezinnen in de tekst.
CATEGORIEEN = [
    "persoonsgegevens",
    "bijzondere_persoonsgegevens",
    "bedrijfsgevoelig",
    "beroepsgeheim",
]
BEELDWOORDEN = ("foto", "scan", "screenshot")

# Maximale lengte per stringveld.
LIMIETEN = {
    "moment": 50,
    "aanleiding": 220,
    "beeld": 90,
    "vraag": 80,
    "betrokkene": 40,
    "herkenbare_details": 160,
    "inzet": 90,
    "plek": 50,
    "minimaliseer": 90,
}
VELDEN = set(LIMIETEN) | {"beeldwoord", "categorieen"}

ZONDER_PUNT = ("moment", "beeld", "inzet", "plek", "minimaliseer", "betrokkene")
MET_SLOTTEKEN = ("aanleiding", "herkenbare_details")
# Opmaak- en formatteringstekens; `$` en `~` zetten st.markdown om naar wiskunde
# of doorhaling.
VERBODEN_TEKENS = set("{}<>*_`#[]$~")
VERBODEN_PLEKWOORDEN = {"je", "jouw", "mijn", "ons", "onze"}
# De betrokkene is iemand anders dan de gebruiker; het einde zegt
# "krijgt niemand bericht: {betrokkene} niet, en jij ook niet".
VERBODEN_BETROKKENEN = {"jij", "jijzelf", "jezelf", "je", "zelf", "ik", "mezelf", "u", "uzelf"}
AANHALINGSTEKENS = "\"'“”‘’„«»"

# Opties van de activeren-vraag waar de regels voor het einde naar verwijzen.
OPTIE_NIETS = "Nog niets"
BEELD_OPTIES = ("Een foto", "Een screenshot")

FALLBACK = {
    "moment": "Dinsdag, net voor de middag",
    "aanleiding": "Een collega vraagt dringend om een samenvatting van een document, "
                  "en je hebt geen tijd om het helemaal te lezen.",
    "beeld": "een foto van het document op je bureau",
    "beeldwoord": "foto",
    "vraag": "Vat dit samen in vijf punten",
    "betrokkene": "de klant uit het document",
    "herkenbare_details": "Een naam, een adres, een paar bedragen en in de hoek je eigen notities.",
    "categorieen": ["persoonsgegevens", "bedrijfsgevoelig"],
    "inzet": "het vertrouwen van die klant en de reputatie van je organisatie",
    "plek": "de gang op het werk",
    "minimaliseer": "neem alleen over wat nodig is, zonder namen of bedragen",
}


# --- Normalisatie en validatie ---

def normaliseer(ruw):
    """Trim, verwijder overbodige leestekens en vul de categorieën aan.
    Geeft None terug als de invoer geen object is."""
    if not isinstance(ruw, dict):
        return None
    velden = {}
    for sleutel, waarde in ruw.items():
        if isinstance(waarde, str):
            waarde = waarde.strip()
            if sleutel in ZONDER_PUNT:
                waarde = waarde.rstrip(".").rstrip()
            if sleutel == "vraag":
                waarde = waarde.strip(AANHALINGSTEKENS).strip()
            if sleutel == "beeldwoord":
                waarde = waarde.lower()
        velden[sleutel] = waarde

    categorieen = velden.get("categorieen")
    if isinstance(categorieen, list) and all(isinstance(c, str) for c in categorieen):
        gekozen = {c.strip() for c in categorieen}
        # De zinnen voor bijzondere gegevens ("bovendien") en beroepsgeheim
        # ("En wie …") veronderstellen een voorgaande zin.
        if "bijzondere_persoonsgegevens" in gekozen:
            gekozen.add("persoonsgegevens")
        if gekozen & set(CATEGORIEEN) and _eerste_categorie(gekozen) == "beroepsgeheim":
            gekozen.add("persoonsgegevens")
        bekend = [c for c in CATEGORIEEN if c in gekozen]
        onbekend = sorted(gekozen - set(CATEGORIEEN))
        velden["categorieen"] = bekend + onbekend
    return velden


def _eerste_categorie(gekozen):
    return next((c for c in CATEGORIEEN if c in gekozen), None)


def _bevat_woord(tekst, woord):
    return re.search(rf"(?<!\w){re.escape(woord)}(?!\w)", tekst, re.IGNORECASE) is not None


def valideer(velden, profiel):
    """True als de (genormaliseerde) verhaalvelden aan alle regels van §5.2 voldoen."""
    if not isinstance(velden, dict) or set(velden) != VELDEN:
        return False
    for sleutel, limiet in LIMIETEN.items():
        waarde = velden[sleutel]
        if not isinstance(waarde, str) or not waarde or len(waarde) > limiet:
            return False
        if "\n" in waarde or "\r" in waarde or VERBODEN_TEKENS & set(waarde):
            return False
    if velden["beeldwoord"] not in BEELDWOORDEN:
        return False
    categorieen = velden["categorieen"]
    if not isinstance(categorieen, list) or not categorieen:
        return False
    if any(c not in CATEGORIEEN for c in categorieen):
        return False
    if any(not velden[s].endswith((".", "!", "?")) for s in MET_SLOTTEKEN):
        return False
    if not velden["beeld"].startswith("een "):
        return False

    # De betrokkene is altijd verzonnen: nooit (een deel van) de naam van de gebruiker.
    naam = (profiel.get("naam") or "").strip()
    if naam:
        delen = [naam] + [d for d in re.findall(r"\w+", naam) if len(d) >= 3]
        if any(_bevat_woord(velden["betrokkene"], d) for d in delen):
            return False

    betrokkene = set(re.findall(r"\w+", velden["betrokkene"].lower()))
    if betrokkene <= VERBODEN_BETROKKENEN:
        return False

    plekwoorden = set(re.findall(r"\w+", velden["plek"].lower()))
    if plekwoorden & VERBODEN_PLEKWOORDEN:
        return False
    return True


# --- Afgeleide velden ---

def gedeelde_opties(activeren):
    """De gekozen opties van de activeren-vraag; 'Nog niets' telt niet mee naast andere."""
    gedeeld = list((activeren or {}).get("gedeeld") or [])
    if len(gedeeld) > 1 and OPTIE_NIETS in gedeeld:
        gedeeld.remove(OPTIE_NIETS)
    return gedeeld


def opsomming(items):
    """['a', 'b', 'c'] -> 'a, b en c'."""
    if len(items) <= 1:
        return "".join(items)
    return f"{', '.join(items[:-1])} en {items[-1]}"


def klein(tekst):
    return tekst[:1].lower() + tekst[1:]


def eigen_gedrag_zin(activeren, module):
    """De zin in het einde die terugverwijst naar het antwoord uit stap 1 (§6.3)."""
    zinnen = module["einde_eigen_gedrag"]
    gedeeld = gedeelde_opties(activeren)
    if not gedeeld:
        return ""
    if gedeeld == [OPTIE_NIETS]:
        return zinnen["niets"].strip()
    if any(o in BEELD_OPTIES for o in gedeeld):
        zin = zinnen["beeld"].strip()
    else:
        zin = zinnen["andere"].strip().format(gedeeld=opsomming([klein(o) for o in gedeeld]))
    if (activeren or {}).get("gevoelig") == "Ja":
        zin += zinnen["met_gevoelig"].rstrip()
    return zin


def afgeleid(velden, module, activeren):
    zinnen = module["categorie_zinnen"]
    return {
        "moment_klein": klein(velden["moment"]),
        "categorie_zinnen": " ".join(
            zinnen[c].strip() for c in CATEGORIEEN if c in velden["categorieen"]
        ),
        "eigen_gedrag_zin": eigen_gedrag_zin(activeren, module),
    }


# --- Generatie ---

def verhaal_hash(profiel):
    sleutel = [profiel.get("werk") or "", profiel.get("intro") or "", profiel.get("kennisniveau") or ""]
    return hashlib.sha256(json.dumps(sleutel, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


def _prompt(profiel):
    # Per voorbeeld het werk als losse regel en daaronder alleen de velden, zodat
    # het model niet de vorm {"werk": …, "velden": …} overneemt.
    voorbeelden = "\n".join(
        f"Werk: {v['werk']}\n{json.dumps(v['velden'], ensure_ascii=False)}"
        for v in content.load_voorbeelden()
    )
    return content.load_prompt("verhaalvelden").format(
        werk=profiel.get("werk") or "onbekend",
        intro=profiel.get("intro") or "geen toelichting gegeven",
        kennisniveau=profiel.get("kennisniveau") or "onbekend",
        voorbeelden=voorbeelden,
    )


def _parse_json(tekst):
    """Haal het JSON-object uit het antwoord, ook als er tekst of codehekjes rond staan."""
    begin, einde = tekst.find("{"), tekst.rfind("}")
    if begin == -1 or einde <= begin:
        raise ValueError("Geen JSON-object in het antwoord.")
    data = json.loads(tekst[begin:einde + 1])
    # Soms verpakt het model de velden zoals in de voorbeelden: {"werk": …, "velden": {…}}.
    if isinstance(data, dict) and isinstance(data.get("velden"), dict):
        data = data["velden"]
    return data


def genereer(profiel):
    """Genereer en valideer de verhaalvelden; de fallback bij elk probleem."""
    if not (profiel.get("werk") or profiel.get("intro")):
        return dict(FALLBACK)
    if not llm.available():
        log.info("Verhaalvelden: geen API-key, fallback gebruikt.")
        return dict(FALLBACK)
    try:
        tekst = llm.complete(
            _prompt(profiel),
            [{"role": "user", "content": "Geef het JSON-object."}],
            json_mode=True,
        )
        velden = normaliseer(_parse_json(tekst))
    except (llm.LLMError, ValueError) as fout:
        log.warning("Verhaalvelden: generatie mislukt (%s), fallback gebruikt.", fout)
        return dict(FALLBACK)
    if not valideer(velden, profiel):
        log.warning("Verhaalvelden: validatie mislukt, fallback gebruikt: %r", velden)
        return dict(FALLBACK)
    return velden


def _basisvelden(profiel):
    """Gecachete verhaalvelden per profiel (ook de fallback, zodat een mislukte
    call niet bij elke rerun opnieuw geprobeerd wordt)."""
    cache = st.session_state.setdefault("verhaal_cache", {})
    sleutel = verhaal_hash(profiel)
    if sleutel not in cache:
        with st.spinner("We maken je verhaal klaar…"):
            cache[sleutel] = genereer(profiel)
    velden = cache[sleutel]
    # De naam zit niet in de cachesleutel; een gewijzigde naam mag niet als betrokkene opduiken.
    return velden if valideer(velden, profiel) else dict(FALLBACK)


def velden(profiel):
    """De verhaalvelden inclusief afgeleide velden, met het actuele activeren-antwoord."""
    basis = _basisvelden(profiel)
    activeren = st.session_state.get("activeren_antwoord")
    return {**basis, **afgeleid(basis, content.load_module(), activeren)}


# --- Invullen ---

class _MetFallback(dict):
    def __missing__(self, sleutel):
        log.warning("Verhaalveld '%s' ontbreekt; fallback ingevuld.", sleutel)
        return FALLBACK.get(sleutel, "")


def vul_in(template, velden):
    """Vul een skelet in; een ontbrekend veld valt terug op de fallback, nooit een crash."""
    try:
        tekst = template.format_map(_MetFallback(velden))
    except (ValueError, IndexError) as fout:
        log.error("Skelet niet invulbaar (%s): %r", fout, template)
        tekst = template
    # Een lege alinea (bv. zonder eigen_gedrag_zin) laat geen gat achter.
    return re.sub(r"\n{3,}", "\n\n", tekst).strip()


def vul_stappen(stappen, velden):
    """Kopieën van de stappen met ingevulde titel, verhaal en einde."""
    ingevuld = []
    for stap in stappen:
        kopie = dict(stap)
        for veld in ("titel", "verhaal", "einde"):
            if kopie.get(veld):
                kopie[veld] = vul_in(kopie[veld], velden)
        ingevuld.append(kopie)
    return ingevuld


def verhaalblok(velden):
    """De beschrijving van de scène voor in het basisblok van de prompts."""
    return (
        f"Verhaal van de gebruiker: {velden['moment']}. De gebruiker uploadt "
        f"{velden['beeld']} in een gratis AI-tool met de vraag '{velden['vraag']}'. "
        f"De gegevens zijn van {velden['betrokkene']}."
    )
