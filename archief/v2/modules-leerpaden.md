# Leerpaden versie 2 — Vijf modules, vijf stappen

**Werkdocument bij het design document** · Gebaseerd op *De Gevaren van het Delen van Data met AI-tools* (PWO Sustainable AI)

---

## Het vaste stramien

Elke module volgt hetzelfde leerpad van vijf stappen. Dit maakt de structuur voorspelbaar voor de gebruiker, uniform voor de app-architectuur (elke stap = één scherm in de YAML), en stuurbaar voor de LLM.

| Stap | Type | Functie | Rol van de LLM |
|------|------|---------|----------------|
| 1 | **Activeren** | Herkenbare situatie of prikkelende vraag die voorkennis en relevantie activeert | Situatie herschrijven naar de leefwereld van de gebruiker (sector, rol, gebruikte tools) |
| 2 | **Kern** | De essentiële concepten, feitelijk en compact | Toon en complexiteit aanpassen aan kennisniveau; feiten blijven onaangetast |
| 3 | **Verdieping** | Case, voorbeeld of nuance die de kern tastbaar maakt | Voorbeeld kiezen of inkleuren passend bij het profiel |
| 4 | **Toepassing** | Scenario- of beslissingsvraag, bij voorkeur via de chat-agent | Scenario situeren in de context van de gebruiker; feedback geven volgens het vaste feedbackpatroon |
| 5 | **Quiz & verankering** | Drie vaste meerkeuzevragen (één per kernleerdoel), daarna samenvatting plus één concrete takeaway | Vragen zijn vast en worden níét herschreven; feedback op antwoorden volgt het vaste feedbackpatroon en is gepersonaliseerd. Bij lage score: uitgebreidere samenvatting. Takeaway koppelen aan de eigen praktijk |

**Leerdoelniveaus** volgen de vier niveaus van AI-geletterdheid (OESO, 2024): *kennen & begrijpen*, *toepassen*, *evalueren & creëren*, *ethisch handelen*. Elke stap is gekoppeld aan één dominant niveau.

**Sectorspecifieke inhoud (hfst. 7)** is geen module maar voedt de personalisatielaag: de LLM krijgt de sectorvoorbeelden als achtergrondkennis en zet ze in waar relevant. **Blik op de toekomst (hfst. 10)** dient als afsluiting na module 5 en als verdiepingsmateriaal voor de chat-agent.

---

## Module 1 — Hoe gaan AI-tools om met je data?

**Modeldoel:** Je kan uitleggen wat er met data gebeurt wanneer je die invoert in een AI-tool, en bewust kiezen tussen consumer- en enterprise-versies.

| Stap | Leerdoel (Je kan…) | Niveau | Kerninhoud (bron) |
|------|--------------------|--------|-------------------|
| 1.1 Activeren | …benoemen welke data jij zelf al met AI-tools deelde | Ethisch handelen | Herkenbare openingsvraag: "Wat heb jij deze week in een AI-tool getypt of geüpload?" Cijfer als anker: 39,7% van alle AI-interacties bevat gevoelige data (Cyberhaven 2026). (hfst. 1) |
| 1.2 Kern | …de drie stappen uitleggen die je data doorloopt: opslag in logbestanden, bewaarde geschiedenis, mogelijk gebruik voor training | Kennen & begrijpen | Wat erin gaat, krijg je niet zomaar terug; OpenAI kan specifieke prompts niet verwijderen. (hfst. 2) |
| 1.3 Verdieping | …uitleggen dat menselijk toezicht en serverlocatie extra risicofactoren zijn | Kennen & begrijpen | Medewerkers van providers kunnen conversaties inzien (kwaliteit, veiligheid, training). Amerikaanse servers: Schrems II en de CLOUD Act. (hfst. 2) |
| 1.4 Toepassing | …beoordelen of een consumer- of enterprise-versie geschikt is voor een gegeven situatie | Evalueren | Scenario via chat: collega gebruikt gratis account voor werkdocument. Verschillen: training-opt-out, DPA, data-isolatie, EU-verwerking. (hfst. 2) |
| 1.5 Quiz & verankering | …aantonen dat je weet wat er met ingevoerde data gebeurt | Kennen & begrijpen | Quiz M1 (3 vragen, zie quizbibliotheek) + samenvatting + takeaway: "Behandel elke prompt als data die je uit handen geeft." |

---

## Module 2 — Welke data is gevoelig?

**Modeldoel:** Je kan gevoelige data herkennen — persoonsgegevens, bijzondere categorieën, bedrijfsgevoelige en multimodale data — en beoordelen of iets in een AI-tool thuishoort.

| Stap | Leerdoel (Je kan…) | Niveau | Kerninhoud (bron) |
|------|--------------------|--------|-------------------|
| 2.1 Activeren | …inschatten welke data in jouw werkcontext circuleert | Ethisch handelen | Openingsvraag: "Welke informatie passeert er op een gewone werkdag op jouw scherm?" Niet alle data is gelijk: wettelijk beschermd vs. strategisch waardevol. (hfst. 3) |
| 2.2 Kern | …uitleggen wat persoonsgegevens zijn volgens de AVG | Kennen & begrijpen | Alle informatie over een geïdentificeerde of identificeerbare persoon: naam, adres, e-mail, telefoon, IP-adres, locatie, financiële gegevens, online identificatoren. (hfst. 3) |
| 2.3 Verdieping | …bijzondere categorieën herkennen en uitleggen waarom die extra beschermd zijn | Kennen & begrijpen | Ras/etniciteit, politieke opvattingen, religie, vakbond, genetisch/biometrisch, gezondheid, seksuele geaardheid. Verwerking in principe verboden. Plus bedrijfsgevoelig: broncode, plannen, contracten, klantenlijsten; beroepsgeheim. (hfst. 3) |
| 2.4 Toepassing | …beoordelen of concrete data (ook beeld, audio, video) veilig is om in te voeren | Evalueren | Scenario via chat: foto van whiteboard met klantnamen uploaden — gevoelig of niet? Multimodale data bevat evengoed persoonsgegevens en interne info. (hfst. 3) |
| 2.5 Quiz & verankering | …gevoelige datacategorieën correct herkennen | Kennen & begrijpen | Quiz M2 (3 vragen, zie quizbibliotheek) + samenvatting + takeaway: "Gevoelig zit niet alleen in tekst — ook in wat je fotografeert, opneemt of deelt als scherm." |

---

## Module 3 — De risico's in de praktijk

**Modeldoel:** Je kan risico's van AI-gebruik herkennen in concrete situaties en de mogelijke impact van een datalek inschatten.

| Stap | Leerdoel (Je kan…) | Niveau | Kerninhoud (bron) |
|------|--------------------|--------|-------------------|
| 3.1 Activeren | …herkennen of shadow AI in jouw omgeving speelt | Ethisch handelen | "Gebruik jij of een collega weleens een AI-tool die IT niet kent?" Cijfers: >80% gebruikt niet-goedgekeurde tools (UpGuard), een derde via persoonlijke accounts (Cyberhaven). (hfst. 4) |
| 3.2 Kern | …uitleggen wat shadow AI is en waarom het risico's creëert | Kennen & begrijpen | Definitie; goede intenties, ongecontroleerde datastromen; blokkeren werkt niet (45% vindt workarounds). (hfst. 4) |
| 3.3 Verdieping | …aan de hand van het Samsung-incident uitleggen hoe snel het misgaat | Kennen & begrijpen | Samsung-case (drie lekken in drie weken). Technische vectoren beknopt: extractie van trainingsdata, prompt injection, browser-extensies, agentic AI. (hfst. 4) |
| 3.4 Toepassing | …de impact van een datalek inschatten op privacy, bedrijfsgeheimen, reputatie en juridische aansprakelijkheid | Evalueren | Scenario via chat + impactgebieden: onverwijderbare persoonsgegevens, verlies concurrentievoordeel, schending beroepsgeheim, reputatie, AVG-boetes tot 20 mln/4%. (hfst. 5) |
| 3.5 Quiz & verankering | …risico's en impact correct benoemen, en het grootste risico in eigen context aanduiden | Ethisch handelen | Quiz M3 (3 vragen, zie quizbibliotheek) + reflectie: "Welke schade zou bij jou het grootst zijn?" Takeaway: "Eén prompt kan jaren werk blootleggen." |

---

## Module 4 — Juridisch kader

**Modeldoel:** Je kan de belangrijkste regels uit de AVG en de AI Act toepassen om te beoordelen of het delen van data met AI-tools toegestaan is.

| Stap | Leerdoel (Je kan…) | Niveau | Kerninhoud (bron) |
|------|--------------------|--------|-------------------|
| 4.1 Activeren | …herkennen dat AI-gebruik onder bestaande wetgeving valt | Kennen & begrijpen | Anker: Italiaanse Garante verbood ChatGPT tijdelijk (2023); toezichthouders worden strenger. (hfst. 6) |
| 4.2 Kern | …de AVG-kernprincipes toepassen op AI-gebruik | Toepassen | Doelbinding, dataminimalisatie, opslagbeperking, verantwoordingsplicht, verplichte DPA bij verwerking namens jouw organisatie. (hfst. 6) |
| 4.3 Verdieping | …de risicogebaseerde aanpak van de AI Act uitleggen | Kennen & begrijpen | Vier niveaus: onaanvaardbaar, hoog, beperkt, minimaal risico; transparantieplicht voor general-purpose AI. (hfst. 6) |
| 4.4 Toepassing | …de spanning tussen rechten van betrokkenen en AI-training beoordelen | Evalueren | Scenario via chat rond recht op vergetelheid: data in een getraind model is technisch nauwelijks te verwijderen; recht op uitleg vs. black box. (hfst. 6) |
| 4.5 Quiz & verankering | …de juridische basisregels correct toepassen en verantwoorden waarom je data wel of niet deelt | Ethisch handelen | Quiz M4 (3 vragen, zie quizbibliotheek) + samenvatting + takeaway: "Deel alleen wat strikt nodig is — en kunnen verantwoorden waarom." |

---

## Module 5 — Veiliger werken met gevoelige data

**Modeldoel:** Je kan in praktijksituaties veilige keuzes maken: data beschermen, de juiste tools kiezen en weten waar je terechtkan bij twijfel.

| Stap | Leerdoel (Je kan…) | Niveau | Kerninhoud (bron) |
|------|--------------------|--------|-------------------|
| 5.1 Activeren | …inschatten hoe veilig je huidige werkwijze is | Ethisch handelen | "Wat doe jij vandaag als je een document met gevoelige info wil laten samenvatten?" (hfst. 9) |
| 5.2 Kern | …het verschil uitleggen tussen anonimisering en pseudonimisering, en de beperkingen ervan benoemen | Kennen & begrijpen | Anonimisering (onomkeerbaar, buiten AVG) vs. pseudonimisering (omkeerbaar, onder AVG). Re-identificatie: 87% uniek identificeerbaar via geboortedatum + geslacht + postcode. Geen wondermiddel. (hfst. 8) |
| 5.3 Verdieping | …veiligere alternatieven en governance-maatregelen benoemen | Toepassen | AI-gebruiksbeleid, rollen (DPO, IT, gebruiker), leveranciersbeoordeling; Europese en lokale alternatieven (Mistral, Aleph Alpha, lokaal gehoste open-source modellen). (hfst. 9) |
| 5.4 Toepassing | …in een praktijksituatie de veilige keuze maken | Toepassen | Beslissingsscenario via chat: document met gevoelige info — uploaden, eerst ontdoen van gevoelige info + goedgekeurde tool, of persoonlijk account? Vuistregels als checklist. (hfst. 9) |
| 5.5 Quiz & verankering | …veilige keuzes correct maken en de prikbord-regel toepassen als dagelijkse reflex | Ethisch handelen | Quiz M5 (3 vragen, zie quizbibliotheek) + kernboodschap: "Behandel een AI-tool als een slimme maar onbetrouwbare buitenstaander: deel alleen wat je op een openbaar prikbord zou hangen." Korte blik vooruit: multimodaal, agentic AI, evoluerende regelgeving. (hfst. 10) |

---

## Quizbibliotheek

Drie vaste meerkeuzevragen per module, grotendeels hergebruikt uit het agent-script. De vragen en antwoordopties zijn **vast** (de LLM herschrijft ze niet); alleen de feedback op het gekozen antwoord wordt gepersonaliseerd volgens het feedbackpatroon. Score: 3/3 of 2/3 = beknopte samenvatting, eventueel verdiepende reflectievraag; 0/3 of 1/3 = uitgebreidere samenvatting met heruitleg van de fout beantwoorde leerdoelen.

**Quiz M1 — Hoe gaan AI-tools om met je data?**
1. Wat gebeurt er mogelijk met data die je invoert in een AI-tool? — A meteen verwijderd / B opgeslagen en mogelijk gebruikt voor training / C blijft alleen op je toestel → **B**
2. Wie kan jouw conversaties met een AI-tool potentieel inzien? — A niemand / B alleen jijzelf / C ook medewerkers van de AI-provider → **C**
3. Wat is het belangrijkste verschil tussen een consumenten- en een enterprise-versie? — A enterprise is altijd sneller / B enterprise biedt vaak betere databescherming / C consumentenversies zijn veiliger → **B**

**Quiz M2 — Welke data is gevoelig?**
1. Welke van deze zijn persoonsgegevens? — A naam / B IP-adres / C e-mailadres / D alle drie → **D**
2. Welke gegevens zijn bijzondere persoonsgegevens? — A postcode / B gezondheidsgegevens / C voornaam / D gebruikersnaam → **B**
3. Kan een spraakopname of foto gevoelige data bevatten? — A nee, alleen tekst is gevoelig / B ja, ook beeld en audio kunnen persoonsgegevens en interne info bevatten → **B**

**Quiz M3 — De risico's in de praktijk**
1. Wat is shadow AI? — A een slim AI-model / B gebruik van AI-tools zonder toestemming of toezicht van de organisatie / C een veilige interne AI → **B**
2. Een collega gebruikt een persoonlijk gratis AI-account om interne documenten samen te vatten. Wat is het grootste risico? — A tragere wifi / B gevoelige data verlaat de organisatie zonder bescherming / C het document wordt mooier → **B**
3. Welke gevolgen kan een datalek via AI-tools hebben? — A reputatieschade / B verlies van bedrijfsgeheimen / C privacyproblemen en boetes / D alle drie → **D**

**Quiz M4 — Juridisch kader**
1. Welke wet beschermt persoonsgegevens in de EU? — A AI Act / B AVG/GDPR / C auteurswet → **B**
2. Hoe reguleert de AI Act AI-systemen? — A per bedrijfsgrootte / B volgens risiconiveau / C alleen voor chatbots → **B**
3. Waarom staat het recht op vergetelheid op gespannen voet met AI-training? — A AI-providers weigeren altijd / B data in een getraind model is technisch nauwelijks te verwijderen / C het recht geldt niet voor AI → **B**

**Quiz M5 — Veiliger werken met gevoelige data**
1. Wat is het verschil tussen anonimisering en pseudonimisering? — A geen verschil / B bij pseudonimisering blijft de persoon identificeerbaar via aanvullende informatie / C anonimisering valt onder de AVG, pseudonimisering niet → **B**
2. Je wil een document met gevoelige informatie laten samenvatten door AI. Wat doe je best? — A het volledige document uploaden / B eerst gevoelige informatie verwijderen en een goedgekeurde tool gebruiken / C een persoonlijk gratis account gebruiken → **B**
3. Je wil een nieuwe AI-tool gebruiken voor je werk. Wat doe je eerst? — A meteen gebruiken / B checken of de tool is goedgekeurd binnen je organisatie / C snel even testen met echte data → **B**

---

## Vertaling naar de app

**YAML-structuur per stap.** Elke stap wordt één entry met vaste velden:

```yaml
- module: 1
  stap: 2
  type: kern                  # activeren | kern | verdieping | toepassing | quiz_verankering
  titel: "Wat gebeurt er met ingevoerde data?"
  leerdoel: "Je kan de drie stappen uitleggen die je data doorloopt"
  niveau: "kennen & begrijpen"
  image: "m1-2.png"           # optioneel; illustratie bij de stap
  content: |                  # vaste, niet-personaliseerbare inhoud (bullets, beeld)
    ...
  context: >                  # basistekst die de LLM personaliseert
    ...
  interactie: >               # alleen bij type toepassing: scenario-opdracht voor de chat-agent
    ...

- module: 1
  stap: 5
  type: quiz_verankering
  titel: "Wat onthoud je?"
  leerdoel: "Je kan aantonen dat je weet wat er met ingevoerde data gebeurt"
  niveau: "kennen & begrijpen"
  quiz:                       # vaste vragen, worden níét herschreven door de LLM
    - vraag: "Wat gebeurt er mogelijk met data die je invoert in een AI-tool?"
      opties: ["Meteen verwijderd", "Opgeslagen en mogelijk gebruikt voor training", "Blijft alleen op je toestel"]
      correct: 1
      feedback_basis: >       # kern van de uitleg; LLM personaliseert de formulering
        Invoer wordt opgeslagen in logbestanden, geschiedenis wordt bewaard,
        en data kan gebruikt worden voor modeltraining.
    # ... vraag 2 en 3
  context: >                  # samenvatting + takeaway, gepersonaliseerd o.b.v. quizscore
    ...
```

**Personalisatieregels per staptype** (voor de systeemprompt):

- *Activeren*: herschrijf de situatie naar sector en rol van de gebruiker; stel de vraag persoonlijk.
- *Kern*: pas alleen toon en complexiteit aan (beginner: eenvoudiger taal, meer uitleg; gevorderd: compacter, meer nuance). Feiten, definities en cijfers blijven letterlijk behouden.
- *Verdieping*: kies of kleur het voorbeeld passend bij het profiel; sectorvoorbeelden uit hfst. 7 zijn hiervoor beschikbaar.
- *Toepassing*: situeer het scenario in de context van de gebruiker; feedback volgens het vaste patroon (juist: bevestig, leg uit, link naar praktijk; fout: corrigeer rustig, leg eenvoudig uit, geef voorbeeld, laat opnieuw proberen).
- *Quiz & verankering*: vragen en antwoordopties letterlijk tonen zoals in de YAML. Feedback per antwoord personaliseren op basis van `feedback_basis` en het gebruikersprofiel. Na de drie vragen: samenvatting genereren waarvan de diepgang afhangt van de score (lage score = heruitleg van de gemiste leerdoelen), afgesloten met de takeaway gekoppeld aan wat de gebruiker bij de intake vertelde.

**Chat-agent.** De agent krijgt per module de volledige moduleinhoud plus het gebruikersprofiel als context, blijft binnen het onderwerp, en is bij stap 4 (toepassing) leidend: daar stelt hij het scenario, wacht op antwoord en geeft feedback.

**Beeldmateriaal.** Elke stap kan een illustratie dragen via het `image`-veld. Vaste stijl voor alle nieuwe beelden: *a minimalist hand-drawn line art illustration on textured paper, purple ink only* (conform de richtlijn uit het didactisch ontwerp). De acht bestaande afbeeldingen van module 1 (afb1-1 t/m afb1-8) zijn herbruikbaar maar moeten herverdeeld worden over de vijf nieuwe stappen; voor modules 2 t/m 5 is nieuw beeldmateriaal nodig (richtcijfer: één beeld per stap, 25 in totaal, te genereren met een image-generator volgens de vaste stijlprompt). Afbeeldingen zijn statisch en personaliseren niet mee.
