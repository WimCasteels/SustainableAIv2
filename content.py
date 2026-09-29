"""Contentmodel: laden en valideren van de module-YAML's, sectoren en prompt-templates."""

import hashlib
import json
import re
from pathlib import Path

import yaml

CONTENT_DIR = Path(__file__).parent / "content"
PROMPTS_DIR = CONTENT_DIR / "prompts"
IMAGES_DIR = Path(__file__).parent / "images"

STAP_TYPES = ["activeren", "kern", "verdieping", "toepassing", "quiz_verankering"]

TYPE_LABELS = {
    "activeren": "Activeren",
    "kern": "Kern",
    "verdieping": "Verdieping",
    "toepassing": "Toepassing",
    "quiz_verankering": "Quiz & verankering",
}

# Moduletitels en modeldoelen (uit het leerpadendocument).
MODULES = {
    1: {
        "titel": "Hoe gaan AI-tools om met je data?",
        "modeldoel": "Je kan uitleggen wat er met data gebeurt wanneer je die invoert in een "
                     "AI-tool, en bewust kiezen tussen consumer- en enterprise-versies.",
    },
    2: {
        "titel": "Welke data is gevoelig?",
        "modeldoel": "Je kan gevoelige data herkennen — persoonsgegevens, bijzondere categorieën, "
                     "bedrijfsgevoelige en multimodale data — en beoordelen of iets in een AI-tool thuishoort.",
    },
    3: {
        "titel": "De risico's in de praktijk",
        "modeldoel": "Je kan risico's van AI-gebruik herkennen in concrete situaties en de "
                     "mogelijke impact van een datalek inschatten.",
    },
    4: {
        "titel": "Juridisch kader",
        "modeldoel": "Je kan de belangrijkste regels uit de AVG en de AI Act toepassen om te "
                     "beoordelen of het delen van data met AI-tools toegestaan is.",
    },
    5: {
        "titel": "Veiliger werken met gevoelige data",
        "modeldoel": "Je kan in praktijksituaties veilige keuzes maken: data beschermen, de juiste "
                     "tools kiezen en weten waar je terechtkan bij twijfel.",
    },
}

VERPLICHTE_VELDEN = ["module", "stap", "type", "titel", "leerdoel", "niveau"]


def load_modules():
    """Laad en valideer alle module-YAML's. Raise ValueError bij contentfouten."""
    modules = {}
    for nummer in MODULES:
        pad = CONTENT_DIR / f"module-{nummer}.yaml"
        if not pad.exists():
            raise ValueError(f"Contentbestand ontbreekt: {pad.name}")
        with open(pad, encoding="utf-8") as f:
            stappen = yaml.safe_load(f)
        _valideer_module(nummer, pad.name, stappen)
        modules[nummer] = stappen
    return modules


def _valideer_module(nummer, bestand, stappen):
    if not isinstance(stappen, list) or len(stappen) != 5:
        raise ValueError(f"{bestand}: een module heeft exact vijf stappen.")
    for i, stap in enumerate(stappen):
        plek = f"{bestand}, stap {i + 1}"
        for veld in VERPLICHTE_VELDEN:
            if veld not in stap or stap[veld] in (None, ""):
                raise ValueError(f"{plek}: verplicht veld '{veld}' ontbreekt.")
        if stap["module"] != nummer:
            raise ValueError(f"{plek}: modulenummer klopt niet ({stap['module']}).")
        if stap["stap"] != i + 1:
            raise ValueError(f"{plek}: stapnummer klopt niet ({stap['stap']}).")
        if stap["type"] != STAP_TYPES[i]:
            raise ValueError(
                f"{plek}: type '{stap['type']}' past niet in het stramien (verwacht '{STAP_TYPES[i]}')."
            )
        if not stap.get("context"):
            raise ValueError(f"{plek}: veld 'context' ontbreekt.")
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


def load_sectoren():
    with open(CONTENT_DIR / "sectoren.yaml", encoding="utf-8") as f:
        return {entry["sector"]: entry for entry in yaml.safe_load(f)}


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


def sectorblok(profiel, sectoren):
    """Formatteer de sectorcontext voor in de prompts; leeg bij onbekende sector."""
    entry = sectoren.get(profiel.get("sector_code"))
    if not entry or entry["sector"] == "anders" and not profiel.get("sector"):
        entry = entry or sectoren.get("anders")
    if not entry:
        return ""
    return (
        f"Sectorcontext ({entry['label']}): gevoelige data in deze sector: "
        f"{entry['gevoelige_data'].strip()} Kernrisico: {entry['kernrisico'].strip()} "
        f"Bruikbaar voorbeeld: {entry['voorbeeld'].strip()}"
    )


def basisblok(profiel, sectoren):
    """Vul het gedeelde basisblok in met het gebruikersprofiel."""
    return load_prompt("basis").format(
        naam=profiel.get("naam") or "onbekend",
        kennisniveau=profiel.get("kennisniveau", "onbekend"),
        gevoelige_data=profiel.get("gevoelige_data", "onbekend"),
        sector=profiel.get("sector") or "onbekend",
        intro=profiel.get("intro") or "geen toelichting gegeven",
        sectorblok=sectorblok(profiel, sectoren),
    )


def strip_html(tekst):
    return re.sub(r"<[^>]+>", " ", tekst or "").strip()


def stap_inhoud(stap):
    """Beknopte tekstweergave van een stap, als context voor de chat-agent."""
    delen = [
        f"Titel: {stap['titel']}",
        f"Leerdoel: {stap['leerdoel']}",
    ]
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
