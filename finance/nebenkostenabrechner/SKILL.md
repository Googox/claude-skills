# Nebenkostenabrechner (Betriebskostenabrechnung Wohnimmobilie)

Erstellt eine formal saubere, prüfbare Betriebskostenabrechnung für vermietete
Wohneinheiten nach § 2 BetrKV und HeizkostenV — inklusive Umlageschlüsseln,
Zeitanteilen bei Mieterwechsel, CO2-Kostenaufteilung und druckfertigem
Mieterdokument.

**Zielgruppe:** private Vermieter mit ein bis acht Einheiten, die ohne
Hausverwaltung abrechnen und dabei die Ausschlussfrist des § 556 Abs. 3 BGB
sowie die Umlagefähigkeitsgrenzen des § 1 Abs. 2 BetrKV sicher einhalten wollen.

**Kein Rechtsrat.** Der Skill rechnet und strukturiert. Die Prüfung der
Mietvertragsklauseln, des Wirtschaftlichkeitsgebots und der Abrechnungsformalien
im Einzelfall bleibt beim Vermieter bzw. dessen Steuerberater oder
Mietrechtsanwalt.

## Bestandteile

| Datei | Zweck |
|-------|-------|
| `assets/nebenkosten-dashboard.html` | Interaktives Dashboard als Artifact-Fragment. Jahresakten, Kostenkatalog, Heizkostenmodul, Charts, druckfertige Mieterabrechnung, CSV-Export, Sicherung als JSON. |
| `assets/nebenkostenabrechner.html` | Generierte Standalone-Datei für den Offline-Betrieb per Doppelklick. Wird von `scripts/build-standalone.py` erzeugt, nicht von Hand bearbeiten. |
| `scripts/build-standalone.py` | Ergänzt das Artifact-Fragment um die HTML-Hülle, die der Viewer sonst beisteuert. |
| `scripts/nebenkosten.py` | CLI-Rechner ohne externe Abhängigkeiten. Liest eine JSON-Akte, gibt Abrechnung als Text, JSON oder CSV aus. |
| `references/betriebskosten-recht.md` | Wissensbasis: 17 Positionen der BetrKV, nicht umlagefähige Kosten, Fristen, HeizkostenV, CO2KostAufG. |
| `references/umlageschluessel.md` | Auswahl und Begründung des richtigen Umlagemaßstabs je Kostenart. |
| `assets/objekt-vorlage.json` | Leere Jahresakte zum Ausfüllen. |
| `assets/beleg-checkliste.md` | Checkliste vor dem Versand an den Mieter. |

## Workflow 1 — Jahresabrechnung erstellen

1. `assets/objekt-vorlage.json` kopieren, Stammdaten und Einheiten eintragen
   (Wohnfläche, Personenzahl, Kaltmiete, Vorauszahlungen, Nutzungszeitraum).
2. Belege des Abrechnungszeitraums sortieren, Beträge je BetrKV-Position
   eintragen, jeweils mit Beleg-Nummer.
3. Heizungsblock füllen: Brennstoff, Betriebsstrom, Wartung, Messdienst,
   Schornsteinfeger. Grundkostenanteil zwischen 30 und 50 Prozent wählen.
4. `python3 scripts/nebenkosten.py akte.json --format text` ausführen.
5. Ergebnis gegen `assets/beleg-checkliste.md` prüfen.
6. Abrechnung dem Mieter **nachweisbar** zustellen, spätestens zwölf Monate
   nach Ende des Abrechnungszeitraums.

## Workflow 2 — Dashboard für laufende Erfassung

1. `assets/nebenkosten-dashboard.html` als Artifact publizieren
   (Capabilities `db` und `downloads`).
2. Belege unterjährig direkt eintragen statt am Jahresende zu rekonstruieren.
3. Die Jahresakte wird serverseitig gespeichert; jede Periode liegt unter
   `abrechnungen/<jahr>`.
4. Am Jahresende Register „Abrechnung“ öffnen, drucken oder als CSV
   an den Steuerberater übergeben.

## Workflow 3 — Offline auf dem eigenen Rechner betreiben

1. `python3 scripts/build-standalone.py` ausführen oder `assets/nebenkostenabrechner.html`
   direkt herunterladen.
2. Datei in einen festen Ordner legen, etwa `Dokumente/Haus/Nebenkosten`, und per
   Doppelklick im Browser öffnen. Keine Installation, kein Server, kein Internet nötig.
3. Eingaben werden im Browserspeicher gehalten. Dieser überlebt Neustarts, aber nicht
   das Löschen der Browserdaten, einen Browserwechsel oder einen neuen Rechner.
4. Nach jeder Sitzung **Sichern** klicken. Die erzeugte Datei
   `Nebenkosten-Sicherung-JJJJ-MM-TT.json` enthält alle Jahresakten.
5. Mit **Laden** den Stand auf einem beliebigen Rechner wiederherstellen.
6. Je Abrechnungsjahr einen Ordner mit PDF-Druck, CSV-Export, JSON-Sicherung und
   gescannten Belegen führen. Das trägt Belegeinsicht und Betriebsprüfung.

**Verifiziert:** Der vollständige Zyklus aus Eingabe, Sichern, Löschen des
Browserspeichers und Laden wurde über das `file://`-Protokoll in Chromium getestet.
Ohne Internet lädt lediglich die Webschrift nicht; die Anwendung rechnet unverändert.

## Workflow 4 — Abrechnung durch einen Messdienst übernehmen

1. Im Register „Heizung“ den Schalter **Messdienst rechnet ab** setzen.
2. Eigene Kostenseite trotzdem vollständig erfassen: Brennstoff aus der
   Bestandsrechnung, Betriebsstrom, Wartung, Messdienstgebühr, Schornsteinfeger.
   Diese Seite ist die Prüfgröße, nicht Dekoration.
3. Endbeträge je Wohnung aus der Messdienstabrechnung in die Spalten
   „Heizung € laut Messdienst“ und „Warmwasser € laut Messdienst“ übertragen.
4. Den Summenabgleich lesen. Weicht der verteilte Betrag um mehr als ein Prozent
   von der eigenen Kostenseite ab, erst klären, dann abrechnen.
5. Datum der Zählerinbetriebnahme eintragen. Liegt es im Abrechnungszeitraum,
   warnt das Dashboard vor der Zweiteilung und der Gradtagzahlen-Aufteilung;
   liegt es danach, weist es auf das 15-Prozent-Kürzungsrecht hin.

## Workflow 5 — Leerstand und unterjähriger Mieterwechsel

1. Je Einheit das Einzugs- und gegebenenfalls Auszugsdatum in die Felder
   „Nutzung von“ und „Nutzung bis“ eintragen. Leer lassen bedeutet: volle Dauer.
2. Liegt das Einzugsdatum nach dem Ende des Abrechnungszeitraums, zählt die
   Einheit als nicht vermietet und erhält keine Abrechnung.
3. Der Leerstandsanteil wird auf der Übersicht ausgewiesen und nicht auf die
   übrigen Mieter verteilt. Er bleibt beim Eigentümer.
4. Vermietungsabsicht für die Leerstandszeit dokumentieren, damit die Kosten
   steuerlich als Werbungskosten anerkannt werden.
5. Für verbrauchsabhängige Positionen beim Wechsel eine Zwischenablesung
   veranlassen; eine Zeitanteilung ist dort nur zweite Wahl.

## Workflow 6 — Ölabrechnung über die Bestandsrechnung

1. Tankpeilung zum Ende des Abrechnungszeitraums dokumentieren (Datum, Foto).
2. Anfangsbestand in Litern und Euro aus der Vorjahresabrechnung übernehmen.
3. Alle Öllieferungen des Zeitraums mit Liter, Betrag und Beleg erfassen.
4. Bewertungsmethode wählen (gewogener Durchschnitt oder FIFO) und über die Jahre
   beibehalten.
5. Der errechnete Verbrauchswert ersetzt die Brennstoffkosten. Der Endbestandswert
   wird beim Anlegen der nächsten Jahresakte automatisch vorgetragen.

## Workflow 7 — Angehörigenvermietung absichern

1. Betroffene Einheit im Register „Objekt“ markieren.
2. Ortsübliche Kaltmiete je Quadratmeter aus dem örtlichen Mietspiegel eintragen
   und die Quelle für das jeweilige Jahr ablegen.
3. Quote gegen die ortsübliche Warmmiete prüfen: ab 66 Prozent voller
   Werbungskostenabzug, zwischen 50 und 66 Prozent Totalüberschussprognose,
   unter 50 Prozent anteiliger Abzug.
4. Die Quote wird mit und ohne Nebenkostenumlage ausgewiesen. Die Differenz zeigt,
   welchen Beitrag die Abrechnung zur steuerlichen Absicherung leistet.
5. Prüfung jährlich wiederholen — die ortsübliche Miete steigt, die vereinbarte nicht.

## Workflow 8 — Vorauszahlungen anpassen

1. Nach jeder Abrechnung prüfen, ob die Nachzahlung 25 Prozent der geleisteten
   Vorauszahlung übersteigt.
2. Ist das der Fall, Vorauszahlung nach § 560 Abs. 4 BGB auf ein Zwölftel der
   tatsächlichen Jahreskosten anheben. Das Dashboard weist den Wert je Einheit aus.
3. Anpassung schriftlich und unter Bezug auf die Abrechnung erklären; sie wirkt
   ab dem auf die Erklärung folgenden Monat.

## Workflow 9 — Streitfall Belegeinsicht

1. Der Mieter hat Anspruch auf Einsicht in die Originalbelege.
2. Beleg-Nummern aus dem Kostenkatalog gegen die abgelegten Rechnungen prüfen.
3. Termin anbieten, Einsicht dokumentieren. Kopien nur gegen Kostenerstattung
   und nur, wenn Einsicht am Ort unzumutbar ist.

## Qualitätskriterien

- Jede umgelegte Position ist einer BetrKV-Ziffer und einem Beleg zugeordnet.
- Der Umlageschlüssel ist je Position benannt und über die Jahre konstant.
- Heizkosten sind zu 50 bis 70 Prozent verbrauchsabhängig verteilt.
- Der CO2-Vermieteranteil ist vor der Umlage abgezogen.
- Bei Öl ist der Verbrauch aus der Bestandsrechnung angesetzt, nicht die Tankrechnung.
- Bei Angehörigenvermietung ist die Quote gegen die ortsübliche Warmmiete belegt.
- Nicht umlagefähige Kosten sind erfasst, aber nicht verteilt.
- Die Abrechnung ist innerhalb der Zwölfmonatsfrist zugegangen.
- Nach jeder Sitzung liegt eine JSON-Sicherung außerhalb des Browserspeichers.
- Der Leerstandsanteil ist ausgewiesen und bleibt beim Eigentümer.

## Anti-Patterns

- Instandhaltung, Reparaturen oder Verwaltungskosten in die Umlage nehmen.
- „Sonstige Betriebskosten“ umlegen, ohne sie im Mietvertrag konkret zu benennen.
- Umlageschlüssel zwischen zwei Jahren ohne sachlichen Grund wechseln.
- Kabel-TV weiterhin über § 2 Nr. 15 BetrKV abrechnen (Privileg zum 30.06.2024 entfallen).
- Die Abrechnung erst am letzten Tag der Frist versenden — maßgeblich ist der Zugang.
- Bei Öl die Tankrechnung statt des Verbrauchs umlegen.
- Anschaffungskosten gekaufter Messgeräte als Betriebskosten umlegen.
- Bei fernablesbaren Zählern die monatliche Verbrauchsinformation vergessen
  (drei Prozent Kürzungsrecht des Mieters).
- Gegenüber Angehörigen auf die Nebenkostenabrechnung verzichten — das senkt die
  Quote nach § 21 Abs. 2 EStG und gefährdet den Werbungskostenabzug.
- Sich auf den Browserspeicher als Archiv verlassen, ohne je zu sichern.
- Die Abrechnung des Messdienstes ungeprüft übernehmen, ohne Summenabgleich.
- Bei unterjährigem Zählereinbau nach Kalendertagen statt nach Gradtagzahlen teilen.
- Leerstandskosten auf die verbleibenden Mieter umlegen, statt sie selbst zu tragen.
