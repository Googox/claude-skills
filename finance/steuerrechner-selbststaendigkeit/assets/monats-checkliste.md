# Monats-Checkliste Steuerrücklagen — [MONAT/JAHR]

> Am 3. Werktag des Monats, Dauer ca. 15 Minuten.

## 1. Zahlen aus Qonto (Vormonat)

| Position | Betrag (netto) |
|---|---|
| Umsatz | __________ € |
| Betriebsausgaben | __________ € |
| Tatsächliche Vorsteuer (aus Qonto-VAT-Erfassung) | __________ € |

## 2. Rechner ausführen

```bash
python3 scripts/steuerrechner.py --profil steuerprofil.json \
  --umsatz <UMSATZ> --ausgaben <AUSGABEN> --vorsteuer <VORSTEUER>
```

## 3. Überweisungen Hauptkonto → Unterkonten

| Unterkonto | Betrag lt. Rechner | Erledigt |
|---|---|---|
| „Umsatzsteuer" | __________ € | ☐ |
| „Gewerbesteuer" | __________ € | ☐ |
| „ESt + Soli + KiSt" | __________ € | ☐ |
| „Puffer" (5–10 % vom Umsatz) | __________ € | ☐ |

## 4. Fälligkeiten der nächsten 4 Wochen

| Termin | Zahlung | Topf gedeckt? |
|---|---|---|
| 10\. d. M. | USt-Voranmeldung: __________ € | ☐ |
| 15.02. / 15.05. / 15.08. / 15.11. | GewSt-Vorauszahlung: __________ € | ☐ |
| 10.03. / 10.06. / 10.09. / 10.12. | ESt-Vorauszahlung: __________ € | ☐ |

## 5. Quartalsweise zusätzlich (März / Juni / Sept. / Dez.)

- ☐ YTD-Hochrechnung: läuft das Jahr besser/schlechter als geplant?
  (`--jahreswerte` mit hochgerechnetem Jahresumsatz)
- ☐ Weicht die echte Steuerlast > 20 % von den festgesetzten Vorauszahlungen
  ab? → Herabsetzungsantrag prüfen bzw. Rücklagensatz erhöhen.
- ☐ Qonto-Auto-Transfer-Prozentsatz noch passend?

## Notizen

_______________________________________________
