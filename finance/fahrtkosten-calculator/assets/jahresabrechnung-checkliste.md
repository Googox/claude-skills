# Jahresabrechnung — Checkliste

Abzuarbeiten zwischen dem 31.12. und der Übergabe an den Steuerberater.

## 1. Daten vervollständigen

- [ ] Tacho-Foto vom 31.12. gemacht und abgelegt
- [ ] `km_stand_jahresende` im Fahrzeugprofil eingetragen
- [ ] Fahrten der letzten Dezemberwoche nachgetragen
- [ ] Planwerte im Profil durch **Ist-Kosten aus den Belegen** ersetzt:
  - [ ] Leasingraten (Kontoauszüge, Anzahl der Raten im Jahr)
  - [ ] Leasingsonderzahlung + Laufzeit aus dem Vertrag
  - [ ] Versicherungsbeitrag (Jahresrechnung)
  - [ ] Kfz-Steuer (Bescheid)
  - [ ] Kraftstoff / Ladestrom (Summe aller Belege)
  - [ ] Wartung, Reifen, Reparaturen (Werkstattrechnungen)
  - [ ] Stellplatz / Garage
- [ ] Geprüft, dass Brutto/Netto **einheitlich** erfasst ist

## 2. Fahrtenbuch prüfen

```bash
python3 scripts/km_kostenrechner.py --profil fahrzeug.json \
  --fahrtenbuch fahrten-JJJJ.csv --strikt
```

- [ ] Exit-Code 0 — keine Beanstandungen
- [ ] Lücken zwischen Kilometerständen geschlossen
- [ ] Alle Dienstreisen haben Ziel, Zweck und Geschäftspartner
- [ ] Differenz Kilometerstände ↔ Fahrtenbuch unter 1 %
- [ ] Kilometerstände stimmen mit Werkstatt-/HU-Rechnungen überein

## 3. Abrechnen

```bash
python3 scripts/km_kostenrechner.py --profil fahrzeug.json \
  --fahrtenbuch fahrten-JJJJ.csv > jahresabrechnung-JJJJ.txt
```

- [ ] Betrieblicher Anteil notiert: ________ %
- [ ] Bei über 50 %: Modellwechsel mit dem Steuerberater besprochen
- [ ] Individueller Satz gegen die Pauschale geprüft, günstigere Methode gewählt
- [ ] Methode entspricht der unterjährig verwendeten (sonst Korrektur erklären)

## 4. Korrekturbuchung

- [ ] Summe der unterjährigen Eigenbelege ermittelt: ________ EUR
- [ ] Endgültiger Jahresbetrag aus der Abrechnung: ________ EUR
- [ ] Differenz als Korrekturbuchung im Dezember erfasst: ________ EUR
- [ ] Jahres-Eigenbeleg erzeugt und unterschrieben

## 5. Belegpaket für den Steuerberater

- [ ] Jahresabrechnung (`jahresabrechnung-JJJJ.txt`)
- [ ] Fahrtenbuch-Export des Jahres
- [ ] Kostenaufstellung mit allen Einzelbelegen
- [ ] Kilometerstandsnachweise Jahresanfang und Jahresende
- [ ] Leasingvertrag (Rate, Sonderzahlung, Laufzeit, Inklusivkilometer)
- [ ] Alle Eigenbelege des Jahres
- [ ] Vermerk zur Umsatzsteuer-Behandlung (brutto oder netto)

## 6. Für das nächste Jahr

- [ ] Tacho-Foto vom 01.01. als Anfangsstand
- [ ] Neues Fahrtenbuch angelegt
- [ ] Vorläufigen Kilometersatz für die Monatsbuchungen festgelegt
      (Ist-Satz des Vorjahrs, angepasst um bekannte Änderungen)
- [ ] Mehrkilometer-Risiko geprüft: Inklusivkilometer laut Vertrag vs. Ist-Fahrleistung
