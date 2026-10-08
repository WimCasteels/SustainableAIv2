> Vervangen door design-document-v3.md voor de structuur en de inhoud; de principes over didactiek, LLM-laag en privacy blijven gelden.

# Design Document — Adaptieve leerapp "De gevaren van het delen van data met AI-tools"

**Versie 2** · PWO Sustainable AI · Werkdocument, juni 2026

---

## 1. Doel en context

De app is een adaptieve, AI-ondersteunde leeromgeving die gebruikers bewust maakt van de risico's van het delen van data met AI-tools. Versie 1 bewees het basisconcept: statische slidedecks (YAML) waarvan de begeleidende tekst per slide door een LLM wordt gepersonaliseerd op basis van een korte intake. Versie 2 bouwt dit uit tot een volwaardig leertraject met vijf modules, een vast didactisch stramien, een chat-agent voor dialoog en toepassingsscenario's, en quizzen per module.

De inhoud is gebaseerd op het document *De Gevaren van het Delen van Data met AI-tools* (PWO Sustainable AI). De didactische uitwerking volgt het model van Van Gelder en is vastgelegd in het bijhorende werkdocument *Leerpaden versie 2 — Vijf modules, vijf stappen* (`modules-leerpaden-v2.md`), dat als bijlage bij dit design document hoort.

Kernboodschap van de training: **elke prompt is een potentieel datalek.**

## 2. Doelgroep en gebruiksscenario's

De app richt zich op een breed publiek van professionals en studenten, zonder voorkennis over privacy of AI. Er zijn twee evenwaardige gebruiksscenario's, en het ontwerp moet beide bedienen zonder aparte modi te bouwen.

**Zelfstandig gebruik.** Een gebruiker vindt de app online, doorloopt de intake en volgt één of meerdere modules op eigen tempo. Dit scenario vraagt een duidelijke onboarding, zelfverklarende navigatie, een herkenbaar begin- en eindpunt per module, en de chat-agent als vangnet voor vragen die anders onbeantwoord blijven.

**Workshop- of lesgebruik.** Een begeleider laat deelnemers de app (gedeeltelijk) doorlopen tijdens een sessie. Dit scenario vraagt een snelle start (intake in minder dan twee minuten), vrije module- en stapnavigatie zodat de begeleider het tempo bepaalt, en quizzen die zich lenen voor klassikale bespreking.

## 3. Scope van versie 2

**In scope:** vijf modules met elk een leerpad van vijf stappen volgens het vaste stramien (activeren, kern, verdieping, toepassing, quiz & verankering); uitgebreide intake met profielvragen; LLM-personalisatie van de contextteksten met regels per staptype; een chat-agent als vast paneel naast de slides, leidend in de toepassingsstap; vaste quizzen met gepersonaliseerde feedback en score-afhankelijke samenvatting; sectorspecifieke voorbeelden via de personalisatielaag; migratie van de LLM-laag naar een Europees model (Mistral); publieke online deployment met bijhorende kosten- en misbruikbeheersing; transparantie naar de gebruiker over wat er met de eigen intakedata gebeurt.

**Out of scope (bewust):** pre- en postmetingen van kennis en attitudes (vraagt persistente opslag; voorzien voor een latere versie), gebruikersaccounts en voortgangsopslag over sessies heen, meertaligheid (de app is Nederlandstalig), een begeleider-dashboard, en certificaten of attestering.

## 4. Leerinhoud en didactiek

De volledige inhoudelijke uitwerking staat in `modules-leerpaden-v2.md`. Samengevat: vijf modules (Hoe gaan AI-tools om met je data; Welke data is gevoelig; De risico's in de praktijk; Juridisch kader; Veiliger werken met gevoelige data) met elk vijf stappen volgens een vast stramien. Elke stap is gekoppeld aan één leerdoel op een van de vier niveaus van AI-geletterdheid (OESO, 2024). Sectorspecifieke inhoud (hoofdstuk 7 van het brondocument) is geen aparte module maar achtergrondkennis voor de personalisatielaag; de toekomstblik (hoofdstuk 10) sluit module 5 af en dient als verdiepingsmateriaal voor de chat-agent.

Het didactische contract per staptype bepaalt hoeveel vrijheid de LLM krijgt: maximaal bij activeren en toepassing, minimaal bij kern (feiten, definities en cijfers blijven letterlijk behouden) en nul bij de quizvragen zelf (alleen de feedback personaliseert).

## 5. Functioneel ontwerp

### 5.1 Intake en profielbepaling

De intake vervangt het huidige vrije tekstveld door een korte, gestructureerde profielbepaling, afgeleid van fase A uit het didactisch ontwerp maar bewust compact gehouden:

1. Hoe wil je aangesproken worden? (vrij, optioneel)
2. Wat is je kennisniveau van AI? (ik maak kennis met AI / ik werk er al mee / ik wil verdiepen)
3. Werk je met gevoelige data? (ja / nee / ik weet niet wat gevoelige data is)
4. In welke sector werk of studeer je? (zorg, overheid, financieel, onderwijs, juridisch, IT, anders — vrij veld bij "anders")
5. Vertel kort iets over jezelf en waarom je hier bent. (vrij, optioneel)

De antwoorden vormen samen het **gebruikersprofiel** dat in session state leeft en in elke LLM-call meegaat. Antwoord 3 ("ik weet niet wat gevoelige data is") activeert extra uitleg in module 2; het kennisniveau stuurt toon en complexiteit; de sector stuurt de voorbeeldkeuze. Bij de intake staat een korte, zichtbare transparantieverklaring (zie §7).

### 5.2 Slideweergave en navigatie

De bestaande slideweergave blijft de ruggengraat: titel, optionele afbeelding, vaste content en gepersonaliseerde contexttekst. Nieuw is de structuur op twee niveaus: een moduleoverzicht (homescherm met vijf modules en hun leerdoelen) en binnen elke module de vijf stappen met progressie-indicator. Het staptype is visueel herkenbaar (bv. een label of icoon), zodat de gebruiker weet wanneer er interactie verwacht wordt. Navigatie blijft vrij: vorige/volgende, stap-slider, terug naar het overzicht.

### 5.3 Personalisatie van contextteksten

Het mechanisme van versie 1 blijft (één call per stap, gecachet op profiel + stap, streaming naar de UI), maar de prompt wordt per staptype opgebouwd uit drie lagen: de algemene didactische regels (je-vorm, korte zinnen, geen jargon zonder uitleg, Nederlands), de staptype-specifieke personalisatieregel uit het leerpadendocument, en de sectorvoorbeelden uit hoofdstuk 7 als beschikbare achtergrondkennis. Voor het staptype *kern* bevat de prompt de expliciete instructie dat feiten, cijfers, definities en juridische formuleringen ongewijzigd moeten blijven en alleen toon en omkadering mogen variëren.

### 5.4 Chat-agent

De chat-agent is een vast paneel naast of onder de slide (kolomlayout op desktop, expander op mobiel) met `st.chat_message` en `st.chat_input`.

De agent heeft twee rollen. **Reactief** op elke stap: vragen over de inhoud beantwoorden, binnen het onderwerp van de training. **Leidend** in stap 4 (toepassing): de agent opent met het scenario uit het YAML-veld `interactie`, gesitueerd in de context van de gebruiker, wacht op een vrij antwoord en geeft feedback volgens het vaste patroon (juist: bevestig, leg uit waarom, link naar de praktijk; fout: corrigeer rustig, leg eenvoudig uit, geef een voorbeeld, nodig uit om opnieuw te proberen).

De gespreksgeschiedenis loopt door per module en wordt gereset bij een modulewissel; dat houdt de context beheersbaar en de kosten voorspelbaar. De agent krijgt per beurt: het gebruikersprofiel, de inhoud van de huidige stap, een beknopte samenvatting van de hele module, en de gespreksgeschiedenis van de module.

Vangrails in de systeemprompt: blijf bij het onderwerp (datarisico's van AI-gebruik); verwijs bij off-topic vragen vriendelijk terug naar de training; geef geen juridisch advies voor concrete individuele gevallen maar algemene uitleg met de aanbeveling om een DPO of jurist te raadplegen; vind geen feiten, cijfers of incidenten uit die niet in het bronmateriaal staan.

### 5.5 Quiz en verankering

Stap 5 van elke module toont drie vaste meerkeuzevragen uit de quizbibliotheek, één voor één. De vragen en opties komen letterlijk uit de YAML en passeren niet door de LLM. Na elk antwoord genereert de LLM feedback op basis van het veld `feedback_basis` en het profiel. Na de derde vraag genereert de LLM de afsluitende samenvatting, waarvan de diepgang afhangt van de score (bij 0 of 1 juist: heruitleg van de gemiste leerdoelen), afgesloten met de takeaway gekoppeld aan de intake. De score leeft alleen in session state.

## 6. Architectuur

### 6.1 Componenten

De app blijft een Streamlit-applicatie. Het rerun-model van Streamlit is beheersbaar omdat de chat een afgebakende component is naast een verder slide-gebaseerde flow; een herevaluatie van de stack is pas aan de orde als de dialoog centraler wordt (zie §9).

Opbouw in modules (Python): `app.py` (routing, layout), `intake.py` (profielbepaling), `slides.py` (weergave, navigatie, progressie), `personalize.py` (promptopbouw en LLM-calls voor contextteksten), `chat.py` (chat-agent, geschiedenis, scenario-logica), `quiz.py` (quizflow, scoring, samenvatting), `llm.py` (één client-laag richting de LLM-provider, met streaming, retries en time-outs), en `content/` met de YAML-bestanden per module plus `sectoren.yaml` (achtergrondkennis hoofdstuk 7) en `prompts/` (systeemprompt-templates per staptype en voor de agent).

### 6.2 Contentmodel

Eén YAML-bestand per module; elke stap is een entry volgens het schema uit het leerpadendocument (`module`, `stap`, `type`, `titel`, `leerdoel`, `niveau`, `image`, `content`, `context`, `interactie`, `quiz`). De app valideert de YAML bij het opstarten (verplichte velden per type, exact vijf stappen per module, drie quizvragen in stap 5) zodat contentfouten vroeg opduiken. Inhoud en code blijven strikt gescheiden: inhoudelijke iteratie vraagt geen codewijziging.

**Beeldmateriaal.** Elke stap kan een statische illustratie tonen (map `images/`). Vaste stijl: minimalist hand-drawn line art, purple ink op textured paper, conform de richtlijn uit het didactisch ontwerp. De acht bestaande afbeeldingen van module 1 worden herverdeeld; voor de overige modules wordt nieuw beeldmateriaal gegenereerd volgens de vaste stijlprompt (richtcijfer één beeld per stap). Het aanmaken van dit beeldmateriaal hoort bij fase 1 en is een contenttaak, geen codetaak.

### 6.3 LLM-laag: Mistral via OpenRouter

Versie 2 migreert van Claude naar **Mistral**, aangeroepen via OpenRouter (de bestaande integratie uit versie 1 blijft daarmee grotendeels herbruikbaar; alleen de modelstring wijzigt). Richtkeuze: een middelgroot model (bv. Mistral Small of Medium, te bepalen na evaluatie) voor zowel personalisatie als chat; de taken zijn talig maar niet complex, en het Nederlands van de recente Mistral-modellen is voor dit doel toereikend.

Twee aandachtspunten bij deze route. Ten eerste: in OpenRouter de provider-routing vastzetten op Mistral (La Plateforme) en de datapolicy-instellingen controleren (geen logging/training door tussenliggende providers), zodat de verwerking zo dicht mogelijk bij de Europese provider blijft. Ten tweede: OpenRouter zelf is een Amerikaanse tussenpartij; de implicatie daarvan voor de transparantieverklaring staat in §7. De `llm.py`-laag abstraheert de provider, zodat een latere rechtstreekse koppeling met La Plateforme of een lokaal gehoste variant (vLLM/Ollama met een open-weight Mistral-model) een configuratiekwestie is.

De migratie vraagt een kwaliteitscheck: dezelfde set teststappen en testprofielen door beide modellen halen en de output vergelijken op feitelijke trouw (kern-stappen), natuurlijkheid van het Nederlands en naleving van de vangrails. Dit is een expliciete milestone (§10).

### 6.4 Kosten- en misbruikbeheersing (publieke deployment)

Publieke toegankelijkheid zonder accounts betekent dat elke bezoeker LLM-kosten genereert. Maatregelen: een limiet op het aantal LLM-calls per sessie (personalisatie is begrensd door het aantal stappen; voor de chat een maximum aantal beurten per module, met een vriendelijke melding bij het bereiken ervan); een maximale invoerlengte voor chatberichten; caching van gepersonaliseerde teksten op profiel + stap; een dagelijks kostenplafond op de API-key met monitoring; en basisbescherming tegen prompt-injectie in de systeemprompts (gebruikersinvoer wordt nooit als instructie behandeld, de agent houdt vast aan rol en onderwerp). De trainingsinhoud zelf (module 3 behandelt prompt injection) maakt het extra gepast dat de app hier zichtbaar werk van maakt.

## 7. Privacy en transparantie: de eigen medicijnregel

Een app die waarschuwt voor het delen van data met AI-tools moet zelf voorbeeldig zijn. Dit is zowel een ontwerpprincipe als een didactische troef.

Concreet: **dataminimalisatie** (de intake vraagt alleen wat de personalisatie nodig heeft; geen e-mail, geen leeftijd verplicht, geen tracking); **geen persistentie** (profiel, chatgeschiedenis en quizscores leven uitsluitend in de sessie en verdwijnen bij het sluiten); **een Europees model met een eerlijk verhaal over de keten** (het model is Mistral, een Europese provider, maar de aanroep loopt via OpenRouter, een Amerikaanse tussenpartij — de transparantieverklaring benoemt dit expliciet in plaats van een zuiverder beeld te schetsen dan de realiteit; provider-routing en datapolicy worden zo strikt mogelijk ingesteld, en een rechtstreekse koppeling met La Plateforme staat genoteerd als verbeterstap); **transparantie in de UI** (bij de intake een korte verklaring: welke gegevens worden waarheen gestuurd, dat ze niet worden opgeslagen door de app, en verwijzingen naar de verwerkingsvoorwaarden van OpenRouter en Mistral); en een **expliciete waarschuwing bij de chat** om geen echte gevoelige gegevens in te voeren — met een knipoog naar de training zelf.

Het design document legt hiermee ook vast wat er moet gebeuren als de metingen in een latere versie terugkomen: dan ontstaat persistente verwerking en is een formele AVG-toets (grondslag, register, eventueel DPIA) nodig vóór implementatie.

## 8. Niet-functionele eisen

Taal: Nederlands, je-vorm, korte zinnen (conform de schrijfinstructies in het brondocument). Responsiviteit: bruikbaar op laptop en tablet; mobiel functioneel maar niet primair. Performance: gepersonaliseerde tekst start binnen circa twee seconden met streaming; bij een falende LLM-call valt de app terug op de originele contexttekst met een discrete melding (graceful degradation — de training blijft altijd doorloopbaar, ook zonder werkende LLM). Toegankelijkheid: voldoende contrast, geen informatie uitsluitend via kleur of emoji. Onderhoudbaarheid: content in YAML, prompts in aparte templatebestanden, providerkeuze in configuratie.

## 9. Risico's en open punten

**Kwaliteit van het Nederlands bij Mistral.** Risico dat de personalisatie houteriger aanvoelt dan bij Claude. Mitigatie: de vergelijkende evaluatie in §6.3; de providerabstractie houdt een terugkeeroptie open.

**Feitelijke trouw bij personalisatie.** Een LLM die teksten herschrijft kan nuances verschuiven, vooral in de juridische module. Mitigatie: het staptype-contract (kern wordt nauwelijks herschreven), steekproefsgewijze review van gegenereerde varianten per profiel, en het vaste-content-veld voor alles wat letterlijk moet blijven.

**Streamlit-grenzen.** Bij intensief chatgebruik kan de UX (reruns, scrollgedrag) gaan knellen. Mitigatie: chat per module resetten, beurtenlimiet; herevaluatie van de stack als versie 3 de dialoog centraler maakt.

**Publiek misbruik.** Geautomatiseerd verkeer of pogingen tot oneigenlijk gebruik van de chat. Mitigatie: maatregelen in §6.4, kostenplafond als noodrem.

**Hosting: Streamlit Community Cloud (beslist).** De app wordt gedeployed op Streamlit Community Cloud, gekoppeld aan een GitHub-repository. Implicaties: de API-key gaat in het secrets-beheer van het platform (nooit in de repo); de gratis tier heeft beperkte resources en laat apps slapen na inactiviteit (acceptabel voor een prototype, een korte opstartvertraging is mogelijk); en de hosting draait op Amerikaanse infrastructuur — dit wordt meegenomen in de transparantieverklaring van §7, naast de OpenRouter-nuance. Als het gebruik groeit of de Amerikaanse hosting gaat knellen, is migratie naar een EU-gehoste container de voorziene vervolgstap; de app heeft daar geen aanpassingen voor nodig.

## 10. Fasering

**Fase 1 — Fundament.** Contentmodel en YAML-validatie; de vijf modules omzetten naar het nieuwe schema (inhoud uit het leerpadendocument); nieuwe intake; moduleoverzicht en stapnavigatie; beeldmateriaal herverdelen (module 1) en genereren (modules 2–5) volgens de vaste stijlprompt.

**Fase 2 — LLM-migratie.** `llm.py`-abstractie; Mistral-integratie; prompt-templates per staptype; vergelijkende kwaliteitsevaluatie Claude vs. Mistral; beslissing en afstelling.

**Fase 3 — Chat-agent.** Chatpaneel; reactieve modus met vangrails; leidende modus in de toepassingsstappen; beurtenlimieten.

**Fase 4 — Quiz & afronding.** Quizflow met gepersonaliseerde feedback en score-afhankelijke samenvatting; transparantieverklaring en chatwaarschuwing; kostenbeheersing; deployment en test in beide gebruiksscenario's (zelfstandig en workshop).

Elke fase levert een werkende app op; fase 1 is al zelfstandig bruikbaar als verbeterde versie 1.

---

*Bijlage: `modules-leerpaden-v2.md` — volledige uitwerking van de vijf modules, het stramien, de quizbibliotheek en het YAML-schema.*
