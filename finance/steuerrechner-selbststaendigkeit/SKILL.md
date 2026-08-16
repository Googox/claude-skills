---
name: steuerrechner-selbststaendigkeit
description: Errechnet für gewerbliche Einzelunternehmer (EÜR) aus dem monatlichen Umsatz alle relevanten Steuern (USt, GewSt mit konfigurierbarem Hebesatz, ESt, Soli, KiSt inkl. §35-Anrechnung) und leitet daraus monatliche Rücklagen-Überweisungen für eine Qonto-Unterkontenstruktur ab
---

# Steuerrechner Selbstständigkeit

## Overview

Steuer-Planungswerkzeug für gewerbliche Einzelunternehmer mit
Einnahmen-Überschuss-Rechnung (EÜR). Aus monatlichem Netto-Umsatz und
Betriebsausgaben werden alle relevanten Steuern aufs Jahr hochgerechnet und
in **drei konkrete monatliche Überweisungen** auf Qonto-Rücklagen-Unterkonten
übersetzt — damit zu jeder Voranmeldung, Vorauszahlung und zur
Steuererklärung die Mittel sicher bereitliegen.

Vorkonfiguriert für den **Gewerbesteuer-Hebesatz 320 % (Wiggensbach,
Landkreis Oberallgäu)**; jeder andere Hebesatz per Parameter.

**Abgedeckte Steuerarten:**

| Steuer | Modellierung |
|---|---|
| Umsatzsteuer | 19 % Regelsatz, Vorsteuerabzug (geschätzt oder exakt), Kleinunternehmer-Option |
| Gewerbesteuer | Freibetrag 24.500 €, Messzahl 3,5 %, Hebesatz konfigurierbar |
| Einkommensteuer | Tarif § 32a EStG (2025 exakt, 2026 hinterlegt), Vorsorgeabzug |
| § 35 EStG | GewSt-Anrechnung (4,0 × Messbetrag) — bei 320 % faktisch volle Anrechnung |
| Solidaritätszuschlag | Freigrenze + Milderungszone |
| Kirchensteuer | optional, 8 % (Bayern/BW) oder frei wählbar |

> **Disclaimer:** Planungswerkzeug für die Rücklagenbildung — keine
> Steuerberatung, kein Ersatz für Steuerbescheid oder Steuerberater.
> Tarifwerte jährlich gegen https://www.bmf-steuerrechner.de prüfen.

## Kernprinzipien (Steuergestalter-Perspektive)

1. **Steuern entstehen auf den Gewinn, nicht auf den Umsatz** — deshalb sind
   Umsatz UND Ausgaben Pflichteingaben; eine reine Umsatz-Prozentregel spart
   systematisch falsch.
2. **Die Umsatzsteuer gehört nie dir** — Durchlaufposten, sofort aufs
   Unterkonto.
3. **Getrennte Töpfe je Steuerart** — USt, GewSt und ESt haben verschiedene
   Empfänger und Fälligkeiten; nur getrennte Salden machen die Deckung je
   Fälligkeit sichtbar.
4. **Rücklage nach echter Steuerlast, nicht nach Vorauszahlungsbescheid** —
   das neutralisiert den Nachzahlungs-Doppeleffekt guter Jahre.
5. **Konservativ runden** — der Rechner ignoriert bewusst kleine
   Entlastungseffekte (z. B. KiSt-Abzug); Überschüsse im Topf sind Puffer.

## Workflow

### Phase 1: Einmalige Einrichtung

1. Qonto-Unterkonten anlegen (siehe
   [references/qonto-kontenstruktur.md](references/qonto-kontenstruktur.md)):
   „Umsatzsteuer", „Gewerbesteuer", „ESt + Soli + KiSt", „Puffer".
2. Persönliches Profil anlegen:
   `cp assets/steuerprofil-beispiel.json steuerprofil.json` und Werte
   anpassen (Hebesatz, Kirche, KV-Beitrag, typische Kostenquote).
3. Qonto-Labels für Einnahmen/Ausgaben-Kategorien definieren, VAT-Erfassung
   aktivieren.
4. Szenario-Tabelle als Orientierung erzeugen:
   ```bash
   python3 scripts/steuerrechner.py --tabelle 6000:16000:2000 \
     --kostenquote 0.25 --kv-monat 850
   ```

### Phase 2: Monatliche Routine (15 Minuten)

1. Vormonat in Qonto filtern → Netto-Umsatz, Netto-Ausgaben, echte Vorsteuer.
2. Rechner ausführen:
   ```bash
   python3 scripts/steuerrechner.py --profil steuerprofil.json \
     --umsatz 12500 --ausgaben 2800 --vorsteuer 410
   ```
3. Die drei ausgewiesenen Beträge vom Hauptkonto auf die Unterkonten
   überweisen, Puffer bedienen.
4. Checkliste abhaken: [assets/monats-checkliste.md](assets/monats-checkliste.md).

### Phase 3: Quartals-Check

1. YTD-Hochrechnung: `--jahreswerte` mit hochgerechnetem Jahresumsatz —
   glättet Ausreißermonate gegen die Progression.
2. Abgleich Rücklage vs. festgesetzte Vorauszahlungen; bei > 20 % Abweichung
   nach unten: Herabsetzungsantrag (siehe
   [references/steuertermine.md](references/steuertermine.md)).
3. Qonto-Auto-Transfer-Prozentsatz nachjustieren.

### Phase 4: Jahreswechsel

1. Neue Tarifwerte prüfen (BMF-Rechner) und ggf. in
   `scripts/steuerrechner.py` (`TARIF_ECKWERTE`, `SOLI_FREIGRENZE`) pflegen.
2. Gestaltungs-Check Dezember: Rürup-Einzahlung (`--sonstige-vorsorge`),
   Investitionen vorziehen (IAB § 7g EStG mit dem Steuerberater prüfen).
3. Nach dem Steuerbescheid: Topf-Salden gegen Nachzahlung/Erstattung
   abrechnen, Überschuss ist frei.

## Tool: `scripts/steuerrechner.py`

Reine Standardbibliothek, Python 3.8+, Text- und JSON-Ausgabe.

```bash
# Standardfall: Monatswerte, Jahr 2026, Hebesatz 320 %
python3 scripts/steuerrechner.py --umsatz 12500 --ausgaben 2800 --kv-monat 850

# Mit Kirchensteuer (Bayern 8 %) und echter Vorsteuer aus Qonto
python3 scripts/steuerrechner.py --umsatz 12500 --ausgaben 2800 --kirche --vorsteuer 410

# Jahreswerte statt Monatswerte (z. B. YTD-Hochrechnung)
python3 scripts/steuerrechner.py --umsatz 150000 --ausgaben 33600 --jahreswerte

# Kleinunternehmer (§ 19 UStG)
python3 scripts/steuerrechner.py --umsatz 1800 --ausgaben 300 --kleinunternehmer

# Szenario-Tabelle über Umsatzstufen
python3 scripts/steuerrechner.py --tabelle 6000:16000:2000 --kostenquote 0.25

# JSON für Weiterverarbeitung/Automatisierung
python3 scripts/steuerrechner.py --umsatz 12500 --ausgaben 2800 --format json
```

**Beispielausgabe (Auszug):**

```
STEUERN AUF GEWINN (Jahr):    33.787,41 EUR
Effektive Belastung Gewinn:   29.0 %
MONATLICHE QONTO-UEBERWEISUNGEN (Ruecklagen-Unterkonten)
   -> Unterkonto 'Umsatzsteuer':   1.843,00 EUR
   -> Unterkonto 'Gewerbesteuer':  857,73 EUR
   -> Unterkonto 'ESt+Soli+KiSt':  1.957,88 EUR
   SUMME RUECKLAGE JE MONAT:       4.658,62 EUR
```

## Resources

**references/**
- [steuergrundlagen.md](references/steuergrundlagen.md) — Rechenwege aller
  Steuerarten, § 35-Anrechnung, Vorauszahlungslogik, Gestaltungshebel
- [qonto-kontenstruktur.md](references/qonto-kontenstruktur.md) — 5-Konten-
  Modell, Monatsroutine, Qonto-Features (Unterkonten, Regeln, VAT, Labels)
- [steuertermine.md](references/steuertermine.md) — Jahreskalender aller
  Fälligkeiten mit Topf-Zuordnung

**assets/**
- [steuerprofil-beispiel.json](assets/steuerprofil-beispiel.json) —
  Profil-Vorlage für persönliche Standardwerte
- [monats-checkliste.md](assets/monats-checkliste.md) — abhakbare
  Monatsroutine

## Grenzen des Modells

- Einzelunternehmer/Grundtarif; keine Zusammenveranlagung (Splitting), keine
  weiteren Einkunftsarten, keine Kinderfreibeträge.
- Gewerbeertrag ≈ Gewinn (keine Hinzurechnungen/Kürzungen § 8/9 GewStG —
  für Dienstleister ohne hohe Miet-/Zinsaufwendungen zutreffend).
- KiSt-Sonderausgabenabzug bewusst ignoriert (konservativ).
- Umsatzsteuer nur Regelsatz 19 % (kein 7 %-Mix).
- Tarifwerte 2026 nach Steuerfortentwicklungsgesetz hinterlegt — vor
  Verwendung gegen den BMF-Rechner verifizieren.
