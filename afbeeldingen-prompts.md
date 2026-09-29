# Afbeeldingsprompts — alle modules (AP-huisstijl)

Engelstalige prompts voor een image-generator (Gemini/Imagen), in een vlakke, iconische stijl afgestemd op de huisstijl van AP Hogeschool Antwerpen: twee tinten rood plus donkergrijs op een witte achtergrond, geometrische vormen, en korte Nederlandse labels die het concept verduidelijken. Genereer in **landscape (16:9)**.

> **Kleurcodes:** de prompts werken met beschrijvende kleuren ("bright red", "darker red", "dark grey"). Vul de exacte hexwaarden uit de interne AP-huisstijlgids in zodra beschikbaar; die zijn vooral nodig voor de app-CSS en eventuele nabewerking, minder voor de generatie zelf.

> **Let op:** het AP-logo zelf hoort níét in de illustraties (de huisstijl schrijft strikt logogebruik voor: enkel aangeleverde bestanden, altijd op wit, nooit bewerkt). De stijl knipoogt wel naar het beeldmerk via geometrische driehoeken als terugkerend vormelement.

## Vaste basisprompt

Elke afbeelding start met dit blok; plak er de scène-beschrijving van de gewenste afbeelding achter.

```
A flat vector infographic illustration on a clean white background, in landscape format. Simple geometric icon shapes built from triangles, circles and rounded rectangles. Strictly three colors only: bright red, a darker shade of red, and dark grey. No gradients, no shadows, no photorealism. All text labels in dark grey, in a clean geometric sans-serif font, all caps, short and clearly legible. Generous white space around a single clear focal icon composition, easy to understand at a glance.
```

---

## Module 1 — Hoe gaan AI-tools om met je data?

**1.1 — m1-1.png** (Wat deel jij eigenlijk met AI?)
```
Scene: a dark grey person icon at a desk typing on a laptop; from the laptop screen, a stream of small red icons rises up: a document, an envelope, a photo frame and a speech bubble. A label above the stream reads "JOUW DATA".
```

**1.2 — m1-2.png** (Wat gebeurt er met ingevoerde data?)
```
Scene: a horizontal flow of four connected icons left to right: a keyboard, a filing cabinet, a speech bubble with a clock, and a brain made of connected nodes; the icons alternate between the two shades of red, connected by dark grey arrows. Under each icon a label: "INVOER", "OPSLAG", "GESCHIEDENIS", "TRAINING".
```

**1.3 — m1-3.png** (Wie kijkt er mee, en waar staat je data?)
```
Scene: a large dark grey eye icon above a red server cabinet icon, labeled "MENSELIJK TOEZICHT"; from the server, a dotted red line crosses a stylized grey ocean wave toward a second server icon on the other side, labeled "SERVERLOCATIE".
```

**1.4 — m1-4.png** (Consumer of enterprise)
```
Scene: two chat window icons side by side, separated by a dark grey vertical line; the left one in bright red with an open padlock below it, labeled "CONSUMER"; the right one in darker red with a closed padlock and a small shield with a white checkmark, labeled "ENTERPRISE".
```

**1.5** — gebruikt het gedeelde quizbeeld `m-quiz.png` (zie onderaan).

---

## Module 2 — Welke data is gevoelig?

**2.1 — m2-1.png** (Wat circuleert op jouw scherm?)
```
Scene: a laptop icon in dark grey with five small items floating above the screen: a document, an envelope, a photo frame, a speech bubble and a location pin, alternating bright red and darker red. A label below reads "JOUW WERKDAG".
```

**2.2 — m2-2.png** (Persoonsgegevens volgens de AVG)
```
Scene: a large identity card icon with a dark grey person silhouette, surrounded by six small red icons in a circle: an envelope, a phone, a location pin, a house, a bank card and an at-sign. A label below reads "PERSOONSGEGEVENS".
```

**2.3 — m2-3.png** (Bijzondere categorieën: extra beschermd)
```
Scene: a large shield icon split into two shades of red, containing three small white icons: a medical cross, a DNA helix and a heart; a dark grey padlock sits at the bottom point of the shield. A label below reads "EXTRA BESCHERMD".
```

**2.4 — m2-4.png** (Multimodale data: ook beeld en geluid)
```
Scene: a smartphone icon in dark grey photographing a whiteboard icon filled with abstract red scribble lines; a dotted red line travels from the phone to a red cloud icon in the corner. A label below reads "OOK DIT IS DATA".
```

---

## Module 3 — De risico's in de praktijk

**3.1 — m3-1.png** (Shadow AI in jouw omgeving?)
```
Scene: a dark grey laptop icon casting a large flat bright red shadow shaped like a simple robot head; the shadow is clearly bigger than the laptop itself. A label below reads "SHADOW AI".
```

**3.2 — m3-2.png** (Ongecontroleerde datastromen)
```
Scene: a dark grey rectangular outline representing an office building, with three small document icons escaping through a gap in the wall, following a dotted red line toward a large red cloud icon outside. A label below reads "ZONDER TOEZICHT".
```

**3.3 — m3-3.png** (Het Samsung-incident)
```
Scene: a dark grey factory icon with a computer chip on its roof; from a crack in the wall, a stream of small red documents and angle-bracket code symbols flows into an open red chat window icon. A label below reads "3 LEKKEN IN 3 WEKEN".
```

**3.4 — m3-4.png** (Impact van een datalek)
```
Scene: one red chat bubble icon in the center with a dark grey crack through it, labeled "ÉÉN PROMPT"; four thin lines radiate to four corner icons: a broken padlock labeled "PRIVACY", falling coins labeled "GELD", a newspaper labeled "REPUTATIE" and a judge's gavel labeled "JURIDISCH", alternating red shades and grey.
```

---

## Module 4 — Juridisch kader

**4.1 — m4-1.png** (Toezichthouders worden strenger)
```
Scene: a large dark grey judge's gavel coming down next to a red chat window icon showing a white pause symbol. A label below reads "STRENGER TOEZICHT".
```

**4.2 — m4-2.png** (AVG-principes: dataminimalisatie)
```
Scene: a wide dark grey funnel; many small red document icons pour into the top, a single document icon comes out of the narrow bottom end onto an open hand outline. A label below reads "ALLEEN WAT NODIG IS".
```

**4.3 — m4-3.png** (De AI Act: risicogebaseerde aanpak)
```
Scene: a pyramid of four stacked horizontal triangle layers, from dark red at the top to light grey at the bottom; the top layer carries a small white warning triangle, with the label "RISICO" beside the top and "AI ACT" below the pyramid. A small dark grey law book icon stands beside the pyramid.
```

**4.4 — m4-4.png** (Recht op vergetelheid vs. AI-training)
```
Scene: a dark grey eraser icon rubbing against a woven network of connected red nodes and lines; a few faint half-erased nodes show the erasing barely works. A label below reads "RECHT OP VERGETELHEID?".
```

---

## Module 5 — Veiliger werken met gevoelige data

**5.1 — m5-1.png** (Hoe veilig is je huidige werkwijze?)
```
Scene: a dark grey person icon holding a document, standing at a forked path; one path leads to a red cloud icon, the other to a red shield icon with a white checkmark. A label below reads "WELKE WEG KIES JIJ?".
```

**5.2 — m5-2.png** (Anonimisering: geen wondermiddel)
```
Scene: a person silhouette assembled from puzzle pieces in two shades of red, one dark grey piece still being placed by a robotic arm icon; the puzzle pieces carry the small labels "LEEFTIJD", "POSTCODE" and "JOB"; a small grey redaction bar covers the face area but the silhouette is clearly complete. A label below reads "GEEN WONDERMIDDEL".
```

**5.3 — m5-3.png** (Governance en Europese alternatieven)
```
Scene: a dark grey server cabinet icon protected by a large red shield, surrounded by a circle of twelve small red stars; a small grey clipboard icon with three checkmarks stands beside it. A label below reads "EUROPESE ALTERNATIEVEN".
```

**5.4 — m5-4.png** (Eerst checken, dan delen)
```
Scene: a large red upload button icon with an upward arrow, and in front of it a dark grey checklist icon with three ticked boxes, clearly positioned between a hand cursor and the button. A label below reads "EERST CHECKEN".
```

**5.5 — m5-5.png** (De prikbord-regel, slotbeeld)
```
Scene: a large dark grey notice board icon with several small white papers pinned with red pins; one bigger red document with a white padlock symbol is about to be pinned by a hand outline, while two simple grey person icons look on. A label below reads "OPENBAAR PRIKBORD?".
```

---

## Gedeeld quizbeeld — m-quiz.png (voor stappen 1.5, 2.5, 3.5 en 4.5)

```
Scene: a large clipboard icon in dark grey with three answer rows; one row is marked with a bold red checkmark in a red circle; a small red lightbulb icon floats above the clipboard. A label below reads "WAT ONTHOUD JE?".
```

---

## Praktische tips

Genereer per prompt enkele varianten en kies op eenvoud: het beste beeld is in één oogopslag leesbaar, ook klein weergegeven naast een slide. Controleer de labels streng op spelling; tekst is de zwakste plek van image-generators, dus genereer bij een spelfout opnieuw of zet de tekst er achteraf op (dat geeft bovendien een consistent lettertype over alle beelden heen, het dichtst bij de Foco-typografie van AP). Bewaak ook de kleurdiscipline (weiger varianten met blauw, geel of kleurverlopen). Houd alle gekozen beelden naast elkaar voor een consistentiecheck vóór je ze in `images/` plaatst. Bestandsnamen volgen het patroon `m{module}-{stap}.png`, conform het `image`-veld in de YAML's. Overweeg tot slot of de app-CSS mee evolueert naar de AP-kleuren (de huidige indigo-accenten vloeken met rood); dat is een kleine aanpassing in het stylesheet-blok van de app.
