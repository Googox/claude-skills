---
name: fahrtkosten-calculator
description: Berechnet für Einzelunternehmer den individuellen Kilometersatz eines privat geleasten Fahrzeugs, das betrieblich mitgenutzt wird, vergleicht ihn mit der 0,30-EUR-Pauschale und erzeugt die finanzamtsfeste Dokumentation (Fahrtenbuch-Prüfung, Eigenbeleg, Jahresabrechnung) für die Nutzungseinlage — monatlich oder jährlich
---

# Fahrtkosten-Calculator (privat geleastes Fahrzeug → Einzelunternehmen)

## Overview

Du least ein Fahrzeug **privat** und nutzt es teilweise **betrieblich**. Jeder
betrieblich gefahrene Kilometer soll mit seinen echten Kosten beim
Einzelunternehmen als Betriebsausgabe ankommen — nachvollziehbar für das
Finanzamt, monatlich oder einmal jährlich.

Dieser Skill liefert dafür die vollständige Kette:

```
Kostenbelege  →  Gesamtkosten p. a.
                                     ┐
Fahrtenbuch   →  Gesamtfahrleistung  ┤→ individueller km-Satz
                 betriebliche km     ┘   ↕ Vergleich mit 0,30 EUR/km
                                         ↓
                                      Betriebsausgabe
                                         ↓
                            Eigenbeleg + Buchungssatz + Jahresabrechnung
```

> **Wichtige Klarstellung vorweg:** Als Einzelunternehmer kannst du dir selbst
> **keine Rechnung stellen** — es gibt keinen Vertrag mit sich selbst und keinen
> umsatzsteuerlichen Leistungsaustausch. Der Vorgang heißt steuerlich
> **Nutzungseinlage**: Du legst den betrieblich veranlassten Teil deiner privaten
> Fahrzeugaufwendungen in den Betrieb ein. Wirtschaftlich ist das die
> „Weiterberechnung", die du meinst — formal aber ein Eigenbeleg, keine Rechnung.
> Eine Rechnung mit Umsatzsteuerausweis an dich selbst würde eine unrichtig
> ausgewiesene Steuer nach § 14c UStG auslösen. Details:
> [references/rechtsgrundlagen.md](references/rechtsgrundlagen.md).

> **Disclaimer:** Planungs- und Dokumentationswerkzeug, **keine Steuerberatung**.
> Die Methodenwahl und die Jahreswerte vor Abgabe der Steuererklärung mit dem
> Steuerberater abstimmen.

## Warum der individuelle Kilometersatz meist deutlich mehr bringt

Du hast ein **Wahlrecht** je Fahrt-Kategorie:

| Methode | Nachweis | Typischer Satz |
|---|---|---|
| **Pauschale** 0,30 EUR/km | nur Aufzeichnung der dienstlichen Fahrten | 0,30 EUR/km |
| **Einzelnachweis** (individuell) | Gesamtkosten **und** Gesamtfahrleistung nachweisen | 0,45–0,90 EUR/km |

Beim Leasing liegt der individuelle Satz fast immer über der Pauschale — die
Leasingrate plus verteilte Sonderzahlung schlägt stärker durch als die AfA eines
alten gekauften Fahrzeugs. Im mitgelieferten Beispiel:

```
Gesamtkosten 12.620,67 EUR / 21.577 km  =  0,5849 EUR/km
7.195 dienstliche km  ×  0,5849  =  4.208,45 EUR   (individuell)
7.195 dienstliche km  ×  0,30    =  2.158,50 EUR   (pauschal)
                              Differenz  2.049,95 EUR mehr Betriebsausgaben
```

Der Preis dafür ist der Nachweis: lückenloses Fahrtenbuch **plus** vollständige
Kostenbelege. Unter ca. 5 % betrieblicher Nutzung lohnt der Aufwand selten — dann
ist die Pauschale der pragmatische Weg. Der Rechner weist darauf hin.

## Die drei Fahrt-Kategorien (werden unterschiedlich behandelt)

| Kategorie | CSV-Wert | Abzug |
|---|---|---|
| Dienstreise / Auswärtstätigkeit (Kunden, Messen, Lieferanten) | `dienstreise` | **alle gefahrenen km** × individueller Satz oder 0,30 EUR |
| Wohnung ↔ Betriebsstätte | `betriebsstaette` | nur **Entfernungspauschale** (2026: 0,38 EUR je Entfernungs­kilometer, einfache Strecke) — § 4 Abs. 5 Satz 1 Nr. 6 EStG |
| Privatfahrten | `privat` | nicht abziehbar |

Die häufigste teure Fehlbuchung ist, Fahrten zur eigenen Betriebsstätte mit dem
vollen Kilometersatz anzusetzen. Der Rechner trennt das automatisch.

## Workflow

### Phase 1: Einmalige Einrichtung (30 Minuten)

1. **Fahrzeugprofil anlegen**
   ```bash
   cp assets/fahrzeugprofil-beispiel.json fahrzeug.json
   ```
   Eintragen: Leasingrate, **Sonderzahlung + Laufzeit**, Versicherung, Kfz-Steuer,
   Stellplatz, Kraftstoff-/Strombudget, Wartung, Reifen. Welche Position
   hineingehört und welche nicht:
   [references/gesamtkosten-katalog.md](references/gesamtkosten-katalog.md).

2. **Kilometerstand zum Stichtag festhalten** — Foto vom Tacho am 1.1. (bzw. am
   Tag der Fahrzeugübernahme) und am 31.12. Das ist der Anker für die
   Gesamtfahrleistung; ohne ihn ist der individuelle Satz angreifbar.

3. **Fahrtenbuch aufsetzen**
   ```bash
   cp assets/fahrtenbuch-vorlage.csv fahrten-2026.csv
   ```
   Anforderungen an die Form (zeitnah, geschlossen, nachträglich unveränderbar):
   [references/fahrtenbuch-anforderungen.md](references/fahrtenbuch-anforderungen.md).

4. **Umsatzsteuer-Frage einmal klären** (Vorsteuer aus den Leasingraten):
   [references/umsatzsteuer-leasing.md](references/umsatzsteuer-leasing.md) — die
   Entscheidung bestimmt, ob du im Profil Brutto- oder Nettobeträge erfasst.

5. **Vorläufigen Kilometersatz bestimmen** für die unterjährigen Buchungen:
   Planwerte ins Profil, geschätzte Jahresfahrleistung eintragen, einmal rechnen.

### Phase 2: Monatliche Routine (10 Minuten)

1. Fahrten des Vormonats ins Fahrtenbuch nachtragen (besser: laufend am Fahrtende).
2. Tankbelege, Werkstattrechnungen, Leasingabbuchung im Ordner ablegen.
3. Monatsabrechnung rechnen:
   ```bash
   python3 scripts/km_kostenrechner.py \
     --profil fahrzeug.json --fahrtenbuch fahrten-2026.csv --monat 2026-03
   ```
4. Eigenbeleg erzeugen, ausdrucken, unterschreiben, zur Buchhaltung:
   ```bash
   python3 scripts/km_kostenrechner.py \
     --profil fahrzeug.json --fahrtenbuch fahrten-2026.csv \
     --monat 2026-03 --eigenbeleg > eigenbeleg-2026-03.txt
   ```
5. Buchen (SKR03): `4670 Reisekosten Unternehmer Fahrtkosten` an
   `1890 Privateinlagen`. SKR04: `6670` an `2180`.
6. Optional: Betrag vom Geschäfts- aufs Privatkonto überweisen. Das ist eine
   **Privatentnahme** und steuerlich neutral — die Betriebsausgabe entsteht durch
   die Einlagebuchung, nicht durch die Überweisung.

### Phase 3: Jahresabschluss (45 Minuten)

1. Kilometerstand 31.12. fotografieren und ins Profil eintragen.
2. Ist-Kosten aus den Belegen ins Profil übernehmen (statt Planwerten).
3. Fahrtenbuch prüfen lassen — **vor** der Abrechnung:
   ```bash
   python3 scripts/km_kostenrechner.py \
     --profil fahrzeug.json --fahrtenbuch fahrten-2026.csv --strikt
   ```
   Exit-Code 2 bedeutet: Lücken oder fehlende Pflichtangaben. Erst schließen,
   dann abrechnen.
4. Jahresabrechnung erzeugen und gegen die Summe der Monatsbuchungen stellen:
   ```bash
   python3 scripts/km_kostenrechner.py \
     --profil fahrzeug.json --fahrtenbuch fahrten-2026.csv
   ```
   Die Differenz zwischen vorläufigem und Ist-Satz wird in einer Korrekturbuchung
   im Dezember erfasst.
5. Belegpaket für den Steuerberater zusammenstellen:
   [assets/jahresabrechnung-checkliste.md](assets/jahresabrechnung-checkliste.md).

## Zwei Wege zum selben Ergebnis

| | Oberfläche | Kommandozeile |
|---|---|---|
| Datei | `assets/kilometersatz-rechner.html` im Browser öffnen | `scripts/km_kostenrechner.py` |
| Eingabe | Formularfelder, Ergebnis rechnet live mit | Fahrzeugprofil (JSON) + Fahrtenbuch (CSV) |
| Stärke | schnelles Durchspielen von Szenarien, Schwellen auf einen Blick | echtes Fahrtenbuch, Lückenprüfung, Monatsabrechnung, JSON-Export |
| Gedacht für | „Was passiert, wenn ich 3.000 km mehr dienstlich fahre?" | die tatsächliche Jahresabrechnung mit Belegen |

Für alles, was unterschrieben oder verschickt wird, gibt es zusätzlich das
**Word-Formular** `assets/Eigenbeleg-Fahrzeugkosten.docx`:

| Seite | Inhalt |
|---|---|
| 1 | Eigenbeleg mit Kopfdaten, Rechenblöcken A bis D, Rechtsgrundlage, Buchungssatz, Anlagen-Checkliste, Unterschriftszeile |
| 2 | Kostenaufstellung als Anlage — alle Kostenpositionen einzeln, mit Spalte für die Belegnummer |
| 3 | Fahrtenbuch-Erfassungsbogen im Querformat, 22 Zeilen (A4 quer) |

Ausfüllbar von Hand nach dem Ausdrucken oder direkt in Word, dann als PDF an
den Steuerberater. Die Rechenwege stehen als Hinweis neben jedem Feld, damit die
Zahlen auch ohne den Rechner nachvollziehbar bleiben.

Beide rechnen identisch — dieselben Formeln, dieselben Sätze. Die Oberfläche
speichert Eingaben nur im eigenen Browser, es wird nichts übertragen.

## Kommandos

```bash
# Jahresabrechnung (Standard)
python3 scripts/km_kostenrechner.py --profil fahrzeug.json --fahrtenbuch fahrten.csv

# Monatsabrechnung zusätzlich ausweisen
python3 scripts/km_kostenrechner.py --profil fahrzeug.json --fahrtenbuch fahrten.csv \
  --monat 2026-03

# Eigenbeleg-Text (Monat oder Jahr, je nach --monat)
python3 scripts/km_kostenrechner.py --profil fahrzeug.json --fahrtenbuch fahrten.csv \
  --monat 2026-03 --eigenbeleg

# Maschinenlesbar (für Weiterverarbeitung / Buchhaltungsimport)
python3 scripts/km_kostenrechner.py --profil fahrzeug.json --fahrtenbuch fahrten.csv \
  --format json

# Fahrtenbuch-Prüfung als Gate (Exit-Code 2 bei Beanstandungen)
python3 scripts/km_kostenrechner.py --profil fahrzeug.json --fahrtenbuch fahrten.csv \
  --strikt

# Abweichendes Jahr
python3 scripts/km_kostenrechner.py --profil fahrzeug.json --fahrtenbuch fahrten.csv \
  --jahr 2025
```

## Was der Rechner automatisch prüft

| Prüfung | Warum |
|---|---|
| Leasingsonderzahlung ohne Laufzeit → Abbruch | Die Sonderzahlung muss periodengerecht über die Vertragslaufzeit verteilt werden (BFH VIII R 1/21, VI R 9/22) — nicht voll im Zahlungsjahr |
| Lücken zwischen Kilometerständen | Nicht erfasste Fahrten machen den Einzelnachweis angreifbar |
| Überlappende Kilometerstände | Zeigt Erfassungsfehler oder nachträgliche Manipulation |
| Dienstreise ohne Ziel / Zweck / Geschäftspartner | Pflichtangaben; ohne sie kippt die Fahrt in „privat" |
| Betrieblicher Anteil > 50 % | Ab dieser Schwelle behandelt die Finanzverwaltung das Fahrzeug regelmäßig als betriebliches Fahrzeug (1-%-Regelung / voller Kostenabzug) — das Nutzungseinlage-Modell passt dann nicht mehr |
| Betrieblicher Anteil < 5 % | Aufwand des Einzelnachweises steht in keinem Verhältnis |
| Differenz Kilometerstände ↔ Fahrtenbuch | Nicht erfasste km werden konservativ als privat gewertet |
| Reisenebenkosten in den Gesamtkosten | Parkgebühren, Maut, Fähre gehören **nicht** in den km-Satz, sondern sind zusätzlich voll abziehbar |

## Kernprinzipien

1. **Der Kilometersatz ist ein Bruch — beide Seiten müssen belegt sein.**
   Gesamtkosten ohne Gesamtfahrleistung ist kein Nachweis, und umgekehrt.
2. **Alle Kilometer zählen, nicht nur die dienstlichen.** Der Nenner ist die
   gesamte Jahresfahrleistung. Wer Privatfahrten nicht erfasst, hat keinen Nenner.
3. **Die Leasingsonderzahlung gehört auf die Laufzeit verteilt**, nicht ins
   Zahlungsjahr. Das ist der häufigste und teuerste Fehler bei geleasten Fahrzeugen.
4. **Fahrten zur eigenen Betriebsstätte sind gedeckelt** auf die
   Entfernungspauschale — unabhängig davon, was der Kilometer wirklich kostet.
5. **Zeitnah aufzeichnen schlägt vollständig rekonstruieren.** Ein am Jahresende
   erstelltes Fahrtenbuch erkennt jeder Prüfer.
6. **Der Eigenbeleg ist kein Ersatz für die Belege**, sondern deren Klammer.
   Fahrtenbuch und Kostenbelege müssen dahinter liegen.

## Zusammenspiel mit anderen Skills

Die ermittelte Betriebsausgabe senkt den Gewinn und damit ESt, GewSt und Soli.
Für die Rücklagenplanung den Jahresbetrag als Betriebsausgabe in den
[Steuerrechner](../steuerrechner-selbststaendigkeit/SKILL.md) übernehmen:

```bash
python3 ../steuerrechner-selbststaendigkeit/scripts/steuerrechner.py \
  --umsatz 12500 --ausgaben 2800   # + 350,70 EUR/Monat aus diesem Rechner
```

## Dateien

| Datei | Zweck |
|---|---|
| `scripts/km_kostenrechner.py` | Rechner, Fahrtenbuch-Prüfung, Eigenbeleg-Generator |
| `scripts/build_word_formular.js` | Erzeugt das Word-Formular neu (`node scripts/build_word_formular.js`, benötigt `npm install docx`) |
| `assets/kilometersatz-rechner.html` | Interaktive Oberfläche — lokal im Browser öffnen, rechnet live, speichert Eingaben im Browser |
| `assets/fahrzeugprofil-beispiel.json` | Vorlage für die Kostenerfassung |
| `assets/fahrtenbuch-vorlage.csv` | Fahrtenbuch-Struktur mit Beispieljahr |
| `assets/Eigenbeleg-Fahrzeugkosten.docx` | **Word-Formular** — drei Seiten zum Ausfüllen von Hand oder am Rechner, per Mail versendbar |
| `assets/eigenbeleg-vorlage.md` | Eigenbeleg als Markdown-Fassung |
| `assets/jahresabrechnung-checkliste.md` | Belegpaket für den Steuerberater |
| `references/rechtsgrundlagen.md` | Nutzungseinlage, Wahlrechte, Rechtsprechung |
| `references/gesamtkosten-katalog.md` | Was in den km-Satz gehört — und was nicht |
| `references/fahrtenbuch-anforderungen.md` | Formanforderungen, Prüfungsfallen |
| `references/umsatzsteuer-leasing.md` | Vorsteuer bei teilunternehmerischem Leasing |

---

**Steuerstand:** 2026 (Entfernungspauschale 0,38 EUR ab dem ersten Kilometer,
Dienstreisepauschale unverändert 0,30 EUR/km). Werte jährlich prüfen.
