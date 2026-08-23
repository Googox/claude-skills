---
name: brutto-netto-selbststaendige
description: Rechnet für Selbstständige (Einzelunternehmer, EÜR) vom Umsatz bis zum verfügbaren Netto — mit allen direkten Steuern (ESt, Soli, KiSt, GewSt inkl. §35-Anrechnung), allen Pflichtbeiträgen zur Sozialversicherung (Kranken-, Pflege-, Rentenversicherung) und der freiwilligen Arbeitslosenversicherung nach §28a SGB III inklusive ALG-I-Schätzung
---

# Brutto-Netto-Rechner Selbstständigkeit

## Überblick

Ein Angestellter sieht sein Netto auf der Gehaltsabrechnung. Ein
Selbstständiger sieht nur Umsatz — und erfährt zwölf bis achtzehn Monate
später, was davon wirklich ihm gehörte. Dieser Skill schließt die Lücke: Er
rechnet den Weg **Umsatz → Gewinn → Netto** vollständig durch und macht
sichtbar, was jeder zusätzliche Euro Umsatz tatsächlich einbringt.

Vollständig bedeutet hier: **alle direkten Steuern**, **alle Pflichtbeiträge
zur Sozialversicherung** und die **freiwillige Arbeitslosenversicherung** —
einschließlich ihrer steuerlichen Wechselwirkung über den
Sonderausgabenabzug.

Vorkonfiguriert für den Gewerbesteuer-Hebesatz **320 % (Wiggensbach,
Landkreis Oberallgäu)** und das Rechenjahr **2026**; beides per Parameter
änderbar.

### Abgedeckte Abgaben

| Block | Position | Modellierung |
|---|---|---|
| **Direkte Steuern** | Einkommensteuer | Grundtarif § 32a EStG (2025 und 2026 exakt) |
| | Solidaritätszuschlag | Freigrenze 20.350 € (2026) + Milderungszone 11,9 % |
| | Kirchensteuer | optional, 8 % (BY/BW) oder 9 % |
| | Gewerbesteuer | Freibetrag 24.500 €, Messzahl 3,5 %, Hebesatz frei; Anrechnung § 35 EStG (4,0 × Messbetrag) |
| **Pflichtbeiträge** | Krankenversicherung | GKV freiwillig (14,6 % / 14,0 % + Zusatzbeitrag, Mindest- und Höchstbemessung) oder PKV mit gesetztem Beitrag |
| | Pflegeversicherung | 3,6 % Basis, +0,6 % kinderlos ab 23, −0,25 % je Kind vom 2. bis 5. Kind |
| | Rentenversicherung | Regelbeitrag / halber Regelbeitrag (Gründer) / einkommensgerecht / freiwillig / Versorgungswerk / Rürup |
| **Freiwillig** | Arbeitslosenversicherung | § 28a SGB III: 2,6 % der Bezugsgröße = 102,83 €/Monat (2026), Gründerermäßigung 50 %, plus ALG-I-Schätzung nach fiktiver Bemessung § 152 SGB III |
| **Durchlaufend** | Umsatzsteuer | 19 % mit Vorsteuerabzug, Kleinunternehmeroption — wird separat ausgewiesen und mindert das Netto **nicht** |

> **Hinweis:** Planungswerkzeug, keine Steuer- oder Rechtsberatung und kein
> Ersatz für Steuerbescheid, Steuerberater oder die Auskunft der Agentur für
> Arbeit. Rechengrößen jährlich prüfen — siehe
> [references/rechengroessen-2026.md](references/rechengroessen-2026.md).

## Kernprinzipien

1. **Netto heißt: nach Steuern UND nach Sozialabgaben.** Reine Steuerrechner
   zeigen bei 116.400 € Gewinn eine Belastung von 25 %. Mit Kranken-, Pflege-
   und Altersvorsorge sind es 44 %. Wer nur die Steuer plant, plant die
   Hälfte.
2. **Die Umsatzsteuer gehört nie dir.** Durchlaufposten — liquiditätswirksam,
   aber kein Bestandteil des Netto. Deshalb steht sie im Bericht ganz oben und
   außerhalb der Netto-Rechnung.
3. **Beiträge und Steuern hängen zusammen.** Altersvorsorge und
   Basis-Kranken-/Pflegebeiträge senken das zu versteuernde Einkommen. Der
   Rechner bildet das ab, inklusive der 4-%-Kürzung bei Krankengeldanspruch
   und der Günstigerprüfung für sonstige Vorsorgeaufwendungen.
4. **Die Grenzbelastung steuert Entscheidungen, nicht der Durchschnitt.**
   Ob sich ein Zusatzmandat lohnt, entscheidet der Anteil, der vom nächsten
   Euro bleibt. Der Bericht weist ihn aus.
5. **Oberhalb der Beitragsbemessungsgrenze ändert sich die Logik.** Ab
   5.812,50 € Gewinn im Monat steigen KV und PV nicht weiter — jeder weitere
   Euro wird nur noch besteuert. Das verschiebt die Grenzbelastung spürbar
   nach unten und ist der wichtigste Planungseffekt im mittleren
   Einkommensbereich.

## Workflow

### Phase 1: Profil einmalig anlegen

1. Vorlage kopieren und an die eigene Lage anpassen:
   ```bash
   cp assets/profil-beispiel.json mein-profil.json
   ```
2. Die drei Fragen klären, die das Ergebnis am stärksten bewegen:
   - **Gewerblich oder freiberuflich?** Personal-, Unternehmens- und
     IT-Beratung sind in der Regel gewerblich (Gewerbesteuer), Katalogberufe
     nach § 18 EStG nicht. Bei 320 % Hebesatz ist die Gewerbesteuer über
     § 35 EStG faktisch vollständig anrechenbar — sie kostet dann
     Liquidität, aber kein Geld.
   - **Rentenversicherungspflicht?** Prüfen, ob § 2 SGB VI greift
     (arbeitnehmerähnliche Selbstständige, Lehrende, Pflegekräfte,
     Handwerker). Details in
     [references/pflichtbeitraege-selbststaendige.md](references/pflichtbeitraege-selbststaendige.md).
   - **Krankenversicherung:** GKV freiwillig mit oder ohne Krankengeld, oder
     PKV mit festem Beitrag?
3. Szenariotabelle erzeugen und die eigene Umsatzspanne einordnen:
   ```bash
   python3 scripts/brutto_netto.py --tabelle 6000:16000:2000 --kostenquote 0.25 \
     --rv ruerup --rv-betrag 500 --alv
   ```

### Phase 2: Monatliche Routine (15 Minuten)

1. Vormonat auswerten: Netto-Umsatz, Netto-Betriebsausgaben, echte Vorsteuer.
2. Rechner ausführen:
   ```bash
   python3 scripts/brutto_netto.py --profil mein-profil.json \
     --umsatz 12500 --ausgaben 2800 --vorsteuer 410
   ```
3. Die vier ausgewiesenen Monatsbeträge auf Rücklagenkonten überweisen
   (Umsatzsteuer, Gewerbesteuer, ESt + Soli + KiSt, Sozialversicherung).
4. Checkliste abhaken:
   [assets/monats-checkliste.md](assets/monats-checkliste.md).

### Phase 3: Quartals-Check

1. Jahreshochrechnung statt Monatswerte rechnen — das glättet Ausreißermonate
   gegen die Progression:
   ```bash
   python3 scripts/brutto_netto.py --umsatz 150000 --ausgaben 33600 --jahreswerte
   ```
2. Weicht der hochgerechnete Gewinn stark vom Vorjahr ab, die
   GKV-Beitragsfestsetzung anpassen lassen — freiwillig Versicherte werden
   vorläufig eingestuft und rückwirkend abgerechnet; eine unerwartete
   Nachforderung über zwölf Monate trifft die Liquidität hart.
3. Bei Abweichung über 20 % nach unten: Herabsetzung der
   Einkommensteuer-Vorauszahlungen beantragen.

### Phase 4: Jahreswechsel

1. Rechengrößen des neuen Jahres in `RECHENGROESSEN` im Skript ergänzen
   (Bezugsgröße, Beitragsbemessungsgrenzen, Zusatzbeitrag, Tarifeckwerte).
   Quellenliste in
   [references/rechengroessen-2026.md](references/rechengroessen-2026.md).
2. Gestaltungs-Check im Dezember: Rürup-Einzahlung bis zum Höchstbetrag
   (2026: 30.826 €) prüfen — das ist der größte legale Hebel für
   Selbstständige mit hohem Grenzsteuersatz.
3. Nach dem Steuerbescheid: Rücklagen gegen die tatsächliche Festsetzung
   abrechnen, Überschuss ist frei.

## Tool: `scripts/brutto_netto.py`

Reine Standardbibliothek, Python 3.8+, Text- und JSON-Ausgabe.

```bash
# Standardfall: Monatswerte, gewerblich, GKV, Rürup, mit Arbeitslosenversicherung
python3 scripts/brutto_netto.py --umsatz 12500 --ausgaben 2800 \
  --rv ruerup --rv-betrag 500 --alv

# Freiberuflich, rentenversicherungspflichtig zum Regelbeitrag
python3 scripts/brutto_netto.py --umsatz 9000 --ausgaben 1500 \
  --freiberuflich --rv regelbeitrag

# Privat krankenversichert, zwei Kinder, Kirchensteuer Bayern
python3 scripts/brutto_netto.py --umsatz 14000 --ausgaben 3000 \
  --kv privat --pkv-monat 780 --kinder 2 --kirche

# Gründer: halber Regelbeitrag RV, halber ALV-Beitrag
python3 scripts/brutto_netto.py --umsatz 5000 --ausgaben 1000 \
  --rv halber-regelbeitrag --alv --alv-gruender

# Jahreswerte statt Monatswerte
python3 scripts/brutto_netto.py --umsatz 150000 --ausgaben 33600 --jahreswerte

# Szenariotabelle über Umsatzstufen
python3 scripts/brutto_netto.py --tabelle 6000:16000:2000 --kostenquote 0.25

# JSON für Weiterverarbeitung
python3 scripts/brutto_netto.py --umsatz 12500 --ausgaben 2800 --format json
```

### Wichtige Parameter

| Parameter | Wirkung |
|---|---|
| `--freiberuflich` | Keine Gewerbesteuer (§ 18 EStG statt § 15 EStG) |
| `--hebesatz` | GewSt-Hebesatz der Gemeinde, Standard 320 |
| `--kv gesetzlich\|privat` | GKV-Berechnung oder fester PKV-Beitrag (`--pkv-monat`) |
| `--zusatzbeitrag` | Kassenindividuell als Dezimalzahl, Standard 0.029 (Durchschnitt 2026) |
| `--ohne-krankengeld` | Ermäßigter Satz 14,0 % statt 14,6 %; entfernt die 4-%-Kürzung beim Sonderausgabenabzug |
| `--kinder N` | Senkt den Pflegeversicherungssatz ab dem zweiten Kind |
| `--rv MODUS` | `keine`, `regelbeitrag`, `halber-regelbeitrag`, `einkommensgerecht`, `freiwillig`, `versorgungswerk`, `ruerup` |
| `--alv` / `--alv-gruender` | Freiwillige Arbeitslosenversicherung, ganzer oder halber Beitrag |
| `--qualifikationsgruppe 1-4` | Basis der ALG-I-Schätzung, 1 = Hochschulabschluss |
| `--weitere-vorsorge` | BU, Unfall, Haftpflicht pro Monat (sonstige Vorsorgeaufwendungen) |

### Beispielausgabe (Auszug)

```
4) BRUTTO -> NETTO
Gewinn (brutto)                        116.400,00 EUR
./. Sozialabgaben                       21.776,83 EUR
./. Steuern                             29.314,00 EUR
= NETTO IM JAHR                         65.309,17 EUR
= NETTO IM MONAT                         5.442,43 EUR
Abgabenquote auf den Gewinn:   43,9 %
Von 1.000 EUR Mehrgewinn bleiben: 580,00 EUR (42,0 % Abgaben)
```

## Resources

**references/**
- [pflichtbeitraege-selbststaendige.md](references/pflichtbeitraege-selbststaendige.md)
  — wer welche Beiträge zahlen muss, Bemessungsgrundlagen, Mindest- und
  Höchstbeiträge, GKV-Beitragsfestsetzung, Gestaltungsspielräume
- [arbeitslosenversicherung-freiwillig.md](references/arbeitslosenversicherung-freiwillig.md)
  — § 28a SGB III: Zugangsvoraussetzungen, Dreimonatsfrist, Beitragshöhe,
  ALG-I-Berechnung nach fiktiver Bemessung, Kündigung, Lohnt-sich-Rechnung
- [rechengroessen-2026.md](references/rechengroessen-2026.md) — alle
  verwendeten Werte mit Quelle und Vorjahresvergleich, Pflegeanleitung für
  den Jahreswechsel

**assets/**
- [profil-beispiel.json](assets/profil-beispiel.json) — Profilvorlage
- [monats-checkliste.md](assets/monats-checkliste.md) — abhakbare
  Monatsroutine

## Grenzen des Modells

- Einzelunternehmer mit Grundtarif. Keine Zusammenveranlagung (Splitting),
  keine weiteren Einkunftsarten, keine Kinderfreibeträge im Steuertarif.
- Gewerbeertrag ≈ Gewinn (keine Hinzurechnungen und Kürzungen nach §§ 8, 9
  GewStG) — für Dienstleister ohne hohe Miet- und Zinsaufwendungen zutreffend.
- Kirchensteuer wird nicht als Sonderausgabe gegengerechnet (konservativ).
- Umsatzsteuer nur zum Regelsatz 19 %, kein 7-%-Mix, keine Reverse-Charge-
  Umsätze.
- Künstlersozialkasse (halbierte Beitragslast) ist nicht abgebildet; für
  KSK-Versicherte sind die KV-, PV- und RV-Beiträge im Ergebnis zu halbieren.
- Die ALG-I-Schätzung nähert die Lohnsteuer über den Einkommensteuertarif mit
  Vorsorgepauschale an statt über die amtliche Lohnsteuertabelle; Abweichung
  typischerweise unter 5 %.
- Beitragsrückerstattungen, Selbstbehalte und Wahltarife der PKV bleiben
  unberücksichtigt.
