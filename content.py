"""Contentmodel: laden en valideren van de module-YAML, de verhaalvoorbeelden en de prompt-templates."""

import functools
import hashlib
import json
import re
from pathlib import Path

import yaml

import verhaal

CONTENT_DIR = Path(__file__).parent / "content"
PROMPTS_DIR = CONTENT_DIR / "prompts"
IMAGES_DIR = Path(__file__).parent / "images"
MODULE_PAD = CONTENT_DIR / "module.yaml"

TYPE_LABELS = {
    "activeren": "Activeren",
    "kern": "Kern",
    "verdieping": "Verdieping",
    "toepassing": "Toepassing",
    "quiz_verankering": "Quiz & verankering",
}

MODULE_NR = 1
MODULES = {
    MODULE_NR: {
        "titel": "Van upload tot datalek",
        "modeldoel": "Je kan uitleggen wat er gebeurt met data die je in een AI-tool zet, "
                     "gevoelige data herkennen in tekst én beeld, en in je eigen werk de "
                     "veilige keuze maken.",
    },
}

# Eén doorlopend verhaal: (staptype, rol) per stap.
STRAMIEN = [
    ("activeren", "hook"),
    ("kern", "why"),
    ("kern", "what"),
    ("verdieping", "how"),
    ("toepassing", "toepassing"),
    ("quiz_verankering", "einde"),
]

VERPLICHTE_VELDEN = ["module", "stap", "type", "rol", "titel", "leerdoel", "niveau"]
EIGEN_GEDRAG_VARIANTEN = ["beeld", "andere", "niets", "met_gevoelig"]


@functools.lru_cache(maxsize=None)
def load_module(pad=MODULE_PAD):
    """Laad en valideer de module-YAML. Raise ValueError bij contentfouten."""
    pad = Path(pad)
    if not pad.exists():
        raise ValueError(f"Contentbestand ontbreekt: {pad.name}")
    with open(pad, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    _valideer_module(pad.name, data)
    return data


def _valideer_module(bestand, data):
    if not isinstance(data, dict):
        raise ValueError(f"{bestand}: de module is een mapping met 'stappen', "
                         "'categorie_zinnen' en 'einde_eigen_gedrag'.")
    for sleutel in ["stappen", "categorie_zinnen", "einde_eigen_gedrag"]:
        if sleutel not in data:
            raise ValueError(f"{bestand}: sleutel '{sleutel}' ontbreekt.")

    zinnen = data["categorie_zinnen"]
    if not isinstance(zinnen, dict) or set(zinnen) != set(verhaal.CATEGORIEEN):
        raise ValueError(f"{bestand}: 'categorie_zinnen' bevat exact de categorieën "
                         f"{', '.join(verhaal.CATEGORIEEN)}.")
    eigen = data["einde_eigen_gedrag"]
    if not isinstance(eigen, dict) or set(eigen) != set(EIGEN_GEDRAG_VARIANTEN):
        raise ValueError(f"{bestand}: 'einde_eigen_gedrag' bevat exact "
                         f"{', '.join(EIGEN_GEDRAG_VARIANTEN)}.")

    stappen = data["stappen"]
    if not isinstance(stappen, list) or len(stappen) != len(STRAMIEN):
        raise ValueError(f"{bestand}: de module heeft exact {len(STRAMIEN)} stappen.")
    for i, stap in enumerate(stappen):
        _valideer_stap(f"{bestand}, stap {i + 1}", i, stap)

    _valideer_skeletten(bestand, data)


def _valideer_stap(plek, i, stap):
    for veld in VERPLICHTE_VELDEN:
        if veld not in stap or stap[veld] in (None, ""):
            raise ValueError(f"{plek}: verplicht veld '{veld}' ontbreekt.")
    if stap["module"] != MODULE_NR:
        raise ValueError(f"{plek}: modulenummer klopt niet ({stap['module']}).")
    if stap["stap"] != i + 1:
        raise ValueError(f"{plek}: stapnummer klopt niet ({stap['stap']}).")
    if (stap["type"], stap["rol"]) != STRAMIEN[i]:
        raise ValueError(
            f"{plek}: type/rol '{stap['type']}/{stap['rol']}' past niet in het stramien "
            f"(verwacht '{STRAMIEN[i][0]}/{STRAMIEN[i][1]}')."
        )
    if not stap.get("verhaal"):
        raise ValueError(f"{plek}: veld 'verhaal' ontbreekt.")
    if i > 0 and not stap.get("context"):
        raise ValueError(f"{plek}: veld 'context' ontbreekt.")

    if stap["type"] == "activeren":
        _valideer_activeren(plek, stap.get("activeren"))
    if stap["type"] == "toepassing" and not stap.get("interactie"):
        raise ValueError(f"{plek}: een toepassingsstap vereist het veld 'interactie'.")
    if stap["type"] == "quiz_verankering":
        quiz = stap.get("quiz")
        if not isinstance(quiz, list) or len(quiz) != 3:
            raise ValueError(f"{plek}: de quiz vereist exact drie vragen.")
        for j, vraag in enumerate(quiz):
            for veld in ["vraag", "opties", "correct", "feedback_basis"]:
                if veld not in vraag:
                    raise ValueError(f"{plek}, vraag {j + 1}: veld '{veld}' ontbreekt.")
            if not 0 <= vraag["correct"] < len(vraag["opties"]):
                raise ValueError(f"{plek}, vraag {j + 1}: 'correct' verwijst niet naar een optie.")
        if not stap.get("einde"):
            raise ValueError(f"{plek}: veld 'einde' ontbreekt.")


def _valideer_activeren(plek, blok):
    if not isinstance(blok, dict):
        raise ValueError(f"{plek}: de activeren-stap vereist een blok 'activeren'.")
    for veld in ["vraag", "opties", "vervolgvraag", "vervolgopties"]:
        if not blok.get(veld):
            raise ValueError(f"{plek}: 'activeren' mist het veld '{veld}'.")
    # De regels voor het einde (§6.3) verwijzen naar deze opties.
    nodig = [verhaal.OPTIE_NIETS, *verhaal.BEELD_OPTIES]
    ontbrekend = [o for o in nodig if o not in blok["opties"]]
    if ontbrekend:
        raise ValueError(f"{plek}: 'activeren.opties' mist {', '.join(ontbrekend)}.")
    if "Ja" not in blok["vervolgopties"]:
        raise ValueError(f"{plek}: 'activeren.vervolgopties' mist 'Ja'.")


def _valideer_skeletten(bestand, data):
    """Elk skelet moet invulbaar zijn met de fallbackvelden plus de afgeleide velden."""
    testantwoord = {"gedeeld": ["Code"], "gevoelig": "Ja"}
    velden = {**verhaal.FALLBACK, **verhaal.afgeleid(verhaal.FALLBACK, data, testantwoord)}
    for stap in data["stappen"]:
        for veld in ["titel", "verhaal", "einde"]:
            if not stap.get(veld):
                continue
            try:
                stap[veld].format_map(velden)
            except (KeyError, ValueError, IndexError) as fout:
                raise ValueError(
                    f"{bestand}, stap {stap['stap']}: '{veld}' is niet invulbaar ({fout!r})."
                ) from fout
    for variant, zin in data["einde_eigen_gedrag"].items():
        try:
            zin.format(gedeeld="code")
        except (KeyError, ValueError, IndexError) as fout:
            raise ValueError(
                f"{bestand}: einde_eigen_gedrag.{variant} is niet invulbaar ({fout!r})."
            ) from fout


@functools.lru_cache(maxsize=None)
def load_voorbeelden():
    with open(CONTENT_DIR / "verhaal-voorbeelden.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompt(naam):
    with open(PROMPTS_DIR / f"{naam}.txt", encoding="utf-8") as f:
        return f.read()


def image_path(stap):
    """Pad naar de illustratie van een stap, of None als die (nog) niet bestaat."""
    naam = stap.get("image")
    if not naam:
        return None
    pad = IMAGES_DIR / naam
    return pad if pad.exists() else None


def basisblok(profiel, velden):
    """Vul het gedeelde basisblok in met het gebruikersprofiel en het verhaal."""
    return load_prompt("basis").format(
        naam=profiel.get("naam") or "onbekend",
        kennisniveau=profiel.get("kennisniveau", "onbekend"),
        gevoelige_data=profiel.get("gevoelige_data", "onbekend"),
        werk=profiel.get("werk") or "onbekend",
        intro=profiel.get("intro") or "geen toelichting gegeven",
        verhaalblok=verhaal.verhaalblok(velden),
    )


def strip_html(tekst):
    return re.sub(r"<[^>]+>", " ", tekst or "").strip()


def stap_inhoud(stap):
    """Beknopte tekstweergave van een (ingevulde) stap, als context voor de chat-agent."""
    delen = [
        f"Titel: {stap['titel']}",
        f"Leerdoel: {stap['leerdoel']}",
    ]
    if stap.get("verhaal"):
        delen.append(f"Verhaal: {stap['verhaal'].strip()}")
    if stap.get("content"):
        delen.append(f"Vaste inhoud: {strip_html(stap['content'])}")
    if stap.get("context"):
        delen.append(f"Tekst: {stap['context'].strip()}")
    return "\n".join(delen)


def module_samenvatting(stappen):
    regels = []
    for stap in stappen:
        regels.append(
            f"Stap {stap['stap']} ({TYPE_LABELS[stap['type']]}): {stap['titel']} — {stap['leerdoel']}"
        )
    return "\n".join(regels)


def profiel_hash(profiel):
    data = json.dumps(profiel, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]
