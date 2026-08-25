# Eigenbeleg — Nutzungseinlage Fahrzeugkosten

*Zum Ausdrucken und Unterschreiben. Automatisch erzeugen mit:*
`python3 scripts/km_kostenrechner.py --profil fahrzeug.json --fahrtenbuch fahrten.csv --monat JJJJ-MM --eigenbeleg`

---

**Betrieb:** ______________________________________________

**Inhaber:** ______________________________________________

**Steuernummer:** _________________________________________

**Abrechnungszeitraum:** ☐ Monat ______ / ______  ☐ Jahr ______

**Belegdatum:** ___________________  **Beleg-Nr.:** ___________

---

### Fahrzeug

| | |
|---|---|
| Bezeichnung | |
| Kennzeichen | |
| Halter / Leasingnehmer | privat (Inhaber persönlich) |
| Leasingvertrag Nr. | |

### Berechnung

| | |
|---|---|
| Fahrzeug-Gesamtkosten des Jahres | ______________ EUR |
| Gesamtfahrleistung des Jahres | ______________ km |
| **Individueller Kilometersatz** | ______________ EUR/km |
| Alternativ: Pauschale | 0,30 EUR/km |
| Angewandte Methode | ☐ individuell  ☐ pauschal |
| Betrieblich gefahrene Kilometer im Zeitraum | ______________ km |
| **Betrag der Nutzungseinlage** | **______________ EUR** |

☐ Vorläufiger Satz (unterjährige Buchung, Korrektur zum Jahresende)
☐ Endgültiger Satz (Ist-Kosten und Ist-Fahrleistung)

### Rechtsgrundlage

Nutzungseinlage der auf betriebliche Fahrten entfallenden Aufwendungen eines
privat geleasten Fahrzeugs, § 4 Abs. 4 EStG. Kein Leistungsaustausch zwischen
Inhaber und Einzelunternehmen, daher keine Umsatzsteuer und kein gesonderter
Vorsteuerausweis.

### Buchung

| Kontenrahmen | Soll | Haben |
|---|---|---|
| SKR03 | 4670 Reisekosten Unternehmer Fahrtkosten | 1890 Privateinlagen |
| SKR04 | 6670 Reisekosten Unternehmer Fahrtkosten | 2180 Privateinlagen |

*Kontennummern mit dem eigenen Kontenrahmen abgleichen.*

### Anlagen

☐ Fahrtenbuch des Abrechnungszeitraums
☐ Kostenaufstellung des Jahres mit Einzelbelegen
☐ Kilometerstandsnachweis (Tacho-Foto, Werkstattrechnung)
☐ Leasingvertrag inkl. Sonderzahlung und Laufzeit

---

Ort, Datum: ____________________________

Unterschrift: __________________________
