# Gesamtkosten-Katalog: Was gehört in den Kilometersatz?

Der individuelle Kilometersatz ist `Gesamtkosten ÷ Gesamtfahrleistung`. Der
Zähler entscheidet über die Höhe — und darüber, ob die Rechnung standhält.

## Gehört hinein (Zähler)

| Position | Hinweis | Feld im Profil |
|---|---|---|
| Leasingraten | Summe der im Jahr fälligen Raten | `leasing.monatsrate` |
| Leasingsonderzahlung | **anteilig** über die Laufzeit, nie voll im Zahlungsjahr | `leasing.sonderzahlung` + `laufzeit_monate` |
| Kfz-Haftpflicht + Kasko | Jahresbeitrag | `fixkosten_pa.versicherung` |
| Kfz-Steuer | Jahresbetrag | `fixkosten_pa.kfz_steuer` |
| Garage / Stellplatz | wenn separat angemietet | `fixkosten_pa.stellplatz_garage` |
| Schutzbrief, GAP-Versicherung | fahrzeugbezogen | `fixkosten_pa.schutzbrief_gap` |
| Kraftstoff bzw. Ladestrom | alle Tankbelege des Jahres | `variable_kosten_pa.kraftstoff_strom` |
| Wartung, Inspektion, Ölwechsel | | `variable_kosten_pa.wartung_inspektion` |
| Reifen, Einlagerung, Wechsel | | `variable_kosten_pa.reifen` |
| Reparaturen | auch Verschleiß | `variable_kosten_pa.reparaturen` |
| Hauptuntersuchung / AU | | `fixkosten_pa.hauptuntersuchung` |
| Wagenwäsche, Pflege | | `variable_kosten_pa.pflege_waesche` |
| Mehrkilometer-Nachzahlung | bei Vertragsende, anteilig | `variable_kosten_pa.sonstige_variable` |

**Ladestrom zuhause** ist nur ansetzbar, wenn er messbar erfasst wird
(separater Zähler oder Wallbox-Protokoll). Eine Schätzung ist angreifbar.

## Gehört NICHT hinein

| Position | Warum | Richtige Behandlung |
|---|---|---|
| Parkgebühren, Maut, Fähre | **Reisenebenkosten**, keine Fahrzeugkosten | zusätzlich zum km-Satz **voll** als Betriebsausgabe absetzbar |
| Bußgelder, Verwarnungsgelder | § 4 Abs. 5 Satz 1 Nr. 8 EStG | nicht abziehbar |
| Unfallkosten einer Privatfahrt | privat veranlasst | nicht abziehbar |
| Unfallkosten einer Dienstfahrt | betrieblich, aber Einzelfall | separat als Betriebsausgabe, nicht in den km-Satz |
| ADAC-/Automobilclub-Beitrag | überwiegend privat veranlasst | in der Regel nicht ansetzbar |
| Insassenunfallversicherung | privat | nicht ansetzbar |
| Anschaffungskosten / AfA | beim Leasing nicht vorhanden | entfällt |
| Zinsen einer Fahrzeugfinanzierung | nur bei Kauf auf Kredit | dann in die Fixkosten |

Der Rechner gibt eine Warnung aus, wenn eine Position mit einem dieser Namen im
Profil auftaucht.

## Der Nenner: Gesamtfahrleistung

Immer die **komplette Jahresfahrleistung**, nicht nur die betriebliche. Beste
Quelle sind die Kilometerstände:

```json
"fahrleistung": {
  "km_stand_jahresbeginn": 41230,
  "km_stand_jahresende": 62807
}
```

Beleg dafür: Tacho-Foto mit Datum am 1.1. und 31.12., zusätzlich Werkstatt- und
HU-Berichte (dort steht der Kilometerstand mit Datum drauf — ein starker,
fremdbelegter Nachweis).

Weicht die Summe der Fahrtenbucheinträge von der Kilometerstandsdifferenz ab,
wertet der Rechner die Differenz konservativ als Privatfahrten und warnt.

## Brutto oder netto?

- **Kein Vorsteuerabzug** für das Fahrzeug (Regelfall bei privatem Leasing):
  alle Positionen **brutto** erfassen. Die Umsatzsteuer ist dann echter Aufwand.
- **Anteiliger Vorsteuerabzug** gewählt: Positionen **netto** erfassen und die
  Vorsteuer separat in der Voranmeldung ziehen. Sonst wird die Vorsteuer doppelt
  begünstigt. Siehe [umsatzsteuer-leasing.md](umsatzsteuer-leasing.md).

Innerhalb eines Profils niemals mischen.
