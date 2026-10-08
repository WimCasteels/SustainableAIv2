# Elke prompt is een potentieel datalek

Adaptieve leerapp van het PWO Sustainable AI. In een kwartier leer je wat er
gebeurt met wat je in een AI-tool zet, hoe je gevoelige data herkent in tekst
en beeld, en hoe je in je eigen werk de veilige keuze maakt.

De training is één module van zes stappen, opgebouwd als één doorlopend
verhaal (hook → why → what → how → toepassing → einde). Een taalmodel past het
verhaal en de teksten aan het werk en het kennisniveau van de gebruiker aan;
een AI-coach begeleidt in een chatpaneel.

## Documentatie

- [docs/inhoud-aanpassen.md](docs/inhoud-aanpassen.md): voor de inhoudseigenaar.
  Teksten, invulvelden, quiz, prompts en afbeeldingen aanpassen zonder code.
- [docs/ontwikkelaars.md](docs/ontwikkelaars.md): voor ontwikkelaars.
  Architectuur, sessiestatus, LLM-calls en fallbacks, validatie, tests, uitbreiden
  en deployen.
- [design-document-v3.md](design-document-v3.md): het functionele ontwerp.

## Lokaal starten

```bash
pip install -r requirements.txt
streamlit run slides-app.py
```

Zonder API-key werkt de hele training ook: dan zie je het standaardverhaal en
de standaardteksten, en is de AI-coach uitgeschakeld.

## Configuratie

| Instelling | Waar | Betekenis |
|---|---|---|
| `OPEN_ROUTER_API` | `.streamlit/secrets.toml` (of omgevingsvariabele) | API-key voor OpenRouter |
| `LLM_BASE_URL` | omgevingsvariabele | Basis-URL van de API (standaard `https://openrouter.ai/api/v1`) |
| `LLM_MODEL` | omgevingsvariabele | Model (standaard `mistralai/mistral-medium-3-5`) |

Voorbeeld van `.streamlit/secrets.toml` (staat in `.gitignore`):

```toml
OPEN_ROUTER_API = "sk-or-..."
```

## Structuur

| Pad | Inhoud |
|---|---|
| `slides-app.py` | Routing en layout (hoofdbestand voor Streamlit Community Cloud) |
| `intake.py` | Profielvragen en transparantietekst |
| `verhaal.py` | Verhaalvelden: genereren, valideren, fallback en invullen |
| `slides.py` | Weergave van een stap, activeren-vragen en navigatie |
| `personalize.py` | Gepersonaliseerde contextteksten |
| `quiz.py` | Quiz, herhaling bij een lage score en het einde |
| `chat.py` | AI-coach |
| `llm.py` | Koppeling met het taalmodel |
| `content/module.yaml` | De module: verhaalskeletten, contextteksten, quiz en einde |
| `content/verhaal-voorbeelden.yaml` | Voorbeelden van verhaalvelden voor de prompt |
| `content/prompts/` | Prompt-templates |
| `images/` | Illustraties per stap |
| `docs/` | Handleidingen voor de inhoudseigenaar en voor ontwikkelaars |
| `tests/` | Automatische tests (pytest) |
| `archief/` | Inhoud van versie 0 en 2 (niet meer gebruikt) |

De inhoud in `content/` (YAML en prompts) wordt bij het opstarten gevalideerd.
Een fout (bv. een invulveld dat niet bestaat) geeft een duidelijke melding in de
app. Herstart de app na een wijziging aan de inhoud. Meer uitleg staat in
[docs/inhoud-aanpassen.md](docs/inhoud-aanpassen.md).

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

De tests hebben geen API-key nodig; LLM-calls worden gemockt.
