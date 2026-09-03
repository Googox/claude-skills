---
name: aa-candidate-profile
description: Kandidaten-Steckbrief für A/A Executive Search. Wandelt einen hochgeladenen Lebenslauf (PDF, DOCX, Text) plus optionale Interviewnotizen in ein strukturiertes, präsentationsfähiges Kandidatenprofil für den beauftragenden Arbeitgeber, wahlweise als Vollprofil mit Namen (Shortlist) oder als anonymisiertes Blindprofil (Erstansprache). Nutze diesen Skill immer, wenn Aaron "Steckbrief", "Kandidatenprofil", "Profil erstellen", "Lebenslauf aufbereiten", "CV zusammenfassen", "Shortlist-Profil", "Blindprofil", "Kandidatenpräsentation" erwähnt oder einen Lebenslauf hochlädt.
---

# A/A Kandidaten-Steckbrief

Zweck: Der Steckbrief ist das sichtbarste Produkt der Suche. Der Kunde sieht selten die Recherche, immer aber das Profil. Ein Lebenslauf beschreibt, was ein Mensch getan hat. Ein Steckbrief beantwortet die einzige Frage, die der Auftraggeber hat: Warum genau dieser Mensch für genau diese Position. Die Übersetzung von der einen in die andere Form ist die Beratungsleistung, nicht das Abtippen.

## Eingaben

Pflicht: der Lebenslauf als Datei (PDF, DOCX, Bilddatei mit lesbarem Text) oder als eingefügter Text.

Qualitätsentscheidend, wenn vorhanden: das schriftliche Anforderungsprofil oder die Stellenbeschreibung des Auftraggebers als Datei oder Text. Weiter optional: Aarons Interviewnotizen, Gehaltsrahmen und Kündigungsfrist, Wechselmotiv, Zeugnisse, Referenzstand.

Fehlt das Anforderungsprofil, den Steckbrief trotzdem erstellen, aber Block 6 als offenes Feld ausweisen und Aaron einmal fragen, ob er das Profil nachreichen kann. Nicht raten, welche Position gemeint ist und keine Anforderungen erfinden.

Vertraulichkeit des Auftraggebers: der Name des suchenden Hauses ist selbst schutzwürdig. Dass dieses Unternehmen eine Position besetzt, ist vertrauliche Marktinformation. In der lokalen Anwendung wird er deshalb mit pseudonymisiert und erst lokal wieder eingesetzt.

## Zwei Modi

Modus "vollprofil" ist der Standard für die Shortlist-Präsentation beim beauftragenden Arbeitgeber: Klarname, Arbeitgeber im Klartext, vollständige Kontaktdaten optional. Setzt die dokumentierte Freigabe des Kandidaten voraus.

Modus "blindprofil" ist für die Erstansprache und für Mandate vor Freigabe: kein Name, keine Arbeitgebernamen, stattdessen typisierte Beschreibungen wie "Premium-Handelsgruppe, Süddeutschland, rund 450 Mitarbeitende, rund 380 Millionen Euro Umsatz". Auch Studienort, seltene Nischenpositionen und eindeutige Jahreszahlen können re-identifizieren, daher gröber fassen. Vor Ausgabe prüfen: Ist der Kandidat aus diesem Profil im DACH-Premiumhandel erkennbar? Wenn ja, weiter abstrahieren und Aaron darauf hinweisen.

Wenn Aaron den Modus nicht nennt, nachfragen. Nicht raten. Die falsche Wahl ist entweder ein Vertraulichkeitsbruch oder ein wertloses Profil.

## Ablauf

Schritt 1, Lebenslauf extrahieren. Datei mit dem passenden Skill lesen (pdf für PDF, docx für Word). Alle Stationen, Zeiträume, Titel, Ausbildung, Sprachen, Zertifikate erfassen. Zeitliche Lücken über drei Monate markieren, nicht verschweigen und nicht wegrunden.

Schritt 2, Fakten von Behauptungen trennen. Was steht belegt im Lebenslauf, was ist Selbstbeschreibung des Kandidaten, was stammt aus Aarons Interview, was ist Aarons eigene Einschätzung. Diese vier Quellen im Steckbrief unterscheidbar halten. Der Kunde muss erkennen können, worauf eine Aussage beruht.

Schritt 3, Erfolge quantifizieren. Für jede relevante Station zwei bis drei messbare Ergebnisse suchen: Umsatz, Ertrag, Stückzahlen, Führungsspanne, Standortzahl, Turnaround, Aufbauleistung. Stehen keine Zahlen im Lebenslauf, keine erfinden. Stattdessen als offene Frage in Block 9 aufnehmen, das ist Interviewstoff.

Schritt 4, Gegen das Anforderungsprofil spiegeln. Liegt ein schriftliches Anforderungsprofil des Auftraggebers vor, wird es zerlegt und Punkt für Punkt gegen den Werdegang gelegt. Jede Anforderung wird im Wortlaut des Auftraggebers übernommen, nicht umformuliert, und in Muss- und Kann-Kriterien getrennt. Diese Trennung ist der eigentliche Hebel: ein gerissenes Kann-Kriterium hält den Kandidaten im Rennen, ein gerissenes Muss-Kriterium nicht. Auftraggeber vermischen beides regelmäßig im selben Absatz, und wer die Liste sauber trennt, führt das Briefinggespräch.

Status je Anforderung: erfüllt, teilweise erfüllt, nicht erfüllt, jeweils mit einer Zeile Beleg aus dem Lebenslauf. Nicht erfüllte Punkte gehören in den Steckbrief, nicht in die Schublade. Ein Profil ohne Schwachstellen ist unglaubwürdig und beschädigt Aarons Ruf beim ersten Interview. Block 6 schließt mit einer Abgleichszeile, die zählt, wie viele Anforderungen erfüllt sind, und die nicht erfüllten Muss-Kriterien einzeln benennt.

Liegt kein schriftliches Profil vor, danach fragen. Ein Mandat ohne schriftliches Anforderungsprofil ist ein Mandat mit beweglichen Zielen, und die Beweglichkeit geht immer zulasten des Beraters.

Schritt 5, A/A-Assessment anwenden. Die Bewertung folgt Aarons proprietärer Methodik: Knock-out-Kriterien angeführt von mangelnder Integrität, sieben positive Fitness-Signale, gewichtetes Scoring null bis hundert, Kandidat-zu-JD-Matching. Diese Kriterien liegen im separaten A/A-Assessment-SKILL.md. Sie nicht erfinden. Das SKILL.md laden und anwenden. Liegt es nicht vor, Aaron bitten, es beizulegen, und den Steckbrief zunächst ohne den Scoring-Block ausliefern statt mit ausgedachten Achsen.

Schritt 6, Compliance-Prüfung vor Ausgabe. Der Prüflauf in references/agg-dsgvo-leitplanken.md ist verpflichtend, ebenso `scripts/steckbrief_build.py --check`. Findet die Prüfung ein unzulässiges Merkmal, entfernen und Aaron benennen, was entfernt wurde.

Schritt 7, Ausgabe. Kopierfreundlich als Fließtext-Blöcke, geeignet für Word und PowerPoint. Wenn Aaron eine Datei will, den docx-Skill für das Einseiten-Layout nutzen.

## Offene Felder statt Fehlstellen

Fehlt eine Angabe, steht dort niemals ein entschuldigender Satz wie "im Lebenslauf nicht angegeben", sondern ein offenes Feld mit konkreter Ausfüllanweisung. Im Text wird es als doppelte eckige Klammer geschrieben, im Word-Dokument erscheint es grün hinterlegt und kursiv. Beispiel: [[Umsatz- und Ergebnisverantwortung in Euro ergänzen]].

Der Grund ist praktisch. Ein grünes Feld ist eine Arbeitsanweisung an sich selbst und an den Kandidaten, ein entschuldigender Satz ist eine Kapitulation im fertigen Dokument. Der Steckbrief wird damit zum Arbeitsstand, den man im Interview abarbeitet, statt zu einer Liste dessen, was fehlt.

Die Prüfung zählt die offenen Felder und meldet sie als Hinweis. Ein leerer Pflichtblock ist deshalb kein Fehler, sondern eine Warnung: er erscheint als grünes Feld. Fehler bleiben den harten Verstößen vorbehalten, also unzulässigen Merkmalen, fehlender Einwilligung und Klartext im Blindprofil. Vor dem Versand an den Auftraggeber ist jedes grüne Feld auszufüllen oder die Zeile zu streichen.

## Aufbau des Steckbriefs

Block 1, Kopf: Mandat und Position, Auftraggeber, Profil-ID, Datum, Berater, Vertraulichkeitsvermerk, Modus (Vollprofil oder Blindprofil).

Block 2, Executive Summary: drei bis fünf Sätze. Wer ist der Mensch beruflich, was ist seine stärkste Passung zu diesem Mandat, wo liegt der größte Vorbehalt. Diese fünf Sätze entscheiden, ob der Kunde weiterliest. Sie werden zuletzt geschrieben und zuerst gelesen.

Block 3, Eckdaten: Jahrgang nur mit Einwilligung, Wohnregion, Mobilität und Umzugsbereitschaft, Sprachen mit Niveau, Führungsspanne, Budget- oder Ergebnisverantwortung, Verfügbarkeit, Kündigungsfrist.

Block 4, Werdegang: rückwärts chronologisch. Pro Station Zeitraum, Unternehmen mit Größenprofil, Rolle, Verantwortungsumfang, zwei bis drei messbare Erfolge. Lücken über drei Monate ausgewiesen und, wo bekannt, erklärt.

Block 5, Kompetenzprofil: Fachkompetenz, Führungskompetenz, Branchenkompetenz. Je Achse belegt statt behauptet, also mit Verweis auf die Station, an der sie erworben wurde.

Block 6, Passung zum Mandat: Anforderung für Anforderung im Wortlaut des Auftraggebers, mit Kennzeichnung Muss oder Kann, Status erfüllt, teilweise, nicht erfüllt und jeweils einer Zeile Beleg. Abschließend die Abgleichszeile mit der Zählung und den nicht erfüllten Muss-Kriterien.

Block 7, A/A-Assessment: Knock-out-Check, Fitness-Signale, gewichteter Score. Nur wenn die Methodik vorliegt.

Block 8, Motivation und Wechselgrund: was den Kandidaten treibt, was er sucht, warum er jetzt wechselt. Aus dem Interview, klar als Selbstauskunft gekennzeichnet.

Block 9, Risiken und offene Punkte: ehrlich. Lücken, fehlende Nachweise, Gehaltsdelta, Standortfrage, kurze Verweildauern, ungeklärtes Wettbewerbsverbot. Dazu die Fragen, die im nächsten Gespräch zu klären sind.

Block 10, Empfehlung des Beraters: klare Position mit Begründung. Vorstellen, mit Vorbehalt vorstellen, oder nicht vorstellen. Kein Sowohl-als-auch.

## Finalisierung und Freigabe

Der Steckbrief hat zwei Zustaende. Arbeitsstand ist die Word-Datei mit gruenen Feldern, damit wird im Interview gearbeitet. Freigabedokument ist das PDF, das beim Auftraggeber landet. Das PDF entsteht nur, wenn das Freigabe-Gate haelt.

Das Gate prueft vier Punkte: kein offenes gruenes Feld mehr, kein Compliance-Fehler aus der AGG- und DSGVO-Pruefung, dokumentierte Einwilligung des Kandidaten fuer diesen Auftraggeber, und ein eindeutiges Votum in Block 10. Faellt einer dieser Punkte durch, wird kein Freigabe-PDF erzeugt, sondern die Liste der offenen Punkte ausgegeben.

Ein Entwurfs-PDF ist trotzdem moeglich, etwa zur Abstimmung mit dem Kandidaten. Es traegt in der Fusszeile jeder Seite den Vermerk "ENTWURF, nicht freigegeben" und im Dateinamen das Kuerzel ENTWURF. Ein Entwurf geht nie an den Auftraggeber.

Jede PDF-Seite traegt eine Fusszeile mit Vertraulichkeitsvermerk, Firmenname, Profil-ID, Datum und Seitenzaehlung. Damit bleibt ein einzelnes ausgedrucktes Blatt zuordenbar.

Auf der Kommandozeile: `scripts/steckbrief_build.py profil.json --freigabe` prueft nur das Gate, `--pdf datei.pdf` erzeugt das Freigabe-PDF, `--entwurf` erlaubt den Entwurf, `--docx datei.docx` den Arbeitsstand. In der lokalen Anwendung uebernimmt das Schritt 6.

## Ehrlichkeit

Nichts erfinden. Keine Zahlen, keine Titel, keine Erfolge, keine Zertifikate, die nicht im Lebenslauf oder in den Notizen stehen. Nicht glättende Formulierungen für harte Fakten wählen: aus drei Stationen in vier Jahren wird nicht "dynamischer Werdegang", sondern "drei Stationen in vier Jahren, Wechselgründe im Interview zu klären". Ein Steckbrief, der beim ersten Kundeninterview auffliegt, kostet das Mandat und die Beziehung. Unsicheres als unsicher ausweisen.

## Firmenname

Immer "A/A Executive Search" mit Schrägstrich in allen Dokumenten und Antworten.

## Trennung

Kandidatendaten aus diesem Skill gehören ausschließlich zu A/A Executive Search. Keine Vermischung mit Alexandras separaten Geschäftsideen.

## Dateien in diesem Skill

references/steckbrief-methodik.md, Aufbau, Formulierungsregeln, Qualitätskriterien, Anti-Muster.
references/agg-dsgvo-leitplanken.md, verpflichtende Prüfliste vor jeder Ausgabe.
assets/steckbrief-template.md, leere Vorlage zum Ausfüllen.
assets/steckbrief-beispiel.md, ausgefülltes Beispiel mit fiktivem Kandidaten.
assets/kandidat-beispiel.json, Eingabestruktur für das Skript.
assets/aa-candidate-profile-chat-SKILL.md, eigenständige Chat-Fassung dieses Skills zum Installieren als persönlicher Skill. Ohne Skript- und Dateiabhängigkeiten, für Testläufe und eigenes Material. Für echte Mandate bleibt die lokale Anwendung der Produktionsweg.
scripts/anforderungen.py, zerlegt ein schriftliches Anforderungsprofil in prüfbare Punkte und trennt Muss von Kann.
scripts/steckbrief_build.py, erzeugt Steckbrief aus JSON, prüft Vollständigkeit und AGG-Merkmale, Freigabe-Gate, Word- und PDF-Export.
scripts/docx_writer.py, minimaler Word-Schreiber für den Arbeitsstand mit grünen Feldern.
scripts/pdf_writer.py, minimaler PDF-Schreiber für das Freigabedokument.

## Lokale Anwendung

Für die datenschutzsensible Bearbeitung am eigenen Rechner liegt in `app/` ein lokaler Arbeitsplatz. Er liest den Lebenslauf lokal, pseudonymisiert Namen, Arbeitgeber, Orte und Kontaktdaten, erzeugt daraus den Prompt, setzt die Klardaten nach der Textstufe lokal wieder ein, prüft das Ergebnis gegen die Leitplanken und exportiert eine Word-Datei samt Mailentwurf. Start unter Windows über `app/Steckbrief-starten.bat`, Details in `app/README.md`.

Wenn Aaron nach der lokalen Verarbeitung, nach Datenschutz beim Steckbrief oder nach dem Versand an den Auftraggeber fragt, auf diese Anwendung verweisen statt den Lebenslauf im Chat zu verarbeiten.
