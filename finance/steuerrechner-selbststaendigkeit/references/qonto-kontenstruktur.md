# Qonto-Kontenstruktur für transparente Steuerrücklagen

Ziel: Jeden Monat wandert die errechnete Steuerrücklage vom Hauptkonto auf
dedizierte Unterkonten, sodass das Hauptkonto **nur noch frei verfügbares
Geld** zeigt. Keine Überraschungen bei Vorauszahlungen, Voranmeldungen oder
der Steuererklärung.

## Empfohlene Kontenstruktur (5 Konten)

| # | Qonto-Konto | Zweck | Speist sich aus |
|---|---|---|---|
| 1 | **Hauptkonto (Betrieb)** | Alle Einnahmen und Betriebsausgaben | Kundenzahlungen |
| 2 | **Unterkonto „Umsatzsteuer"** | USt-Zahllast bis zur Voranmeldung | Rechner: `unterkonto_umsatzsteuer` |
| 3 | **Unterkonto „Gewerbesteuer"** | GewSt-Vorauszahlungen an die Gemeinde | Rechner: `unterkonto_gewerbesteuer` |
| 4 | **Unterkonto „ESt + Soli + KiSt"** | ESt-Vorauszahlungen und Nachzahlung | Rechner: `unterkonto_est_soli_kist` |
| 5 | **Unterkonto „Puffer/Rücklage"** | 5–10 % vom Umsatz: Nachzahlungs-Doppeleffekt, GKV-Spitzabrechnung, magere Monate | Fester Prozentsatz |

Warum getrennte Töpfe statt eines Sammel-„Steuerkontos": Die drei Steuerarten
haben **unterschiedliche Fälligkeiten und Empfänger** (USt monatlich ans
Finanzamt, GewSt vierteljährlich an die Gemeinde, ESt vierteljährlich ans
Finanzamt). Getrennte Salden zeigen sofort, ob jeder Topf zur nächsten
Fälligkeit gedeckt ist — das ist die Transparenz, die eine Sammelrücklage
nicht liefert.

## Monatliche Routine (ca. 15 Minuten, z. B. am 3. Werktag)

1. **Zahlen ziehen:** In Qonto den Vormonat filtern — Netto-Umsatz und
   Netto-Betriebsausgaben notieren (Labels/Kategorien, s. u.).
2. **Rechner laufen lassen:**
   ```bash
   python3 scripts/steuerrechner.py --profil steuerprofil.json \
     --umsatz <NETTO-UMSATZ VORMONAT> --ausgaben <NETTO-AUSGABEN VORMONAT>
   ```
   Bei stark schwankenden Monaten stattdessen mit dem **Jahres-Forecast**
   rechnen (`--jahreswerte` mit YTD-Hochrechnung), damit die Progression
   nicht von einem Ausreißermonat verzerrt wird.
3. **Drei Überweisungen ausführen** (Hauptkonto → Unterkonten) gemäß Block
   „MONATLICHE QONTO-UEBERWEISUNGEN" der Rechner-Ausgabe.
4. **Puffer bedienen:** 5–10 % vom Umsatz auf Unterkonto 5.
5. **Fälligkeits-Check:** Steht in den nächsten 4 Wochen eine Vorauszahlung
   an (siehe Terminplan)? Deckt der jeweilige Topf den Betrag?

## Qonto-Funktionen gezielt nutzen

- **Unterkonten (Accounts):** Jedes Rücklagenkonto als eigenes Konto mit
  eigener IBAN anlegen — GewSt- und ESt-Vorauszahlungen dann **direkt vom
  jeweiligen Unterkonto** per Überweisung/Lastschrift zahlen. So ist im
  Kontoauszug je Topf lückenlos nachvollziehbar: Zufluss Rücklage → Abfluss
  Finanzamt/Gemeinde.
- **Regeln/Auto-Transfer:** Qonto kann Zuflüsse prozentual automatisch auf
  Unterkonten verteilen. Sinnvolle Automatik-Basis: den vom Rechner
  ausgewiesenen Gesamtsatz (Summe Rücklage ÷ Umsatz) als Prozentregel
  hinterlegen und quartalsweise nachjustieren.
- **Labels/Kategorien:** Konsistent pflegen (z. B. `Honorar`, `Software`,
  `Reise`, `Versicherung`, `Privat`) — dann liefert der Monatsfilter die
  Rechner-Eingaben in Sekunden, und der Steuerberater bekommt saubere Exporte.
- **VAT-Erkennung:** Qonto kann die USt je Beleg erfassen — damit liegt die
  **tatsächliche Vorsteuer** des Monats vor. Diese statt der 19 %-Schätzung
  per `--vorsteuer` an den Rechner geben (genauer!).

## Faustformeln zur Plausibilisierung

Bei ~25 % Kostenquote und Hebesatz 320 % liegt die Gesamtrücklage
(inkl. USt-Zahllast) typischerweise bei:

| Netto-Umsatz/Monat | Rücklage gesamt | in % vom Umsatz |
|---|---|---|
| 6.000 € | ~1.570 € | ~26 % |
| 10.000 € | ~3.310 € | ~33 % |
| 14.000 € | ~5.200 € | ~37 % |

(Werte aus `--tabelle 6000:16000:2000 --kostenquote 0.25 --kv-monat 800`;
mit eigenen Parametern neu erzeugen.)

**Merksatz:** Unter ~30 % Gesamtrücklage vom Umsatz wird es bei gutem
Geschäftsverlauf fast immer knapp. Lieber konservativ zurücklegen — was am
Jahresende im ESt-Topf übrig bleibt, ist die schönste „Steuererstattung",
die es gibt: die eigene.
