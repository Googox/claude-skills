# Fahrtenbuch: Formanforderungen und Prüfungsfallen

Der individuelle Kilometersatz steht und fällt mit der Aufzeichnung. Für den
Nachweis der betrieblichen Fahrten und der Gesamtfahrleistung gelten die
gleichen Maßstäbe wie beim klassischen Fahrtenbuch.

## Pflichtangaben je Fahrt

**Betriebliche Fahrt (Auswärtstätigkeit):**

| Angabe | CSV-Spalte |
|---|---|
| Datum | `datum` |
| Kilometerstand bei Fahrtbeginn | `km_stand_start` |
| Kilometerstand bei Fahrtende | `km_stand_ende` |
| Reiseziel (Ort und Adresse, nicht nur „Kunde") | `ziel` |
| Reisezweck | `zweck` |
| aufgesuchter Geschäftspartner | `geschaeftspartner` |

Bei Umwegen: den Grund vermerken (Umleitung, Zwischentermin), sonst fällt die
Differenz zur kürzesten Route auf.

**Fahrt Wohnung ↔ Betriebsstätte:** Kategorie `betriebsstaette`, Kilometerstände
und ein kurzer Vermerk genügen.

**Privatfahrt:** nur Kategorie `privat` und die Kilometerangabe. Ziel und Zweck
müssen **nicht** angegeben werden — die Fahrt muss aber erfasst sein, sonst
stimmt der Nenner nicht.

## Formale Anforderungen

1. **Zeitnah** — am Ende der Fahrt oder am selben Tag. Ein im Januar für das
   Vorjahr erstelltes Fahrtenbuch wird nicht anerkannt.
2. **Geschlossene Form** — fortlaufend, lückenlos, nachträgliche Änderungen
   müssen erkennbar sein. Eine frei überschreibbare Excel-Datei erfüllt das
   **nicht**.
3. **Lückenlose Kilometerstände** — der Endstand einer Fahrt ist der Startstand
   der nächsten. Jede Lücke ist eine nicht erfasste Fahrt.
4. **Vollständig** — alle Fahrten, auch private, auch kurze.

## Zulässige Umsetzungen

| Form | Bewertung |
|---|---|
| Gebundenes Papier-Fahrtenbuch | unproblematisch, aber lästig |
| Elektronisches Fahrtenbuch mit GPS-Box und manipulationssicherer Speicherung | Standardlösung, anerkannt |
| App mit revisionssicherem Log und Änderungshistorie | anerkannt, Anbieterprüfung nötig |
| Excel / Google Sheets | **nicht anerkannt** — frei änderbar, keine Historie |
| CSV wie in diesem Skill | als **Arbeitsdatei** zur Berechnung geeignet; die revisionssichere Aufzeichnung muss daneben existieren |

> Die CSV in diesem Skill ist ein Rechen- und Prüfformat, kein Ersatz für die
> revisionssichere Aufzeichnung. Praktikabler Weg: elektronisches Fahrtenbuch
> führen, Jahresexport in die CSV übernehmen, damit rechnen.

## Was der Prüfer als Erstes macht

| Prüfung | Gegenmaßnahme |
|---|---|
| Kilometerstände gegen Werkstatt- und HU-Rechnungen abgleichen | Rechnungen mit Kilometerstand aufheben |
| Auf gleichmäßige Handschrift / identische Zeitstempel achten | zeitnah führen, nicht nachschreiben |
| Tankbelege gegen Fahrten abgleichen (Ort und Datum) | Tankbelege chronologisch ablegen |
| Auffällig runde Kilometerangaben suchen | echte Tachostände übernehmen |
| Fahrten an Wochenenden/Feiertagen als betrieblich prüfen | Zweck und Partner sauber dokumentieren |
| Lücken zwischen Fahrten suchen | `--strikt` vor dem Jahresabschluss laufen lassen |

Der eingebaute Prüfer meldet Lücken, Überlappungen, Nullkilometer-Fahrten und
fehlende Pflichtangaben:

```bash
python3 scripts/km_kostenrechner.py --profil fahrzeug.json \
  --fahrtenbuch fahrten.csv --strikt
```

Exit-Code 2 heißt: erst korrigieren, dann abrechnen.

## Konsequenz eines verworfenen Fahrtenbuchs

Wird die Aufzeichnung nicht anerkannt, fällt der individuelle Kilometersatz weg.
Übrig bleibt im günstigen Fall die 0,30-EUR-Pauschale für glaubhaft gemachte
Fahrten — im Beispiel dieses Skills ein Unterschied von rund 2.050 EUR
Betriebsausgaben pro Jahr.
