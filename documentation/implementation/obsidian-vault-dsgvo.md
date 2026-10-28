# DSGVO-Einordnung der Vault-Architektur

Bewertung der Architektur aus `obsidian-vault-datenmodell.md` für A/A Executive
Search. Stand Oktober 2026.

**Das ist keine Rechtsberatung.** Ich bin kein Anwalt, und die Bewertung von
Drittlandübermittlungen ändert sich mit Gerichtsentscheidungen und
Angemessenheitsbeschlüssen. Was hier steht, ist eine technische Einordnung mit
den Punkten, die ein Datenschutzbeauftragter zuerst prüfen würde. Für die
Interessenabwägung und das Verarbeitungsverzeichnis gehört ein Fachanwalt oder
externer DSB dazu, nicht weil das Thema kompliziert ist, sondern weil die
Haftung bei Aaron als Verantwortlichem liegt.

Ausgangslage: Aaron verarbeitet Daten über Führungskräfte, die er größtenteils
nicht von diesen Personen selbst erhalten hat. Namen, Werdegänge,
Wechselabsichten, Gehaltsbänder, Bewertungsnotizen. Er ist Verantwortlicher im
Sinne von Art. 4 Nr. 7 DSGVO.

---

## 1 Was die Architektur sauber löst

### 1.1 Datenminimierung bei der Übermittlung

Die Trennung in zwei physisch getrennte Vaults bewirkt, dass vertraulich
mitgeteilte Daten die Anthropic-API nie erreichen. Nicht als Policy, sondern
weil der zweite Vault technisch nicht verbunden ist. Das ist Art. 5 Abs. 1
lit. c in der Umsetzung, nicht in der Absichtserklärung.

### 1.2 Keine Drittanbieter-Cloud als Speicherort

Der Vault liegt lokal. Keine Auftragsverarbeitung durch Google, Dropbox oder
einen Sync-Dienst, also auch kein zusätzlicher AV-Vertrag und keine zweite
Drittlandübermittlung für die Speicherung.

### 1.3 Beschaffung ohne Scraping

`aa-market-intelligence` lehnt automatisiertes Auslesen ausdrücklich ab und
verweist auf Sales Navigator, Google Alerts und Fachpresse. Das ist nicht nur
plattformrechtlich relevant: Eine systematische Erfassung ohne Rechtsgrundlage
wäre der schwerere Mangel. Die Beschaffung ist damit nicht durch einen
ToS-Verstoß kontaminiert.

### 1.4 Nachweisbare Herkunft

Die Felder `quelle`, `quelle_url` und `belegbar` sind Pflicht bei
Marktbeobachtungen. Damit ist für jeden Datensatz dokumentiert, woher er kommt.
Das ist die Voraussetzung, um eine Auskunft nach Art. 15 überhaupt beantworten
zu können.

### 1.5 Keine automatisierte Entscheidung im Einzelfall

Art. 22 verbietet Entscheidungen, die ausschließlich auf automatisierter
Verarbeitung beruhen und die Person erheblich beeinträchtigen. Eine
Nichtberücksichtigung als Kandidat kann darunterfallen.

Die Assessment-Methodik hält ausdrücklich fest, dass der Score das Urteil nicht
ersetzt, sondern begründbar macht, und dass bei knappem Ergebnis Aaron
entscheidet. Das ist für Art. 22 der entscheidende Satz. Er muss auch in der
Praxis gelten: Ein Score, der faktisch allein aussortiert, wäre eine
automatisierte Entscheidung, egal was im Skill steht.

### 1.6 Zweckbindung

Das Feld `geschaeft: aa` auf jeder Datei macht die Zweckbindung abfragbar. Die
Skills verbieten die Vermischung mit anderen Geschäftsideen. Das ist Art. 5
Abs. 1 lit. b, technisch prüfbar statt behauptet.

---

## 2 Restrisiko, ungeschminkt

### 2.1 Die Übermittlung an Anthropic ist der größte offene Punkt

Ein MCP-Server auf `127.0.0.1` löst die Speicherung, nicht die Übermittlung.
Sobald Claude eine Kontaktdatei liest, geht ihr Inhalt an die API.

Daraus folgen drei Prüfpunkte, die vor dem Produktivbetrieb geklärt sein
müssen:

1. **Auftragsverarbeitungsvertrag nach Art. 28.** Umfasst der genutzte Tarif
   einen? Privatkundentarife tun das typischerweise nicht. Ohne AV-Vertrag ist
   jede Übermittlung personenbezogener Daten ungedeckt, unabhängig davon, wie
   saubere Felder dieses Modell definiert.
2. **Drittlandübermittlung nach Art. 44 ff.** Anthropic ist ein US-Anbieter. Auf
   welcher Grundlage die Übermittlung erfolgt, Angemessenheitsbeschluss oder
   Standardvertragsklauseln, muss aus den Vertragsunterlagen hervorgehen und
   dokumentiert werden.
3. **Speicherung der Prompts beim Anbieter.** Ob und wie lange Eingaben
   gespeichert und zu Trainingszwecken genutzt werden, ist tarifabhängig. Für
   Kandidatendaten ist das kein Nebenaspekt.

**Bewertung:** Dieser Punkt ist nicht durch Architektur lösbar, nur durch
Vertrag. Solange er offen ist, sollte der Vault mit echten Kandidatendaten
zurückhaltend per MCP gelesen werden. Arbeiten lässt sich währenddessen mit
Arbeitgeberdaten und Mandatsstruktur, die weniger sensibel sind.

### 2.2 Die Vault-Grenze ist Disziplin, keine Technik

`AA-Vertraulich` ist geschützt, solange niemand den Pfad in eine
MCP-Konfiguration einträgt. Es existiert kein Mechanismus, der das verhindert.
Ein einmaliger Konfigurationsfehler öffnet die Grenze unbemerkt.

Minderung: Das Diagnose-Skript gibt den konfigurierten Pfad aus. Vor jeder
Konfigurationsänderung prüfen.

### 2.3 Informationspflicht nach Art. 14, der blinde Fleck der Branche

Werden personenbezogene Daten nicht bei der betroffenen Person erhoben, muss
diese informiert werden: über Identität des Verantwortlichen, Zwecke,
Rechtsgrundlage, Kategorien der Daten, Speicherdauer, ihre Rechte und die
Quelle der Daten. Frist nach Art. 14 Abs. 3: innerhalb eines Monats,
spätestens bei der ersten Kontaktaufnahme.

Das betrifft praktisch jeden Kandidaten, der über Presse, Alerts oder Sales
Navigator in den Vault kommt, bevor Aaron mit ihm gesprochen hat.

**Das ist der Punkt, der im Executive Search am häufigsten übersehen wird**, und
er lässt sich nicht wegargumentieren. Die Ausnahmen in Art. 14 Abs. 5 sind eng.

Konsequenz für das Datenmodell: ein Feld `info_art14_am`, und eine Dataview-Sicht
über Kontakte, die seit mehr als einem Monat im Vault stehen und noch keine
Information erhalten haben.

### 2.4 Keine Löschfristen definiert

Eine Kandidatennotiz ohne Mandat und ohne Einwilligung darf nicht unbegrenzt
liegen bleiben. Art. 5 Abs. 1 lit. e verlangt eine Speicherung nur so lange, wie
es für den Zweck erforderlich ist. Ohne definierte Frist gibt es keinen Zeitpunkt,
an dem gelöscht wird, und damit faktisch eine unbegrenzte Speicherung.

Konsequenz für das Datenmodell: ein Feld `loeschpruefung_am`, gesetzt beim
Anlegen, und eine Sicht auf fällige Prüfungen. Ein Vorschlag für die Frist, nicht
aus dem Gesetz abgeleitet, sondern aus der Praxis: 24 Monate nach letzter
Interaktion bei Kandidaten ohne laufendes Mandat, dann Prüfung und Entscheidung.

### 2.5 Betroffenenrechte sind machbar, aber nicht organisiert

Auskunft (Art. 15), Löschung (Art. 17) und Widerspruch (Art. 21) sind in einem
Markdown-Vault technisch leicht zu erfüllen: `grep` über zwei Verzeichnisse
findet alles zu einer Person. Beides muss aber als Prozess existieren, mit Frist
von einem Monat.

Besonderheit: Ein Widerspruch nach Art. 21 gegen die Verarbeitung auf Grundlage
berechtigten Interesses wirkt sofort. Dann ist der Datensatz zu löschen oder zu
sperren, nicht nur auf `status: abgesagt` zu setzen.

### 2.6 Backups erreichen die Löschung nicht automatisch

Wird der Vault per Time Machine, Backup-Festplatte oder Versionsverwaltung
gesichert, lebt ein gelöschter Datensatz dort weiter. Eine Löschung, die das
Backup nicht erreicht, ist keine Löschung. Das ist beim Vault im Git-Repository
besonders relevant, weil die Historie den Inhalt dauerhaft konserviert.

**Daraus folgt eine harte Regel: Der produktive Vault gehört nicht in ein
Git-Repository.** Die Spezifikation und die Vorlagen sind versionierbar, die
Daten nicht.

---

## 3 Was ins Verarbeitungsverzeichnis gehört

Art. 30 verlangt ein Verzeichnis der Verarbeitungstätigkeiten. Für diese
Architektur mindestens:

| Punkt | Inhalt |
|-------|--------|
| Verantwortlicher | A/A Executive Search, Aaron als Inhaber, Kontaktdaten |
| Zweck | Vermittlung von Führungskräften, Mandatsbearbeitung, Marktbeobachtung |
| Rechtsgrundlage | Art. 6 Abs. 1 lit. f, berechtigtes Interesse, mit dokumentierter Interessenabwägung. Bei Mandatskandidaten ggf. lit. b |
| Kategorien betroffener Personen | Führungskräfte im Premium-Automobilhandel, Entscheider bei Arbeitgebern |
| Kategorien von Daten | Name, Kontaktdaten, beruflicher Werdegang, Position, Bewertungsnotizen, im getrennten Vault zusätzlich Vergütung und Wechselmotive |
| Empfänger | Anthropic als Auftragsverarbeiter, soweit AV-Vertrag vorliegt. Mandanten im Rahmen der Shortlist, mit eigener Rechtsgrundlage |
| Drittlandübermittlung | USA, Grundlage aus dem Anthropic-Vertrag, dokumentieren |
| Speicherdauer | Je Kategorie, Vorschlag 24 Monate nach letzter Interaktion ohne Mandat |
| Technische Maßnahmen | Festplattenverschlüsselung, Geräteverschlüsselung, Zugangsschutz, getrennte Vaults, loopback-gebundener MCP-Server mit Bearer-Token, kein Cloud-Sync |
| Löschkonzept | Prüffrist je Datensatz, Verfahren für Backups |

Zwei Punkte, die separat zu dokumentieren sind und oft fehlen: die
**Interessenabwägung** zu Art. 6 Abs. 1 lit. f in schriftlicher Form, und das
**Verfahren zur Erfüllung der Informationspflicht** nach Art. 14, inklusive
Mustertext für die erste Kontaktaufnahme.

---

## 4 Zusammenfassende Bewertung

Die Architektur ist datenschutzfreundlich gebaut: lokale Speicherung, technische
Trennung der sensiblen Kategorie, nachweisbare Herkunft, keine automatisierte
Einzelfallentscheidung, prüfbare Zweckbindung. Das ist mehr als die meisten
CRM-Setups im Executive Search leisten.

Der Schwachpunkt liegt nicht in der Architektur, sondern in zwei Punkten
daneben: **der Vertragslage mit Anthropic** und **der Informationspflicht nach
Art. 14**. Beide sind unabhängig von jeder Technik zu klären, und ohne sie ist
ein sauberes Datenmodell nur eine gut dokumentierte Verarbeitung ohne Grundlage.

Priorität, wenn Zeit knapp ist: erst den AV-Vertrag prüfen, dann den Mustertext
für Art. 14 schreiben. Beides ist an einem Vormittag erledigt und entfernt die
beiden Risiken, die im Ernstfall teuer werden.
