# De inhoud van de training aanpassen

Handleiding voor de inhoudseigenaar. Je kan bijna alles aan de training
aanpassen zonder code te schrijven: de teksten, de quizvragen, de prompts voor
het taalmodel en de afbeeldingen. Deze handleiding legt uit waar alles staat,
wat je vrij kan veranderen en waar je op moet letten.

Voor de achtergrond van de keuzes in de training: zie
[design-document-v3.md](../design-document-v3.md).

---

## 1. Waar staat wat?

| Bestand of map | Wat staat erin | Hoe vaak pas je het aan? |
|---|---|---|
| `content/module.yaml` | Alle teksten van de zes stappen, de quiz en het einde | Meestal hier |
| `content/verhaal-voorbeelden.yaml` | Vier voorbeeldverhalen die het taalmodel als inspiratie krijgt | Af en toe |
| `content/prompts/` | De instructies voor het taalmodel | Zelden, en voorzichtig |
| `images/` | De illustraties per stap | Bij nieuwe beelden |
| `afbeeldingen-prompts.md` | Prompts om nieuwe illustraties te laten maken | Bij nieuwe beelden |

Open de bestanden met een gewone teksteditor, zoals Visual Studio Code of
Kladblok. Gebruik geen Word: Word voegt opmaak toe die het bestand breekt.

---

## 2. Hoe de training werkt: verhaal en context

Elke stap heeft twee soorten tekst. Het verschil is belangrijk, want je past ze
anders aan.

**Verhaaltekst (`verhaal`)**
- Het doorlopende verhaal: iemand zet op het werk een foto in een gratis
  AI-tool, en dat loopt slecht af.
- Je schrijft het verhaal zelf, met **invulvelden** tussen accolades, zoals
  `{moment}` of `{beeld}`.
- Het taalmodel bedenkt per gebruiker een scène bij diens werk en de app vult de
  velden daarmee in. Een verpleegkundige leest dan over "een foto van de wonde
  van mevrouw Peeters", een boekhouder over iets uit de boekhouding.
- De zinnen zelf blijven altijd zoals jij ze schreef: het taalmodel herschrijft
  de verhaaltekst nooit.
- In de app staat het verhaal bovenaan, met een paarse lijn ernaast.

**Contexttekst (`context`)**
- De leerinhoud van een stap: wat de AVG zegt, wat er met je data gebeurt, en zo
  verder.
- In stap 2, 3 en 4 herschrijft het taalmodel deze tekst voor het kennisniveau
  en het werk van de gebruiker. De feiten moet het daarbij letterlijk laten
  staan.
- In stap 5 en 6 wordt de contexttekst niet herschreven.
- Zonder taalmodel ziet de gebruiker jouw tekst zoals je hem schreef.
- In de app staat de contexttekst in een omkaderd vak onder het verhaal.

**Wat betekent dat voor jou?**
- Feiten, cijfers en juridische formuleringen zet je in de **context**.
- Spanning, ritme en wendingen zet je in het **verhaal**.
- Invulvelden werken **alleen** in `titel`, `verhaal` en `einde`, niet in
  `context`, `content` of de quiz.

---

## 3. De invulvelden

Deze velden kan je in `titel`, `verhaal` en `einde` gebruiken. Een veld dat niet
in deze lijst staat, kan niet: de app weigert dan op te starten en zegt welk veld
fout is.

| Veld | Wat komt er te staan | Voorbeeld (verpleegkundige) | Voorbeeld (standaardverhaal) |
|---|---|---|---|
| `{moment}` | Tijdstip en situatie, met hoofdletter, zonder punt | Donderdagavond, laatste ronde | Dinsdag, net voor de middag |
| `{moment_klein}` | Hetzelfde, met kleine letter (voor midden in een zin) | donderdagavond, laatste ronde | dinsdag, net voor de middag |
| `{aanleiding}` | Eén of twee volledige zinnen, met punt | De wonde van mevrouw Peeters ziet er anders uit dan gisteren. De wondverpleegkundige is pas maandag terug. | Een collega vraagt dringend om een samenvatting van een document, en je hebt geen tijd om het helemaal te lezen. |
| `{beeld}` | Begint met "een", zonder punt | een foto van de wonde van mevrouw Peeters | een foto van het document op je bureau |
| `{beeldwoord}` | Altijd "foto", "scan" of "screenshot" | foto | foto |
| `{vraag}` | Wat de gebruiker aan de AI-tool vraagt, zonder aanhalingstekens | Is dit een infectie? | Vat dit samen in vijf punten |
| `{betrokkene}` | Van wie de gegevens zijn (altijd verzonnen) | mevrouw Peeters | de klant uit het document |
| `{herkenbare_details}` | Eén zin over wat er op het beeld te zien is | Een stukje van haar gezicht, haar polsbandje met naam en informatie over haar gezondheid. | Een naam, een adres, een paar bedragen en in de hoek je eigen notities. |
| `{categorie_zinnen}` | De vaste zinnen over de soorten gevoelige data (zie §5) | — | — |
| `{inzet}` | Wat er op het spel staat, zonder punt | het vertrouwen van je patiënt en je beroepsgeheim | het vertrouwen van die klant en de reputatie van je organisatie |
| `{plek}` | Waar op het werk een prikbord hangt | de gang van de afdeling | de gang op het werk |
| `{minimaliseer}` | Een tip om minder te delen, begint met een werkwoord, zonder punt | fotografeer alleen de wonde, zonder gezicht of polsbandje | neem alleen over wat nodig is, zonder namen of bedragen |
| `{eigen_gedrag_zin}` | Een zin over wat de gebruiker in stap 1 aanduidde (zie §6); leeg als die niets aanduidde | — | — |

**Tips voor het schrijven met invulvelden**
- **Lees je zin na met minstens twee voorbeelden uit de tabel.** "Je hebt weer
  `{beeld}` in je hand" moet zowel met "een foto van de wonde" als met "een
  screenshot van het dashboard" kloppen.
- **Let op de leestekens.** `{moment}`, `{beeld}`, `{inzet}`, `{plek}` en
  `{minimaliseer}` eindigen zonder punt; dat zet je zelf. `{aanleiding}` en
  `{herkenbare_details}` zijn volledige zinnen met een punt.
- **Midden in een zin** gebruik je `{moment_klein}`, aan het begin `{moment}`.
- **`{beeldwoord}` is een de-woord** ("de foto", "de scan", "de screenshot"),
  dus schrijf "die {beeldwoord}", niet "dat {beeldwoord}".
- **Een lege alinea verdwijnt vanzelf.** Als `{eigen_gedrag_zin}` leeg is,
  blijft er geen gat in de tekst.

---

## 4. De stappen in `content/module.yaml`

De module heeft altijd **zes stappen** in deze vaste volgorde. Je kan de teksten
vrij aanpassen, maar de volgorde, het `type` en de `rol` van een stap niet.

| Stap | `type` | `rol` | Wat gebeurt er |
|---|---|---|---|
| 1 | `activeren` | `hook` | Het verhaal begint; de gebruiker beantwoordt twee vragen |
| 2 | `kern` | `why` | Wat staat er op het beeld en wat staat er op het spel |
| 3 | `kern` | `what` | Waar gaat het beeld naartoe |
| 4 | `verdieping` | `how` | Een echt incident |
| 5 | `toepassing` | `toepassing` | De AI-coach herneemt het verhaal; de gebruiker oefent |
| 6 | `quiz_verankering` | `einde` | Quiz, en daarna het einde van het verhaal |

### Velden per stap

| Veld | Verplicht | Wat |
|---|---|---|
| `module`, `stap` | ja | Altijd `1` en het stapnummer (1 tot 6). Niet aanpassen. |
| `type`, `rol` | ja | Zie de tabel hierboven. Niet aanpassen. |
| `titel` | ja | De titel bovenaan. Invulvelden mogen. |
| `leerdoel` | ja | Staat in de uitklapper "Leerdoel en extra info" en gaat mee naar de AI-coach. |
| `niveau` | ja | Het niveau van het leerdoel (bv. "kennen & begrijpen"). |
| `image` | nee | Bestandsnaam van de illustratie in `images/`. Bestaat het bestand niet, dan wordt er gewoon geen afbeelding getoond. |
| `verhaal` | ja | De verhaaltekst, met invulvelden. |
| `context` | ja, behalve stap 1 | De leerinhoud. Geen invulvelden. |
| `content` | nee | Een visueel blok in HTML (kolommen, een stroomschema, een waarschuwing). |
| `content_zichtbaar` | nee | `true`: het `content`-blok staat meteen onder het verhaal. Anders staat het in de uitklapper. |
| `activeren` | stap 1 | De twee vragen van stap 1 (zie §6). |
| `interactie` | stap 5 | De instructie voor de AI-coach: welk scenario, wat een goed antwoord bevat. |
| `quiz` | stap 6 | Precies drie vragen (zie §7). |
| `einde` | stap 6 | Het slot van het verhaal, na de quiz. Invulvelden mogen. |

### Bijzonderheden per stap

- **Stap 1:** heeft geen `context`. Onder het verhaal staan de twee vragen.
- **Stap 4:** het verhaal bevat de feiten van het incident. Die tekst bevat geen
  invulvelden en wordt nooit herschreven. Werk hem bij als er nieuwe informatie
  over het incident is (zie §10).
- **Stap 5:** de `context` is een korte instructie voor de gebruiker. De
  `interactie` lezen alleen de AI-coach en jij, niet de gebruiker.
- **Stap 6:** de `verhaal`-tekst staat vóór de quiz, het `einde` erna. De
  `context` dient als basis voor de herhaling bij een lage score. De laatste
  regel van het einde staat tussen `**` en wordt dus vet getoond.

---

## 5. De zinnen over soorten gevoelige data

Bovenaan `module.yaml` staat `categorie_zinnen`: vier vaste zinnen, één per
soort gevoelige data.

| Sleutel | Waarover |
|---|---|
| `persoonsgegevens` | Alles wat naar een persoon te herleiden is |
| `bijzondere_persoonsgegevens` | Gezondheid, afkomst, religie, … |
| `bedrijfsgevoelig` | Contracten, cijfers, klantenlijsten, … |
| `beroepsgeheim` | Informatie onder het beroepsgeheim |

**Hoe ze gebruikt worden**
- Het taalmodel kiest per verhaal welke soorten van toepassing zijn.
- De app zet de bijhorende zinnen, in deze vaste volgorde, op de plaats van
  `{categorie_zinnen}` in stap 2.
- Het taalmodel schrijft deze zinnen nooit zelf. Het zijn dus de enige
  juridische zinnen in het verhaal, en jij hebt ze volledig in de hand.

**Regels**
- De vier sleutels moeten er alle vier staan, met precies deze namen.
- De zin over bijzondere persoonsgegevens begint met "bovendien" en die over
  beroepsgeheim met "En". Daarom voegt de app de zin over persoonsgegevens
  automatisch toe als die anders zou ontbreken. Herschrijf je deze zinnen, zorg
  dan dat ze ook na de zin over persoonsgegevens goed lezen.

---

## 6. Stap 1: de vragen en de zin in het einde

**De vragen (`activeren` in stap 1)**

| Veld | Wat |
|---|---|
| `vraag` | "Wat heb jij de afgelopen maand al in een AI-tool gezet?" |
| `opties` | De keuzes; de gebruiker kan er meerdere aanduiden |
| `vervolgvraag` | De tweede vraag. Die verschijnt alleen als de gebruiker iets anders dan "Nog niets" aanduidde. |
| `vervolgopties` | "Ja", "Nee", "Weet ik niet" |

**Wat je moet laten staan**
- In `opties`: **"Nog niets"**, **"Een foto"** en **"Een screenshot"**, letterlijk
  zo geschreven. Het einde verwijst ernaar.
- In `vervolgopties`: **"Ja"**.
- De andere opties mag je vrij aanpassen, toevoegen of schrappen.

**De zin in het einde (`einde_eigen_gedrag`, bovenaan `module.yaml`)**

| Sleutel | Wanneer | Huidige zin |
|---|---|---|
| `beeld` | De gebruiker duidde "Een foto" of "Een screenshot" aan | En eerlijk: je gaf zelf aan dat je al eens een foto of screenshot in een AI-tool zette. |
| `andere` | De gebruiker duidde andere opties aan | Je gaf zelf aan dat je al {gedeeld} in een AI-tool zette. Daarvoor geldt precies hetzelfde. |
| `niets` | De gebruiker duidde alleen "Nog niets" aan | Je gaf aan dat je nog niets in een AI-tool zette. Hou die reflex vast. |
| `met_gevoelig` | Wordt erachter geplakt als het antwoord op de vervolgvraag "Ja" was | En daar stond een naam, een gezicht of klantgegevens in. |

**Hoe de zin tot stand komt**
- Duidde de gebruiker niets aan, dan komt er geen zin.
- `{gedeeld}` wordt de opsomming van de aangeduide opties in kleine letters, bv.
  "de tekst van een mail en code". Schrijf de opties dus zo dat ze ook midden in
  een zin kloppen.
- `met_gevoelig` begint met een spatie, omdat die zin achter een andere komt.

---

## 7. De quiz

Elke vraag in `quiz` heeft vier velden:

```yaml
- vraag: "Je vervangt in een klantenlijst alle namen door codes ..."
  opties:
    - "Ja, zonder namen zijn het geen persoonsgegevens meer."
    - "Ja, zolang je de sleutel nooit mee uploadt, ..."
    - "Nee, dit is pseudonimisering: ..."
    - "Nee, want codes zijn op zich al bijzondere persoonsgegevens."
  correct: 2
  feedback_basis: >
    Namen vervangen door codes is pseudonimisering: ...
```

**De velden**
- **`correct`** is het nummer van de juiste optie, **te beginnen bij 0**. De
  eerste optie is 0, de tweede 1, de derde 2, de vierde 3.
- **De volgorde van de opties in het bestand maakt niet uit.** De app schudt ze
  voor elke gebruiker.
- **`feedback_basis`** is de kern van de uitleg. Het taalmodel maakt er
  persoonlijke feedback van, maar mag er inhoudelijk niet van afwijken. Zonder
  taalmodel ziet de gebruiker deze tekst letterlijk. Hij dient ook als herhaling
  bij een lage score.
- Er zijn **precies drie vragen**.

**Regels voor goede vragen**
- Elke vraag is een situatie, geen definitie.
- Elke foute optie is iets wat mensen echt denken.
- Geen "alle bovenstaande" en geen grappige of absurde opties.
- De juiste optie is niet systematisch de langste.

---

## 8. De voorbeeldverhalen

`content/verhaal-voorbeelden.yaml` bevat vier ingevulde verhalen (verpleegkundige,
leerkracht, advocaat, financieel analist).

- **Wat ze doen:** het taalmodel krijgt ze mee als voorbeeld van wat een goed
  verhaal is. Gebruikers zien ze nooit rechtstreeks.
- **Wanneer aanpassen:** als de gegenereerde verhalen te veel op elkaar lijken
  of een bepaalde toon missen. Voeg dan een voorbeeld toe uit een heel ander
  werkveld, of verbeter een bestaand voorbeeld.
- **Regels:** elk voorbeeld moet aan dezelfde regels voldoen als een gegenereerd
  verhaal (lengtes, leestekens, zie de tabel in §3). Gebruik alleen verzonnen
  namen.

---

## 9. De prompts

De map `content/prompts/` bevat de instructies voor het taalmodel. Elke prompt
heeft zijn eigen invulvelden. Die vult de app in; laat ze staan. Een onbekend of
verkeerd gespeld invulveld (bv. `{werkk}`) laat de app weigeren op te starten,
met een melding die zegt welk veld fout is.

| Bestand | Waarvoor | Invulvelden |
|---|---|---|
| `basis.txt` | Gedeeld begin van elke prompt: schrijfregels, profiel, verhaal, toon | `{naam}` `{kennisniveau}` `{gevoelige_data}` `{werk}` `{intro}` `{verhaalblok}` |
| `verhaalvelden.txt` | Het taalmodel bedenkt het verhaal van de gebruiker | `{werk}` `{intro}` `{kennisniveau}` `{voorbeelden}` |
| `kern.txt` | Herschrijven van de context in stap 2 en 3 | `{titel}` `{context}` |
| `verdieping.txt` | Herschrijven van de context in stap 4 | `{titel}` `{context}` |
| `quiz_feedback.txt` | Feedback na elke quizvraag | `{titel}` `{vraag}` `{gekozen_optie}` `{correcte_optie}` `{feedback_basis}` |
| `quiz_samenvatting.txt` | Herhaling bij een score van 0 of 1 | `{score}` `{gemiste_leerdoelen}` `{context}` |
| `chat_agent.txt` | Rol en regels van de AI-coach | `{module_titel}` `{titel}` `{staptype}` `{stap_inhoud}` `{module_samenvatting}` `{activeren_regel}` |
| `chat_toepassing.txt` | Extra instructie voor de AI-coach in stap 5 | `{interactie}` `{leerdoel}` |

**Let op**
- **Accolades hebben in prompts een betekenis.** Wil je een letterlijke
  accolade in een prompt, schrijf dan `{{` of `}}`.
- **`verhaalvelden.txt` bepaalt de vorm van het verhaal.** De app controleert het
  antwoord van het taalmodel streng: lengtes, leestekens, geen opmaaktekens,
  geen naam van de gebruiker. Wijk je hier af van de regels in §3, dan valt de
  app vaker terug op het standaardverhaal.
- **Het standaardverhaal zelf staat niet in een inhoudsbestand** maar in de code
  (`verhaal.py`). Wil je het aanpassen, vraag het dan aan een ontwikkelaar.

---

## 10. Het incident in stap 4 actueel houden

Stap 4 vertelt over het lek van 53 privéfoto's door AI-agents van OpenAI
(bekendgemaakt op 25 september 2026). Het incident komt op meer plaatsen terug,
dus pas bij nieuwe informatie al deze plekken aan:

1. **Stap 4:** de `titel`, het `verhaal`, de `content` (de waarschuwing) en de
   `context`.
2. **Stap 6:** quizvraag 3, met zijn opties en `feedback_basis`.
3. **Stap 6:** de `context` (de samenvatting).
4. **Het design document**, bijlage D: de bronnen.

De tekst vermeldt bewust **niet** of de gebruikers toestemming gaven voor
training en of het lek verband houdt met het eerdere Hugging Face-incident; dat
was op het moment van schrijven onzeker.

---

## 11. Afbeeldingen

- **Waar:** de illustraties staan in `images/`. Een stap verwijst ernaar met
  `image: "bestandsnaam.png"`.
- **Ontbrekend beeld:** bestaat het bestand niet, dan toont de app gewoon geen
  afbeelding.
- **Huidige beelden:** de stappen gebruiken tijdelijk beelden uit de vorige
  versie: `m1-1.png`, `m2-3.png`, `m1-2.png`, `m3-3.png`, `m5-4.png` en
  `m5-5.png`.
- **Nieuwe beelden:** schrijf de prompts in `afbeeldingen-prompts.md`, zet het
  beeld in `images/` en pas `image` aan in de stap.

---

## 12. YAML schrijven zonder fouten

`module.yaml` is een YAML-bestand. Het formaat is streng op een paar punten.

**Inspringen**
- Gebruik altijd **spaties**, nooit tabs.
- Velden van dezelfde stap staan even ver ingesprongen.

**Lange teksten**

| Schrijfwijze | Wat gebeurt er met de regels | Gebruik voor |
|---|---|---|
| `\|-` | Regeleindes blijven behouden; een lege regel geeft een nieuwe alinea | `verhaal` en `einde` |
| `>` | Alle regels worden aan elkaar geplakt tot één alinea | `context`, `feedback_basis`, `interactie` |

Voorbeeld:

```yaml
  verhaal: |-
    Eerste alinea van het verhaal.

    Tweede alinea, met een {invulveld}.
  context: >
    Deze regels worden aan elkaar geplakt
    tot één doorlopende alinea.
```

**Korte teksten**
- Zet een tekst tussen dubbele aanhalingstekens als hij een `:` of een `#`
  bevat, of met een aanhalingsteken begint. Bijvoorbeeld:
  `titel: "Wat staat er op die {beeldwoord}?"`
- Een titel die met `{` begint, moet altijd tussen aanhalingstekens.

**Opmaak in verhaal en einde**
- `**vet**` geeft vette tekst.
- Gebruik geen `$`: de app zou het als een wiskundige formule tonen.

**Opslaan**
- Sla op als **UTF-8 zonder BOM**. In Visual Studio Code is dat de standaard
  ("UTF-8" rechtsonder). Kladblok kan soms een BOM toevoegen.

---

## 13. Je wijziging controleren

**1. Start de app opnieuw.**
- De app leest de inhoud alleen bij het opstarten.
- Lokaal: stop de app (Ctrl+C) en start opnieuw met `streamlit run slides-app.py`.
- Op Streamlit Community Cloud: herstart de app via het menu ("Reboot app").

**2. Kijk of de app opstart.**
- De app controleert de inhoud bij elke start.
- Bij een fout verschijnt bovenaan een rode melding "Contentfout bij het
  opstarten", met het bestand, de stap en wat er mis is. Bijvoorbeeld:
  - `module.yaml, stap 3: verplicht veld 'leerdoel' ontbreekt.`
  - `module.yaml, stap 1: 'verhaal' is niet invulbaar (KeyError('momnet')).` Hier
    staat een tikfout in een invulveld.
  - `prompts/basis.txt: onbekend invulveld {werkk}.`

**3. Doorloop de training een paar keer.** Minstens:
- **Zonder werk in te vullen:** je krijgt het standaardverhaal. Klopt elke zin?
- **Met twee heel verschillende beroepen**, bv. "verpleegkundige" en
  "boekhouder bij een kmo". Klopt het verhaal grammaticaal met andere
  invulwaarden?
- **In stap 1 telkens iets anders aanduiden** ("Een foto", alleen "Code", "Nog
  niets") en het einde in stap 6 nalezen.
- **De quiz één keer goed en één keer slecht maken.**

**4. Laat de automatische tests draaien.**
- Vraag een ontwikkelaar om de tests te draaien (`python -m pytest`).
- Die controleren onder meer dat elk verhaal invulbaar is en dat de quiz klopt.

---

## 14. Wat je beter niet doet

- **Echte namen of echte gevoelige gegevens in de teksten of voorbeelden
  zetten.** Gebruik altijd verzonnen namen.
- **Feiten, cijfers of incidenten in de `verhaal`-tekst zetten die niet
  kloppen.** Het taalmodel controleert die niet; jij bent de enige controle.
- **Juridische formuleringen in de contexttekst ingrijpend wijzigen zonder
  nazicht.** Laat ze nalezen door een DPO of jurist.
- **De `type`, `rol`, `module` of `stap` van een stap veranderen**, of een stap
  toevoegen of schrappen. Dat vraagt een aanpassing in de code.
