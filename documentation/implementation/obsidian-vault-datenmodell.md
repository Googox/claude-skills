# Obsidian Vault-Datenmodell für A/A Executive Search

Spezifikation des Datenmodells für ein bidirektionales Executive-Search-CRM in
Obsidian, lesbar und schreibbar durch Claude über MCP.

Stand: Oktober 2026. Grundlage für den geplanten Skill `aa-obsidian-sync`.

---

## 1. Entscheidungsgrundlage

Das Modell steht unter drei Randbedingungen, die jede Designentscheidung
dominieren. Sie sind nicht verhandelbar, weil sie aus der Technik und aus dem
Recht kommen, nicht aus Geschmack.

### 1.1 Technisch: der kleinste gemeinsame Nenner sind sieben Tools

Claude Desktop lädt ausschließlich stdio-Prozesse, Claude Code CLI kann HTTP.
Wer beide Clients nutzt, hat damit zwei unterschiedliche Tool-Sets: 18 Tools
über den plugin-eigenen MCP-Server, 7 Tools über den stdio-Wrapper. Portabler
Code baut auf der kleineren Menge:

| Tool | Konsequenz für das Modell |
|------|---------------------------|
| `list_files_in_vault`, `list_files_in_dir` | Ordner dürfen als Navigationshilfe dienen, nicht als Zustandsspeicher |
| `get_file_contents` | Eine Entität ist genau eine Datei |
| `search` | Nur Textsuche, kein strukturierter Query. Sichten entstehen über Dataview, nicht über Suche |
| `patch_content` | Schreiben erfolgt relativ zu Überschriften. Überschriften sind damit Teil des Schemas, nicht Layout |
| `append_content` | Das einzige verlustfreie Schreib-Tool. Historie wird angehängt, nie überschrieben |
| `delete_file` | Wird von Skills nie benutzt. Löschen bleibt manuell |

**Kein `vault_move`.** Das ist die wichtigste Einzelkonsequenz: Ein
Statuswechsel darf niemals eine Datei verschieben, weil der Desktop-Client das
nicht ausführen kann. Status lebt im Frontmatter.

### 1.2 Rechtlich: der lokale Server löst Speicherung, nicht Übermittlung

Ein MCP-Server auf `127.0.0.1` verhindert, dass Notizen bei einem dritten
Cloud-Anbieter liegen. Er verhindert nicht, dass Inhalte an die Anthropic-API
gehen, sobald Claude sie liest. Für einen Verantwortlichen im Sinne der DSGVO
ist das der entscheidende Punkt.

Die Trennlinie verläuft deshalb nicht zwischen Entitäten, sondern zwischen
Herkunftsarten der Information:

- **Öffentlich recherchierbar** (Werdegang, Stationen, Rolle, Unternehmensdaten,
  Pressemeldungen): darf an ein Modell. Es ist ohnehin öffentlich.
- **Vertraulich mitgeteilt** (Gehaltsvorstellung, Wechselmotiv, familiäre Lage,
  Einschätzung über Dritte, alles aus einem Vertrauensverhältnis): geht nie an
  ein Modell.

### 1.3 Fachlich: die bestehenden sechs Skills setzen die Felder

Das Modell erfindet keine Statuslogik. Es übernimmt, was in
`aa-pipeline-review`, `aa-follow-up`, `aa-mandate-kickoff`,
`aa-market-intelligence`, `aa-pitch-prep` und `aa-weekly-review` bereits
festgelegt ist: die Temperaturskala kalt/warm/heiss, die gesetzte Reihenfolge
der Kernpipeline, die Wellen-Trennung, die Fee-Modelle, die Mandatsphasen.

---

## 2. Zwei Vaults, nicht zwei Ordner

**Entscheidung:** Vertrauliche Daten liegen in einem zweiten, physisch
getrennten Obsidian-Vault, der niemals per MCP verbunden wird.

**Begründung:** Ein Unterordner im selben Vault ist Sicherheitstheater. Die
Tools `list_files_in_vault` und `get_file_contents` greifen auf den Vault-Root
zu; eine Ordner-Allowlist bietet das Plugin nicht. Wer Vertraulichkeit
organisatorisch statt technisch trennt, hat sie nicht getrennt, sondern nur
aufgeschrieben, dass er es gern hätte.

```
AA-Search/                     <- per MCP verbunden, modellsichtbar
├── 00-Steuerung/
│   ├── Pipeline.md                 Dataview-Sichten, Einstiegsseite
│   ├── Wochenreview.md             Topf A / Topf B Historie
│   └── Ziele.md                    Kernziel, Meilensteine
├── 10-Kontakte/                    Führungskräfte (Kandidaten und Entscheider)
├── 20-Arbeitgeber/                 Unternehmen und Gruppen
├── 30-Mandate/                     Suchaufträge, Aktenzeichen
├── 40-Ereignisse/                  Bewertungsrelevante Interaktionen
├── 50-Markt/                       Marktbeobachtungen, Führungswechsel
├── 80-Vorlagen/                    Templates je Entität
└── 90-Playbooks/                   Pitch-Argumente, Methodik, Fee-Modelle

AA-Vertraulich/                <- NIE verbunden, nie modellsichtbar
└── Personen/
    └── K-0042.md                   Gehalt, Motive, private Lage
```

**Verknüpfung über Pseudonym.** Die Kontaktdatei im offenen Vault führt das Feld
`vertraulich_ref: K-0042`. Claude sieht die Kennung, nie den Inhalt dahinter.
Aaron öffnet den zweiten Vault manuell, wenn er die Daten braucht.

**Ordner sind Navigationshilfe, nie Zustand.** Eine Datei wandert nie zwischen
Ordnern, weil sich ihr Status ändert. Grund: `vault_move` fehlt im portablen
Tool-Set, siehe 1.1.

---

## 3. Entitäten und Frontmatter-Schemata

Fünf Entitäten. Jede Datei trägt `typ` und `geschaeft` als Pflichtfelder.

**Alle Beispielwerte in diesem Abschnitt sind frei erfunden.** Keine Namen, Unternehmen oder Aktenzeichen in den Schemata beziehen sich auf reale Kontakte der Pipeline. Wer ein Beispiel für einen Datensatz hält, arbeitet mit erfundenen Daten.

`geschaeft: aa` ist kein Dekor: `aa-mandate-kickoff` und
`aa-market-intelligence` verlangen beide ausdrücklich die Trennung von
Alexandras separaten Geschäftsideen. Ein Feld macht diese Trennung abfragbar
und damit prüfbar.

Werte enthalten keine Umlaute (`heiss` statt `heiß`), weil Umlaute in
YAML-Werten und Dateinamen je nach Betriebssystem unterschiedlich normalisiert
werden (macOS NFD, Windows NFC) und Queries dann stillschweigend ins Leere
greifen.

### 3.1 Kontakt (Führungskraft)

Eine Datei für Kandidaten und für Arbeitgeber-Entscheider. Begründung: Im
Executive Search ist dieselbe Person heute Gesprächspartner und morgen
Kandidat. Zwei Entitäten würden dieselbe Person doppelt führen.

```yaml
---
typ: kontakt
geschaeft: aa
rolle_fuer_aa: [kandidat, entscheider]   # eine oder beide
status: aktiv                            # aktiv | ruhend | pitch_terminiert | platziert | abgesagt
temperatur: warm                         # kalt | warm | heiss
welle: kern                              # kern | vibe
pipeline_rang: 3                         # 1-14, nur welle=kern, von Aaron gesetzt
unternehmen: "[[Muster Automobile GmbH]]"
position: "Geschaeftsfuehrer Vertrieb"
region: Nord
erstkontakt_am: 2026-10-14
letzte_interaktion_am: 2026-10-21
naechste_aktion: "Rueckruf zu Mandatsunterlagen"
naechste_aktion_am: 2026-11-04
mandat: "[[M-2026-001 Muster GF Vertrieb]]"
assessment_score:                        # 0-100, leer bis Methodik vorliegt
assessment_stand: nicht_bewertet         # nicht_bewertet | vorlaeufig | final
knockout: false
knockout_grund:
quelle: "Automobilwoche Personalien 2026-10-14"
vertraulich_ref: K-0042
---

## Profil
## Fit-Einschaetzung
## Journal
## Offene Punkte
```

**`pipeline_rang` ist für Skills schreibgeschützt.** `aa-pipeline-review` sagt
wörtlich, die Reihenfolge sei von Aaron gesetzt und werde nicht neu verhandelt.
Das Feld existiert, damit die Reihenfolge überlebt; kein Skill ändert es
selbständig.

**Die vier Überschriften sind Pflicht und fixiert.** Sie sind die Anker für
`patch_content`. Fehlt `## Journal`, kann kein Skill einen Kontaktverlauf
anhängen, ohne die Datei zu überschreiben.

### 3.2 Arbeitgeber

```yaml
---
typ: arbeitgeber
geschaeft: aa
status: ziel                             # ziel | im_gespraech | mandant | kein_bedarf
gruppe: "Muster Gruppe"
marken: [BMW, MINI]
standorte: 12
region: Nord
entscheider: ["[[Beispiel, Erika]]"]
bedarf_hypothese: "Nachfolge mittleres Management"
letzte_interaktion_am: 2026-10-21
naechste_aktion: "Termin bestaetigen"
naechste_aktion_am: 2026-11-06
mandate: ["[[M-2026-001 Muster GF Vertrieb]]"]
quelle: "Unternehmenswebsite, Handelsblatt 2026-09-30"
---

## Lage
## Schmerzpunkt-Hypothesen
## Journal
## Offene Punkte
```

`bedarf_hypothese` heißt bewusst Hypothese. `aa-pitch-prep` verlangt, vermutete
Schmerzpunkte als Hypothesen zu kennzeichnen und nicht als Fakten über das
konkrete Haus. Der Feldname trägt diese Pflicht.

### 3.3 Mandat

```yaml
---
typ: mandat
geschaeft: aa
aktenzeichen: M-2026-001
mandant: "[[Muster Automobile GmbH]]"
position: "Geschaeftsfuehrer Vertrieb"
fee_modell: model_a_hybrid               # model_a_hybrid | model_b_retained
honorar_mindest: 15000
honorar_vereinbart:                      # Vertragsstand schlaegt Standardzahlen
phase: kickoff                           # kickoff | longlist | shortlist | interviews | platzierung | abgeschlossen | abgebrochen
start_am: 2026-11-01
ziel_platzierung_am: 2027-02-01
kandidaten: []
zahlung_status: offen                    # offen | teilzahlung | vollstaendig
---

## Anforderungsprofil
## Suchstrategie
## Meilensteine
## Journal
## Risiken
```

Die Phasen sind exakt die aus `aa-mandate-kickoff`: Kickoff, Longlist,
Shortlist, Interviews, Platzierung. `honorar_vereinbart` existiert separat von
`honorar_mindest`, weil der Skill ausdrücklich verlangt, bei abweichender
Vereinbarung den vertraglichen Stand als Wahrheit zu nehmen und nicht auf die
Standardzahlen zurückzufallen.

### 3.4 Ereignis

```yaml
---
typ: ereignis
geschaeft: aa
datum: 2026-10-21
kanal: termin_vor_ort                    # telefon | mail | termin_vor_ort | video | messe | empfehlung
kontakt: "[[Beispiel, Erika]]"
unternehmen: "[[Muster Automobile GmbH]]"
mandat:
anlass: "Pitch Erstgespraech"
ergebnis: positiv                        # positiv | neutral | negativ | kein_erreichen
temperatur_nachher: warm
folgeaktion: "Mandatsunterlagen senden"
folgeaktion_am: 2026-10-23
---

## Notizen
## Zusagen
```

**Nicht jede Berührung wird eine Datei.** Die Trennlinie: Was bewertet werden
muss, wird ein Ereignis mit eigener Datei. Was nur dokumentiert wird (kurze
Mail, Erinnerung, Absage eines Termins), wird eine Zeile unter `## Journal` in
der Kontaktdatei. Begründung: Bei rund 64 Kontakten und wöchentlichen Touches
erzeugt ein Ereignis-pro-Mail mehrere hundert Dateien im Jahr, von denen
neunzig Prozent nie abgefragt werden.

`## Zusagen` ist ein eigener Abschnitt, weil `aa-follow-up` ausdrücklich
verbietet, Zusagen zu erfinden, die Aaron nicht gemacht hat. Ein eigener
Abschnitt macht den Unterschied zwischen "stand im Gespräch" und "wurde
zugesagt" strukturell sichtbar.

### 3.5 Marktbeobachtung

```yaml
---
typ: marktbeobachtung
geschaeft: aa
erfasst_am: 2026-10-28
person: "Beispiel, Max"
unternehmen_neu: "[[Muster Automobile Nord]]"
unternehmen_alt: "[[Muster Automobile Sued]]"
rolle_neu: "Geschaeftsfuehrer"
anlass: wechsel                          # wechsel | neubesetzung | abgang | befoerderung
quelle: "Automobilwoche Personalien"
quelle_url: "https://..."
belegbar: true
relevanz: pipeline                       # pipeline | beobachten | irrelevant
kontakt_angelegt: false
---

## Belegte Fakten
## Fit-Einschaetzung
## Unsicherheiten
```

`belegbar` und `quelle_url` sind Pflicht, weil `aa-market-intelligence`
Belegbarkeit verlangt und Unbelegbares als unbekannt kennzeichnen muss. Der
Abschnitt `## Unsicherheiten` erzwingt dieselbe Disziplin im Fließtext.

`kontakt_angelegt` trennt Beobachtung von Pipeline-Aufnahme. Eine Beobachtung
wird nicht automatisch Kandidat; die Aufnahme ist Aarons Entscheidung.

---

## 4. Namenskonvention

| Entität | Muster | Beispiel |
|---------|--------|----------|
| Kontakt | `Nachname, Vorname` | `Beispiel, Erika.md` |
| Kontakt bei Dublette | `Nachname, Vorname (Unternehmen)` | `Beispiel, Max (Muster Nord).md` |
| Arbeitgeber | `Firmenname` | `Muster Automobile GmbH.md` |
| Mandat | `M-JJJJ-NNN Kuerzel Position` | `M-2026-001 Muster GF Vertrieb.md` |
| Ereignis | `JJJJ-MM-TT Nachname Kanal` | `2026-10-21 Beispiel termin.md` |
| Marktbeobachtung | `JJJJ-MM-TT Nachname Anlass` | `2026-10-28 Beispiel wechsel.md` |

Kontaktdateien tragen keine ID im Namen, weil der Dateiname in Obsidian der
Linktext ist: `[[Beispiel, Erika]]` liest sich, `[[K-0042]]` nicht. Mandate tragen
ein Aktenzeichen, weil sie Aktencharakter haben und über Jahre referenziert
werden.

Datumspräfix bei Ereignis und Marktbeobachtung, weil beide chronologisch
entstehen und die alphabetische Sortierung dann der zeitlichen entspricht.

---

## 5. Verlinkungslogik

```
Arbeitgeber  <--->  Kontakt          beidseitig (entscheider / unternehmen)
Mandat        -->   Arbeitgeber      einseitig (mandant)
Mandat       <--->  Kontakt          beidseitig (kandidaten / mandat)
Ereignis      -->   Kontakt          einseitig
Ereignis      -->   Arbeitgeber      einseitig
Marktbeob.    -->   Arbeitgeber      einseitig
Kontakt       -->   AA-Vertraulich   nur als Pseudonym-Kennung, kein Wikilink
```

**Beidseitig nur, wo beide Richtungen abgefragt werden.** Ein Arbeitgeber muss
seine Entscheider auflisten, ein Kontakt braucht seinen Arbeitgeber für die
Pipeline-Sicht. Ereignisse verlinken einseitig nach oben; die Rückrichtung
liefert Obsidians Backlink-Panel kostenlos und muss nicht gepflegt werden.

**Pflege-Regel:** Bei beidseitigen Beziehungen schreibt ein Skill immer beide
Seiten oder keine. Eine halb gepflegte Beziehung ist schlimmer als keine, weil
die Dataview-Sicht dann lügt, statt leer zu sein.

---

## 6. Sichten über Dataview

Voraussetzung: Community-Plugin **Dataview** installiert. Die Sichten liegen in
`00-Steuerung/Pipeline.md` und bilden die fünf Abschnitte aus
`aa-pipeline-review` eins zu eins ab.

### Abschnitt 1, Sofort dran (überfällig)

    ```dataview
    TABLE unternehmen AS "Unternehmen",
          naechste_aktion AS "Naechste Aktion",
          (date(today) - naechste_aktion_am).days AS "Tage ueberfaellig"
    FROM "10-Kontakte"
    WHERE typ = "kontakt" AND geschaeft = "aa"
      AND status != "abgesagt" AND naechste_aktion_am < date(today)
    SORT naechste_aktion_am ASC
    ```

### Abschnitt 2, Diese Woche

    ```dataview
    TABLE unternehmen AS "Unternehmen",
          naechste_aktion AS "Naechste Aktion",
          naechste_aktion_am AS "Zieldatum"
    FROM "10-Kontakte"
    WHERE typ = "kontakt" AND geschaeft = "aa"
      AND naechste_aktion_am >= date(today)
      AND naechste_aktion_am <= date(today) + dur(7 days)
    SORT naechste_aktion_am ASC
    ```

### Abschnitt 3, Bestätigte Pitch-Termine

    ```dataview
    TABLE unternehmen AS "Unternehmen",
          naechste_aktion_am AS "Termin",
          temperatur AS "Temperatur"
    FROM "10-Kontakte"
    WHERE typ = "kontakt" AND status = "pitch_terminiert"
    SORT naechste_aktion_am ASC
    ```

### Abschnitt 4, Ruhend

    ```dataview
    TABLE unternehmen AS "Unternehmen",
          naechste_aktion_am AS "Naechste Beruehrung"
    FROM "10-Kontakte"
    WHERE typ = "kontakt" AND status = "ruhend"
    SORT naechste_aktion_am ASC
    ```

### Abschnitt 5, Kernpipeline in Aarons Reihenfolge

    ```dataview
    TABLE pipeline_rang AS "Rang", temperatur AS "Temp",
          letzte_interaktion_am AS "Letzter Kontakt"
    FROM "10-Kontakte"
    WHERE welle = "kern" AND pipeline_rang
    SORT pipeline_rang ASC
    ```

### Zusatzsichten

Mandate nach Phase:

    ```dataview
    TABLE mandant, phase, fee_modell, ziel_platzierung_am
    FROM "30-Mandate"
    WHERE typ = "mandat" AND phase != "abgeschlossen"
    SORT ziel_platzierung_am ASC
    ```

Marktbeobachtungen, noch nicht entschieden:

    ```dataview
    TABLE person, unternehmen_neu, relevanz, quelle
    FROM "50-Markt"
    WHERE typ = "marktbeobachtung" AND relevanz = "pipeline"
      AND kontakt_angelegt = false
    SORT erfasst_am DESC
    ```

Kontakte ohne Berührung seit 30 Tagen (Leck-Erkennung):

    ```dataview
    TABLE unternehmen, letzte_interaktion_am, temperatur
    FROM "10-Kontakte"
    WHERE typ = "kontakt" AND status = "aktiv"
      AND letzte_interaktion_am < date(today) - dur(30 days)
    SORT letzte_interaktion_am ASC
    ```

**Dataview rechnet, Claude liest.** Begründung: Das stdio-Tool-Set kennt keinen
strukturierten Query. Lässt man Claude die Priorisierung aus Rohdateien
rekonstruieren, kostet das Tokens und ist nicht reproduzierbar. Dataview
erzeugt die Sicht deterministisch, Claude liest `Pipeline.md` und bewertet.
Rechnen ist Maschinenarbeit, Bewerten ist der Hebel.

---

## 7. Skill-Mapping

Welcher der sechs Skills liest und schreibt welche Felder. Das ist der Vertrag,
den `aa-obsidian-sync` einhalten muss.

| Skill | Liest | Schreibt |
|-------|-------|----------|
| `aa-pipeline-review` | `00-Steuerung/Pipeline.md`, alle Kontakte | nichts (reine Sicht) |
| `aa-follow-up` | betroffener Kontakt | `naechste_aktion`, `naechste_aktion_am`, `temperatur`, `letzte_interaktion_am`, neues Ereignis, Journal-Zeile |
| `aa-pitch-prep` | Arbeitgeber, Entscheider-Kontakte, `90-Playbooks` | nichts (Briefing bleibt in der Antwort) |
| `aa-mandate-kickoff` | Arbeitgeber, Playbooks, Fee-Modelle | neues Mandat, `phase: kickoff`, Verlinkung beim Mandanten |
| `aa-market-intelligence` | bestehende Kontakte (Dublettenprüfung) | neue Marktbeobachtung |
| `aa-weekly-review` | `Pipeline.md`, Ereignisse der Woche, `Wochenreview.md` | Journal-Zeile in `Wochenreview.md` |

**Nur `aa-follow-up` und `aa-mandate-kickoff` schreiben in Kontakte und
Mandate.** Die übrigen vier sind lesend oder schreiben nur in eigene Bereiche.
Begründung: Je weniger Skills denselben Datensatz schreiben, desto geringer die
Wahrscheinlichkeit widersprüchlicher Stände.

**Schreibregeln für jeden Skill:**

1. Vor dem Schreiben die Datei lesen. Niemals blind `vault_write`, weil das die
   Datei komplett ersetzt und Abschnitte verliert, die nicht im Kontext waren.
2. Historie nur per `append_content` unter `## Journal`. Format:
   `- 2026-10-21 (telefon) Kurzbeschreibung, Ergebnis.`
3. Frontmatter-Felder per `patch_content` einzeln ändern, nicht den ganzen
   Block neu schreiben.
4. `pipeline_rang` nie automatisch ändern.
5. Keine Datei verschieben, keine Datei löschen.
6. Bei fehlenden Pflicht-Überschriften: Überschrift anlegen, dann schreiben.
   Nicht an das Dateiende anhängen.

---

## 8. Offene Punkte

### 8.1 Die Assessment-Methodik fehlt

`aa-mandate-kickoff` und `aa-market-intelligence` verweisen beide auf ein
A/A-Assessment-SKILL.md mit Knock-out-Kriterien (angeführt von mangelnder
Integrität), sieben positiven Fitness-Signalen, drei Standard-Diagnosefragen und
gewichtetem Scoring von 0 bis 100. **Diese Datei existiert nicht.** Beide Skills
weisen korrekt an, in diesem Fall nicht zu improvisieren, sondern nachzufragen.

Folge für das Modell: Die Felder `assessment_score`, `assessment_stand`,
`knockout` und `knockout_grund` sind angelegt, bleiben aber leer, bis die
Methodik vorliegt. Sobald sie existiert, kommen die sieben Fitness-Signale als
eigene gewichtete Felder dazu; ein einzelner Score ohne die Achsen dahinter ist
nicht nachvollziehbar und damit im Zweifel wertlos.

Das Schließen dieser Lücke ist wertvoller als jede weitere Verfeinerung des
CRM. Zwei bestehende Skills laufen aktuell in eine Sackgasse.

### 8.2 Keine technische Durchsetzung der Vertraulichkeitsgrenze

Die Trennung in zwei Vaults ist belastbar, solange der zweite Vault nie
verbunden wird. Es gibt keinen technischen Mechanismus, der das erzwingt; es ist
eine Betriebsdisziplin. Wer den vertraulichen Vault einmal versehentlich im
MCP-Pfad konfiguriert, hat die Grenze geöffnet, ohne es zu merken.

### 8.3 Kein Auftragsverarbeitungsvertrag geklärt

Offen, ob der genutzte Claude-Tarif einen AV-Vertrag umfasst. Ohne ihn ist jede
Übermittlung personenbezogener Daten an die API rechtlich ungedeckt, unabhängig
davon, wie saubere Felder dieses Modell definiert.

### 8.4 Dublettenbehandlung gegen den Vibe-Export

`aa-pipeline-review` verlangt Deduplizierung der 50 C-suite-Kontakte gegen die
14er-Kernpipeline. Das Modell sieht `welle` vor, definiert aber keinen
Abgleich-Algorithmus. Namensgleichheit ist unzuverlässig (Schreibweisen,
Titel). Vorschlag für später: Abgleich über `person` plus `unternehmen`, mit
manueller Bestätigung bei Teilübereinstimmung.
