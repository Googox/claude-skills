# Monats-Checkliste Brutto/Netto

15 Minuten am Monatsanfang für den Vormonat. Ziel: zu jeder Fälligkeit ist
das Geld da, und du weißt jederzeit, was dir wirklich gehört.

## 1. Zahlen holen (5 Min)

- [ ] Vormonat im Geschäftskonto filtern
- [ ] **Netto-Umsatz** notieren (ohne Umsatzsteuer)
- [ ] **Netto-Betriebsausgaben** notieren
- [ ] **Echte Vorsteuer** aus den Eingangsrechnungen ablesen (nicht schätzen,
      wenn Versicherungen, Auslandsleistungen oder Bewirtung dabei sind)
- [ ] Privatentnahmen des Vormonats notieren — gehören nicht in die
      Betriebsausgaben

## 2. Rechnen (2 Min)

```bash
python3 scripts/brutto_netto.py --profil mein-profil.json \
  --umsatz <netto-umsatz> --ausgaben <netto-ausgaben> --vorsteuer <vorsteuer>
```

- [ ] Ergebnis mit dem Vormonat vergleichen — Sprünge über 20 % hinterfragen
- [ ] Bei starkem Ausreißer zusätzlich mit `--jahreswerte` auf Basis der
      Jahreshochrechnung rechnen; die Progression verzerrt Einzelmonate

## 3. Überweisen (5 Min)

Die vier Beträge aus Block 6 des Berichts auf getrennte Rücklagenkonten:

- [ ] → Unterkonto **Umsatzsteuer**
- [ ] → Unterkonto **Gewerbesteuer**
- [ ] → Unterkonto **ESt + Soli + KiSt**
- [ ] → Unterkonto **Sozialversicherung** (nur nötig, wenn Beiträge nicht
      ohnehin monatlich abgebucht werden — dann entfällt die Rücklage)
- [ ] Rest ist verfügbar: privat entnehmen oder als Puffer stehen lassen

## 4. Prüfen (3 Min)

- [ ] Umsatzsteuer-Voranmeldung fristgerecht eingereicht (10. des Folgemonats,
      mit Dauerfristverlängerung der 10. des übernächsten Monats)
- [ ] Krankenkassenbeitrag abgebucht
- [ ] Beitrag zur Arbeitslosenversicherung abgebucht — **mehr als drei
      Monate Rückstand beenden die Versicherung automatisch**
- [ ] Altersvorsorge-Beitrag geflossen
- [ ] Saldo der Rücklagenkonten deckt die nächste Fälligkeit

## Quartalsweise zusätzlich

- [ ] Vorauszahlungstermin Einkommensteuer (10.03., 10.06., 10.09., 10.12.)
- [ ] Vorauszahlungstermin Gewerbesteuer (15.02., 15.05., 15.08., 15.11.)
- [ ] Jahreshochrechnung gegen die festgesetzten Vorauszahlungen halten; bei
      Abweichung über 20 % nach unten Herabsetzung beantragen, bei
      Abweichung nach oben freiwillig erhöhen (spart Nachzahlungszinsen)
- [ ] Gewinnprognose an die Krankenkasse melden, wenn sich das Jahresergebnis
      deutlich vom letzten Steuerbescheid entfernt

## Jährlich

- [ ] Rechengrößen des neuen Jahres im Skript ergänzen
      (`references/rechengroessen-2026.md`, Abschnitt „Pflege zum
      Jahreswechsel")
- [ ] Kassenindividuellen Zusatzbeitrag prüfen — er ändert sich zum 1. Januar
- [ ] Dauerauftrag Arbeitslosenversicherung an die neue Bezugsgröße anpassen
- [ ] Im Dezember: Rürup-Einzahlung bis zum Höchstbetrag durchrechnen
