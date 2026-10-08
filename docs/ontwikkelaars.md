# Technische documentatie

Voor ontwikkelaars die de app onderhouden of uitbreiden. Voor installatie en
lokaal starten: zie de [README](../README.md). Voor de functionele keuzes: zie
[design-document-v3.md](../design-document-v3.md). Voor het aanpassen van de
inhoud: zie [inhoud-aanpassen.md](inhoud-aanpassen.md).

---

## 1. Overzicht

Een Streamlit-app met één module van zes stappen. Ze is opgebouwd uit drie
lagen:

1. **Vaste inhoud** in YAML (`content/module.yaml`): verhaalskeletten met
   invulvelden, contextteksten, quiz en einde.
2. **Verhaalvelden** (`verhaal.py`): één niet-streamende LLM-call per profiel.
   Die levert een klein JSON-object op (moment, beeld, betrokkene, …) dat streng
   gevalideerd wordt en de skeletten invult. Bij elk probleem valt de app terug
   op een vaste set.
3. **Gepersonaliseerde tekst** (`personalize.py`, `quiz.py`, `chat.py`):
   streamende LLM-calls die contextteksten herschrijven, quizfeedback geven en de
   AI-coach aansturen. Elke call heeft een fallback naar de vaste tekst.

De hele training werkt zonder API-key.

### Modules

| Bestand | Verantwoordelijkheid |
|---|---|
| `slides-app.py` | Entrypoint: CSS, inhoud laden en valideren, routing (`intake` / `module`), verhaalvelden ophalen, layout met slides links en chat rechts |
| `intake.py` | Profielformulier, transparantietekst, reset van de sessiestatus bij een nieuw profiel |
| `content.py` | Laden en valideren van `module.yaml` en de prompts, `basisblok()`, hulpfuncties voor de chatcontext |
| `verhaal.py` | Verhaalvelden: prompt, generatie, normalisatie, validatie, fallback, afgeleide velden, `vul_in()` |
| `slides.py` | Weergave van één stap, activeren-vragen (stap 1), navigatie, "Opnieuw beginnen" |
| `personalize.py` | Verhaalbox, contexttekst (gepersonaliseerd of origineel), streaming met nette afhandeling van fouten |
| `quiz.py` | Quiz met geschudde opties, feedback, herhaling bij een lage score, einde |
| `chat.py` | AI-coach: systeemprompt, opening in stap 5, beurtenlimiet, geschiedenis |
| `llm.py` | OpenAI-compatibele client naar OpenRouter: `stream()`, `complete()`, `LLMError` |

`content` en `verhaal` importeren elkaar. Dat werkt omdat geen van beide bij het
importeren attributen van de ander gebruikt. Gebruik daarom altijd `import x`,
nooit `from x import …` tussen deze twee.

---

## 2. Verloop van één run

Streamlit voert `slides-app.py` bij elke interactie opnieuw uit:

```
slides-app.py
├─ content.load_module()        # YAML laden en valideren (lru_cache: één keer per proces)
├─ content.valideer_prompts()   # prompts controleren op bekende invulvelden (lru_cache)
├─ pagina == "intake"? ─► intake.render_intake(); st.stop()
├─ knop "Profiel aanpassen"
├─ velden = verhaal.velden(profiel)               # gecachet per profiel; spinner bij de eerste keer
├─ stappen = verhaal.vul_stappen(stappen, velden) # titel, verhaal en einde ingevuld
├─ kolom links:  slides.render_stap(stappen, profiel, velden)
│                 ├─ verhaalbox (personalize.toon_verhaal)
│                 ├─ stap 1: activeren-vragen
│                 ├─ stap 2–5: personalize.render_context
│                 └─ stap 6: quiz.render_quiz (+ einde)
└─ kolom rechts: chat.render_chat(huidige_stap, stappen, profiel, velden)
```

**Belangrijk**
- **Alles ná `vul_stappen()` werkt met de ingevulde stappen.** Titels als
  "Wat staat er op die {beeldwoord}?" zijn dan al ingevuld, ook in de prompts
  voor de chat en de personalisatie. Geef nooit `MODULE["stappen"]` rechtstreeks
  door aan rendering of prompts.
- **De inhoud wordt één keer per proces geladen** (`functools.lru_cache`). Na een
  wijziging aan `module.yaml` of een prompt moet je de app herstarten.

---

## 3. Sessiestatus

Alles staat in `st.session_state` en verdwijnt met de sessie. Er is geen
persistente opslag.

| Sleutel | Inhoud | Gezet door | Gewist bij nieuw profiel | Gewist bij "Opnieuw beginnen" |
|---|---|---|---|---|
| `pagina` | `"intake"` of `"module"` | app, intake | — | — |
| `profiel` | dict: `naam`, `kennisniveau`, `gevoelige_data`, `werk`, `intro` | intake | overschreven | nee |
| `stap_idx` | 0–5 | slides | → 0 | → 0 |
| `verhaal_cache` | `{verhaal_hash: velden}` | verhaal | ja | nee |
| `pers_cache` | `{(profiel_hash, module, stap): tekst}` | personalize | ja | nee |
| `activeren_antwoord` | `{"gedeeld": [...], "gevoelig": str \| None}` | slides (callbacks) | ja | **nee** (bewust) |
| `activeren_gedeeld`, `activeren_gevoelig` | widgetstatus van de pills en de radio | Streamlit | ja | nee |
| `quiz_1` | `antwoorden`, `feedback`, `volgorde`, `wacht_op_verder`, `samenvatting` | quiz | ja | ja |
| `quizkeuze_1_<i>` | widgetstatus van de radio per vraag | Streamlit | ja | ja |
| `chat_geschiedenis` | lijst berichten (zie §6) | chat | ja | ja |
| `chat_beurten` | aantal berichten van de gebruiker | chat | ja | ja |
| `chat_geopend` | stappen waarvoor de coach al opende | chat | ja | ja |

**`profiel` bevat de activeren-antwoorden niet.** Zo veroorzaakt een gewijzigd
antwoord in stap 1 geen nieuwe personalisatie: `profiel_hash` blijft gelijk en de
gecachete teksten blijven geldig.

**Widgetstatus van stap 1.** Streamlit wist de status van widgets die in een run
niet getoond worden. Daarom:
- `activeren_antwoord` is de bron van waarheid;
- de widgets krijgen hun beginwaarde (`default`/`index`) daaruit;
- `on_change`-callbacks werken `activeren_antwoord` bij vóór de run.

Zonder dat zou terugbladeren naar stap 1 de keuzes leegmaken. Door de callbacks
gebruikt dezelfde run ook meteen het nieuwe antwoord.

---

## 4. LLM-calls

| Waar | Functie | Soort | Cache | Fallback |
|---|---|---|---|---|
| Verhaalvelden (eerste weergave na de intake) | `verhaal.genereer` | `llm.complete`, JSON-modus, timeout 15 s, geen retry | `verhaal_cache`, ook de fallback | `verhaal.FALLBACK` |
| Contexttekst stap 2–4 | `personalize.render_context` | `llm.stream` | `pers_cache` | originele `context` |
| Feedback per quizvraag | `quiz._toon_vraag` | `llm.stream` | in `quiz_1["feedback"]` | `feedback_basis` |
| Herhaling bij score ≤ 1 | `quiz._toon_herhaling` | `llm.stream` | in `quiz_1["samenvatting"]` | `feedback_basis` van de gemiste vragen |
| AI-coach | `chat.render_chat` | `llm.stream` | geschiedenis | vaste melding, niet doorgestuurd (zie §6) |

**Configuratie** (`llm.py`)
- Basis-URL en model komen uit `LLM_BASE_URL` en `LLM_MODEL`.
- `EXTRA_BODY` zet de routing van OpenRouter vast op Mistral, zonder fallbacks
  naar andere providers en zonder datacollectie.
- `stream()` gebruikt timeout 30 s en 1 retry.

**Geen API-key**
- `llm.available()` is dan `False`.
- Elke laag toont de vaste tekst.
- `verhaal.genereer` doet geen call, en ook geen als `werk` en `intro` allebei
  leeg zijn.

**Fouten tijdens het streamen**
- `personalize.stream_tekst()` streamt in een `st.empty()`-placeholder.
- Bij een fout halverwege, of een leeg antwoord, wordt die placeholder geleegd en
  gaat de exception naar de aanroeper, die de vaste tekst toont. Zo blijft er
  nooit een halve tekst boven de originele staan (bugfix 10.2).

**JSON-modus**
- `complete(json_mode=True)` stuurt `response_format={"type": "json_object"}` mee.
- `verhaal._parse_json` neemt hoe dan ook alles van de eerste `{` tot de laatste
  `}`, zodat codehekjes of inleidende tekst niet storen.
- Als de JSON-modus via OpenRouter niet blijkt te werken (open punt §13.5 van het
  design document), volstaat het `json_mode=False` door te geven in
  `verhaal.genereer`.

---

## 5. Verhaalvelden: validatie en veiligheid

LLM-output komt via de verhaalvelden letterlijk in de UI terecht. Daarom gaan de
velden door twee filters.

**Normalisatie** (`verhaal.normaliseer`)
- witruimte trimmen;
- de afsluitende punt weghalen bij `moment`, `beeld`, `inzet`, `plek`,
  `minimaliseer` en `betrokkene`;
- aanhalingstekens rond `vraag` weghalen;
- `beeldwoord` in kleine letters;
- de categorieën in de vaste volgorde zetten;
- `persoonsgegevens` toevoegen als `bijzondere_persoonsgegevens` gekozen is, of
  als `beroepsgeheim` anders de eerste categorie zou zijn. De vaste zinnen
  daarvan veronderstellen een voorgaande zin.

**Validatie** (`verhaal.valideer`) verwerpt de velden als:
- er een veld ontbreekt of te veel is;
- een veld te lang is (`LIMIETEN`);
- een veld een regeleinde bevat;
- een van de tekens `{ } < > * _ \` # [ ] $ ~` voorkomt (`$` en `~` omdat
  `st.markdown` die als wiskunde of doorhaling rendert);
- `beeldwoord` niet `foto`, `scan` of `screenshot` is;
- er onbekende categorieën zijn;
- de slotleestekens ontbreken;
- `beeld` niet met "een " begint;
- `betrokkene` de naam van de gebruiker bevat. De vergelijking gebeurt **als heel
  woord**, op de volledige naam en op elk naamdeel van minstens 3 tekens. Zo
  blokkeert "An" niet "je klanten".
- `plek` "je", "jouw", "mijn", "ons" of "onze" als woord bevat.

De naam zit niet in de cachesleutel. `verhaal._basisvelden` valideert daarom
gecachete velden opnieuw tegen het actuele profiel.

**Weergave**
- Verhaaltekst gaat door `st.markdown` **zonder** `unsafe_allow_html`.
- Titels gaan via `html.escape` in een HTML-wrapper.
- Waar `unsafe_allow_html=True` wel gebruikt wordt (CSS, `content`-blokken uit
  de YAML), staat alleen tekst van de inhoudseigenaar, nooit LLM-output.

**Prompt-injectie**
- Profieltekst (`werk`, `intro`) staat in de prompts expliciet gemarkeerd als
  informatie, niet als instructie.
- Bij de verhaalvelden vangt de strenge validatie de rest op: een gedicht of
  andere afwijkende output past niet in het schema en levert de fallback op.

**Invullen**
- `verhaal.vul_in()` gebruikt `format_map` met een dict die ontbrekende sleutels
  aanvult uit `FALLBACK`. Een ontbrekend veld geeft dus nooit een `KeyError`.
- Accolades ín waarden worden niet opnieuw geïnterpreteerd.
- Drie of meer opeenvolgende regeleindes worden er twee (een lege
  `eigen_gedrag_zin`).

---

## 6. Chatgeschiedenis

`chat_geschiedenis` is een lijst `{"role", "content"}`-dicts, eventueel met een
markering:

| Markering | Getoond in de UI | Mee naar de API | Gebruikt voor |
|---|---|---|---|
| — | ja | ja | gewone berichten |
| `verborgen: True` | nee | ja | het startbericht "Start de toepassingsoefening." in stap 5, zodat de geschiedenis altijd met een user-bericht begint (bugfix 10.4) |
| `lokaal: True` | ja | nee | een mislukte beurt (de vraag én de foutmelding), zodat er geen twee user-berichten na elkaar naar de API gaan en de foutmelding geen "assistant"-tekst wordt |

**Doorgeven aan de API**
- `chat._voor_api()` filtert de berichten met `lokaal`.
- `llm._berichten()` stuurt van elk bericht alleen `role` en `content` door.

**Limiet en weergave**
- De limiet `MAX_BEURTEN = 12` geldt voor de hele sessie.
- Het gesprek staat in een container van vaste hoogte (`GESPREK_HOOGTE`) en
  scrolt daarbinnen.

---

## 7. Quiz

**Geschudde opties**
- Per vraag wordt bij de eerste weergave een permutatie bewaard in
  `quiz_1["volgorde"][i]`.
- De radio krijgt die permutatie als `options` en toont de tekst via
  `format_func`. De gekozen waarde is daardoor rechtstreeks de oorspronkelijke
  index: terugrekenen is niet nodig.

**Verloop** (bugfix 10.3)
1. "Bevestig antwoord" genereert de feedback, bewaart antwoord en feedback, zet
   `wacht_op_verder` en doet een `st.rerun()`.
2. De feedback blijft staan tot de gebruiker op "Volgende vraag" (of na de
   laatste vraag "Bekijk je score") klikt.
3. Daarna volgen de score, bij een score ≤ `MAX_SCORE_HERHALING` een herhaling,
   en altijd het einde.

**Herstarten**
- `quiz.reset()` wist de status, de permutaties en de radio-keys.

---

## 8. Inhoudsvalidatie bij het opstarten

`content.load_module()` en `content.valideer_prompts()` geven een `ValueError`
met een leesbare melding. De app toont die als "Contentfout bij het opstarten"
en stopt.

**Wat er gecontroleerd wordt**
- De structuur: een mapping met `stappen`, `categorie_zinnen` en
  `einde_eigen_gedrag`.
- Precies zes stappen volgens `STRAMIEN`, met de verplichte velden en het juiste
  module- en stapnummer.
- `verhaal` in elke stap; `context` in elke stap behalve stap 1.
- Stap 1 heeft een `activeren`-blok met de opties "Nog niets", "Een foto" en
  "Een screenshot" en de vervolgoptie "Ja".
- Stap 5 heeft `interactie`; stap 6 heeft drie quizvragen met een geldige
  `correct` en een `einde`.
- `categorie_zinnen` en `einde_eigen_gedrag` hebben exact de verwachte sleutels.
- Elk skelet (`titel`, `verhaal`, `einde`) is invulbaar met de fallbackvelden
  plus de afgeleide velden. Elke variant van `einde_eigen_gedrag` is invulbaar
  met `{gedeeld}`.
- Elke prompt in `PROMPT_VELDEN` bestaat en gebruikt alleen de toegelaten
  invulvelden.

---

## 9. Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

| Bestand | Wat |
|---|---|
| `tests/test_content.py` | Laden en validatie van de YAML en de prompts, foutmeldingen bij kapotte inhoud |
| `tests/test_verhaal.py` | Normalisatie, validatie (ook naam en plek als heel woord), generatie met gemockte `llm.complete`, afgeleide velden, `vul_in` |
| `tests/test_quiz.py` | Permutaties en score |
| `tests/test_app.py` | `AppTest` zonder API-key: volledige doorloop, herhaling bij een lage score, de "Volgende vraag"-flow, stap 1 bij terugbladeren, intake en "Profiel aanpassen" |
| `tests/test_llm_mock.py` | Bugfix 10.2 (halve stream) en 10.4 (chatgeschiedenis), met een nep-client in plaats van OpenRouter |

**Valkuilen met `AppTest`**
- Na een `st.rerun()` blijven elementen van de vorige run in de elementboom
  staan. Daardoor vind je soms een verouderde knop, of crasht een volgende
  `run()` op de status van een verdwenen widget.
- De hulpfunctie `_klik()` in `test_app.py` doet daarom na elke klik twee runs.
- Tests die in de module beginnen, zetten `profiel` en `pagina` rechtstreeks in
  `session_state` in plaats van via het intakeformulier.
- Dit is een beperking van `AppTest`, niet van de app.

**Handmatig testen**
- De handmatige tests met een echte API-key staan in §12.2 van het design
  document. Die zijn vooral nodig om te zien of de verhaalvelden de validatie
  halen.
- Kijk bij een fallback in de logs: `verhaal.py` logt een waarschuwing met de
  reden en de afgewezen velden.

---

## 10. Uitbreiden

**Een nieuw verhaalveld**
1. Voeg het toe aan `LIMIETEN` in `verhaal.py` (of aan `VELDEN`, als het geen
   vrije tekst is), en aan `FALLBACK`.
2. Pas zo nodig `normaliseer()` en `valideer()` aan.
3. Beschrijf het in `content/prompts/verhaalvelden.txt`.
4. Voeg het toe aan elk voorbeeld in `content/verhaal-voorbeelden.yaml`.
5. Werk de tabel in `docs/inhoud-aanpassen.md` bij.

**Een afgeleid veld** (berekend door de app, niet door het taalmodel)
- Voeg het toe in `verhaal.afgeleid()`.
- De validatie bij het opstarten neemt het automatisch mee.

**Een nieuwe prompt**
- Voeg het bestand toe aan `content/prompts/` en de invulvelden aan
  `content.PROMPT_VELDEN`.

**Een stap toevoegen of het stramien wijzigen**
- Pas `content.STRAMIEN` en `module.yaml` aan.
- Controleer `slides.render_stap` (welke weergave per type), `TYPE_LABELS`, de
  CSS-badges in `slides-app.py` en de tests. Het aantal stappen staat nergens
  anders hardgecodeerd.

**Een ander model of een andere provider**
- Zet `LLM_MODEL` en `LLM_BASE_URL`.
- Pas `EXTRA_BODY` aan. Die is specifiek voor OpenRouter en moet weg bij een
  rechtstreekse koppeling.
- Pas de transparantietekst in `intake.py` aan als de verwerker verandert.

---

## 11. Deployen

**Streamlit Community Cloud**
- Hoofdbestand: `slides-app.py`. Behoud die naam, anders breekt de bestaande
  deployment.
- Secret: `OPEN_ROUTER_API`, in de instellingen van de app (Settings → Secrets).
- `requirements.txt` bevat alleen de runtime-afhankelijkheden. pytest staat in
  `requirements-dev.txt`.

**Na een wijziging aan inhoud of prompts**
- Herstart de app ("Reboot app"), want die worden per proces gecachet.

**Versies**
- De versies zijn vastgezet op `streamlit>=1.55,<2`, `pyyaml>=6,<7` en
  `openai>=1.40,<3`. De tests zijn gedraaid met Streamlit 1.55.
- `st.pills` en `st.container(key=…)` vragen een recente Streamlit-versie.
- De CSS van de verhaalbox richt zich op de klasse `st-key-verhaal_*` die
  Streamlit aan containers met een key geeft. Controleer die na een upgrade van
  Streamlit.
