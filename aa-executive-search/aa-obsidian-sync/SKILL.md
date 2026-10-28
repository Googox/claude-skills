---
name: aa-obsidian-sync
description: Vault-Zugriffsschicht für A/A Executive Search. Liest den Obsidian-Vault als Wissensbasis vor jeder Analyse und schreibt Arbeitsergebnisse strukturiert zurück, mit korrektem Frontmatter, Verlinkung und Ablageort. Nutze diesen Skill immer, wenn Aaron Vault-Daten braucht oder Ergebnisse dort landen sollen: bei "in den Vault", "aus dem Vault", "Kontakt anlegen", "Status aktualisieren", "Pipeline einlesen", "Notiz speichern", oder vor und nach jedem Pipeline-Review, Follow-up, Pitch-Briefing, Mandats-Kickoff, Marktbeobachtungs- und Wochenreview-Durchlauf. Arbeitet ausschließlich mit den sieben portablen MCP-Tools, damit Claude Desktop und Claude Code CLI identisches Verhalten zeigen.
---

# A/A Obsidian-Sync

Zweck: Obsidian ist Single Source of Truth, nicht ein Ausgabekanal. Dieser Skill
ist die einzige Stelle, an der Vault-Lese- und Schreiboperationen definiert sind.
Alle anderen A/A-Skills bleiben unverändert; sie erzeugen Inhalte, dieser Skill
bringt sie an den richtigen Ort und holt den Stand vorher ab.

Datenmodell: `documentation/implementation/obsidian-vault-datenmodell.md`. Dieser
Skill setzt es um, definiert es nicht neu. Bei Widerspruch gewinnt die
Spezifikation.

## Abhängigkeitsrichtung

Dieser Skill kennt die sechs A/A-Fachskills. Keiner der sechs kennt ihn.

Begründung: Die Repo-Konvention verlangt self-contained Skills ohne
Inter-Skill-Abhängigkeiten. Eine einheitliche Vault-Ausgabe für sechs Skills ist
aber per Definition eine Kopplung. Die Auflösung ist die Richtung: Fällt dieser
Skill weg, funktionieren alle sechs weiter wie vorher und geben ihre Ergebnisse
in der Antwort aus. Nur die Persistenz fehlt dann. Kein Fachskill referenziert
diesen hier, also bricht keiner.

## Werkzeugbasis: sieben Tools, nicht achtzehn

Claude Desktop lädt nur stdio-Prozesse, Claude Code CLI kann HTTP. Das ergibt
zwei unterschiedliche Tool-Sets. Dieser Skill nutzt ausschließlich die
Schnittmenge, damit beide Clients identisch arbeiten:

`list_files_in_vault`, `list_files_in_dir`, `get_file_contents`, `search`,
`patch_content`, `append_content`, `delete_file`

Nicht verwenden, auch wenn verfügbar: `vault_move`, `vault_copy`, `tag_list`,
`command_execute`. Wer sie nutzt, baut einen Skill, der im Desktop bricht.

`delete_file` wird nie aufgerufen. Löschen bleibt eine manuelle Entscheidung.

## Ablauf Lesen: vor jeder Analyse

Immer zuerst lesen, dann denken. Ein Skill, der ohne Vault-Stand analysiert,
erfindet Kontext, den der Vault schon hat.

| Fachskill | Vorher zu lesen |
|-----------|-----------------|
| Pipeline-Review | `00-Steuerung/Pipeline.md`, dann die Kontaktdateien der dort gelisteten Namen |
| Follow-up | Kontaktdatei des Gesprächspartners, Arbeitgeberdatei, letzte drei Ereignisse |
| Pitch-Prep | Arbeitgeberdatei, alle verlinkten Entscheider, `90-Playbooks/` |
| Mandats-Kickoff | Arbeitgeberdatei, `00-Steuerung/Ziele.md`, Assessment-Methodik |
| Marktbeobachtung | Dublettenprüfung: `search` nach Nachname in `10-Kontakte` |
| Wochenreview | `00-Steuerung/Pipeline.md`, `00-Steuerung/Wochenreview.md`, Ereignisse der Woche |

Leseregeln:

1. `00-Steuerung/Pipeline.md` ist die Vorrechnung, nicht die Rohdaten. Dataview
   hat dort schon priorisiert. Nie die Priorisierung aus Einzeldateien
   rekonstruieren, das kostet Tokens und ist nicht reproduzierbar.
2. Dateien einzeln per `get_file_contents` holen, nie den ganzen Ordner.
3. Fehlt eine erwartete Datei, das benennen und nicht raten.
4. `AA-Vertraulich` wird nie gelesen. Steht in einem Kontakt ein
   `vertraulich_ref`, ist das ein Hinweis an Aaron, nicht ein Leseauftrag.

## Ablauf Schreiben: nach jedem Ergebnis

Acht Regeln, verbindlich. Sie stammen aus Abschnitt 7 der Spezifikation.

1. **Vor dem Schreiben die Datei lesen.** Nie blind schreiben, das ersetzt die
   Datei und verliert Abschnitte, die nicht im Kontext waren.
2. **Historie nur per `append_content` unter `## Journal`.** Format:
   `- JJJJ-MM-TT (kanal) Kurzbeschreibung, Ergebnis.`
3. **Frontmatter-Felder einzeln per `patch_content` ändern**, nie den ganzen
   Block neu schreiben.
4. **Statusfelder überschreiben, nicht nur füllen.** `status`, `temperatur`,
   `assessment_stand`, `letzte_interaktion_am`, `naechste_aktion`,
   `naechste_aktion_am` tragen immer einen Vorgabewert, sind also nie leer. Eine
   Logik, die nur Lücken füllt, hinterlässt einen Score von 86 neben
   `assessment_stand: nicht_bewertet`.
5. **Zusammengehörende Felder gemeinsam schreiben.** `assessment_score` nur mit
   allen sieben `sig_*` und dem passenden `assessment_stand`. `naechste_aktion`
   nur mit `naechste_aktion_am`.
6. **`pipeline_rang` nie automatisch ändern.** Die Reihenfolge ist von Aaron
   gesetzt und wird nicht neu verhandelt.
7. **Keine Datei verschieben, keine Datei löschen.** Status lebt im Frontmatter.
8. **Fehlt eine Pflicht-Überschrift**, erst die Überschrift anlegen, dann
   schreiben. Nie an das Dateiende anhängen.

Beidseitige Beziehungen immer vollständig oder gar nicht: Wird ein Kontakt mit
einem Arbeitgeber verknüpft, erhält der Arbeitgeber denselben Kontakt in
`entscheider`. Eine halb gepflegte Beziehung lässt die Dataview-Sicht lügen,
statt leer zu sein.

## Schreibrechte je Fachskill

Nur zwei Skills schreiben in Kontakte und Mandate. Je weniger Schreiber auf
einem Datensatz, desto geringer die Chance widersprüchlicher Stände.

| Fachskill | Darf schreiben |
|-----------|----------------|
| Follow-up | Kontakt: `naechste_aktion`, `naechste_aktion_am`, `temperatur`, `letzte_interaktion_am`, Journal-Zeile. Neues Ereignis in `40-Ereignisse` |
| Mandats-Kickoff | Neues Mandat in `30-Mandate`, `phase: kickoff`, Rückverlinkung beim Arbeitgeber |
| Marktbeobachtung | Neue Datei in `50-Markt`. Kein Kontakt, keine Pipeline-Aufnahme |
| Wochenreview | Journal-Zeile in `00-Steuerung/Wochenreview.md` |
| Pipeline-Review | nichts |
| Pitch-Prep | nichts |

Pipeline-Review und Pitch-Prep sind bewusst lesend. Ein Review, das im Lesen
Daten verändert, macht die Vorher-Nachher-Betrachtung unmöglich.

## Ereignis oder Journal-Zeile

Trennlinie: Was bewertet werden muss, wird ein Ereignis mit eigener Datei. Was
nur dokumentiert wird, wird eine Journal-Zeile im Kontakt.

Eigene Datei: Gespräch, Termin, Pitch, Mandatsgespräch, Referenzauskunft.
Journal-Zeile: kurze Mail, Erinnerung, Terminabsage, Rückruf ohne Erreichen.

Begründung: Bei rund 64 Kontakten und wöchentlichen Berührungen erzeugt ein
Ereignis pro Mail mehrere hundert Dateien im Jahr, von denen die meisten nie
abgefragt werden.

## Neue Dateien anlegen

1. Vorlage aus `80-Vorlagen/` per `get_file_contents` holen.
2. Frontmatter füllen, unbekannte Felder leer lassen, nicht erfinden.
3. Unter `## Offene Punkte` auflisten, was noch von Aaron kommen muss.
4. Dateiname nach Konvention: Kontakt `Nachname, Vorname`, Arbeitgeber
   `Firmenname`, Mandat `M-JJJJ-NNN Kuerzel Position`, Ereignis
   `JJJJ-MM-TT Nachname Kanal`, Marktbeobachtung `JJJJ-MM-TT Nachname Anlass`.
5. Ist der Vorname unbekannt, nur den Nachnamen verwenden und das Ergänzen
   unter `## Offene Punkte` vermerken. Keine Vornamen erfinden.
6. Beidseitige Verlinkung auf der Gegenseite nachtragen.

## Grenzen

Dieser Skill schreibt nie in `AA-Vertraulich` und liest dort nie. Der Vault ist
nicht verbunden; ein Zugriffsversuch wäre ein Konfigurationsfehler, kein
Arbeitsschritt.

Keine Werte erfinden, um ein Schema zu vervollständigen. Ein leeres Feld mit
Eintrag unter `## Offene Punkte` ist besser als ein plausibel geratenes.

Keine Massenoperation ohne Rückfrage. Mehr als fünf Dateien in einem Durchlauf
ändern nur nach ausdrücklicher Bestätigung durch Aaron.

Bricht eine Schreiboperation ab, den Teilzustand benennen. Eine halb geschriebene
beidseitige Verknüpfung ist ein Fehler, der genannt werden muss.

## Firmenname

Immer "A/A Executive Search" mit Schrägstrich, nie mit Und-Zeichen.

## Trennung

Ausschließlich A/A Executive Search. Alle Dateien tragen `geschaeft: aa`. Keine
Vermischung mit Alexandras separaten Geschäftsideen.
