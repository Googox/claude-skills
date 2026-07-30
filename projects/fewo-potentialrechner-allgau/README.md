# FeWo-Potentialrechner Allgäu

Single-Page-Web-App zur strukturierten Vorab-Bewertung von Mietwohnungen im Raum Kempten (Allgäu) für ein Rent-to-Rent-Ferienwohnungsmodell. Führt zweistufig durch K.O.-Filter (Stufe 1) und Standort-/Objektkalkulation mit Scoring (Stufe 2), bevor eine Go/No-Go-Ampel ausgegeben wird.

## Nutzung

`index.html` direkt im Browser öffnen (Doppelklick oder per `file://`-Pfad). Für den ersten Aufruf ist eine Internetverbindung nötig, da React, ReactDOM, Recharts und Babel Standalone über CDN (unpkg.com) geladen werden. Es gibt keinen Build-Schritt und kein Backend – die gesamte Anwendung ist eine einzelne HTML-Datei.

Alle Eingaben bleiben ausschließlich im Browser-State. Zum Speichern/Weitergeben: **JSON exportieren** (Download) und später **JSON importieren** (Datei-Upload). Es wird kein `localStorage` verwendet, ein Neuladen der Seite ohne vorherigen Export verwirft die Eingaben.

## Aufbau

- **Stufe 1 – K.O.-Filter:** Untervermietungserlaubnis, Baurecht, Zweckentfremdungssatzung, WEG-Zustimmung (falls zutreffend), Gewerbeanmeldung (Reminder), Brandschutz. Ein rotes Kriterium sperrt Stufe 2 vollständig ("NICHT GEEIGNET"); ein gelbes Kriterium markiert das Ergebnis später als "VORBEHALTLICH".
- **Stufe 2a – Standortanalyse:** 8 gewichtete Kriterien, ergibt den Standortscore (40 % Gesamtscore-Gewicht).
- **Stufe 2b – Objektkalkulation:** Fixkosten, Einmalinvest, vier Saisonblöcke (ADR/Auslastung/Monate), variable Kosten. Drei Szenarien (konservativ/realistisch/optimistisch) werden parallel berechnet; ergibt den Objektscore (60 % Gesamtscore-Gewicht).
- **Ergebnis:** Ampel (Grün ≥ 70 / Gelb 50–69 / Rot < 50), Kennzahlen-Dashboard, Szenariotabelle, Saisonumsatz-Diagramm, Pflicht-Sensitivität ("Was wäre wenn"-Slider für Kaltmiete/ADR/Auslastung ±20 %), automatische Stellhebel-Vorschläge bei Gelb, Druckansicht als Einseiter.
- **Objektvergleich:** Sortierbare Übersichtstabelle über alle angelegten Objekte.

## Berechnungslogik

Die Kernfunktionen (`evaluateKO`, `computeStandortScore`, `computeScenario`, `computeObjektScore`, `computeGesamtscore`, `computeHebel`) sind als pure functions im `<script>`-Block implementiert. Die Break-even-Auslastung wird analytisch gelöst (lineare Skalierung der Auslastung bei gegebenem ADR-Mix, bis Ergebnis vor Steuern = 0).

Die Umsatzrendite (Marge) wird zusätzlich gegen einen Zielkorridor von 25–40 % geprüft (grün = im Korridor, rot = darunter, gelb = darüber – Annahmen prüfen).

## Explizit nicht enthalten

Kein Scraping von Airbnb/Booking, keine automatischen Marktdaten, keine Steuerberechnung, keine Rechtsprüfung – alle Marktwerte sind manuelle Eingaben, alle rechtlichen K.O.-Kriterien erfordern manuelle Bestätigung durch die Nutzerin.
