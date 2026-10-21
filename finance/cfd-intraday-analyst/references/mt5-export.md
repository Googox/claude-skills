# MT5-Export für exakte Vantage-Kurse

Yahoo liefert nur Futures-Kurse als Proxy. Für die Kurse, die du bei Vantage
tatsächlich handelst, exportierst du die Kerzen aus MetaTrader 5.

## Export (MT5 Desktop)

1. **Ansicht → Symbole** (oder `Strg+U`).
2. Reiter **Balken** wählen.
3. Symbol wählen (z. B. `XAUUSD`, `NAS100`, ggf. mit Kontosuffix), Zeitrahmen
   **M5** (oder M1, das Tool verdichtet auf M5), Zeitraum möglichst lang
   (mindestens 2 bis 3 Monate für `replay`).
4. **Abfrage**, dann **Balken exportieren** → CSV speichern.

Menübezeichnungen können je nach MT5-Version und Sprache leicht abweichen.

## Serverzeit-Offset bestimmen (Pflicht)

MT5-Zeitstempel sind **Serverzeit des Brokers**, nicht UTC. Ohne den richtigen
Offset liegt die Opening Range an der falschen Stelle, und dann ist jede
Auswertung falsch.

So ermittelst du ihn:

1. Uhrzeit in der MT5-Marktübersicht (Serverzeit) ablesen.
2. Mit der aktuellen UTC-Zeit vergleichen (deutsche Zeit minus 1 Stunde im
   Winter, minus 2 Stunden im Sommer).
3. Die Differenz ist der Offset.

| Beobachtung | `--server-offset` |
|---|---|
| Server = UTC+2 im Winter, UTC+3 während der US-Sommerzeit | `ny-close` (häufige Broker-Konvention, bei Vantage **selbst prüfen**) |
| Fester Offset, z. B. immer UTC+2 | `2` |

Ich habe den Offset von Vantage nicht verifiziert. Prüf ihn einmal, dann ist
er für alle Exporte gesetzt.

## Import

```bash
python3 scripts/cfd_analyst.py mt5-import ~/Downloads/XAUUSD_M5.csv \
    --instrument XAUUSD --server-offset ny-close
# -> cfd/data/XAUUSD-5m.json, wird danach automatisch von entry/exit/replay genutzt
```

Erkannt werden Tab-, Komma- und Semikolon-Trennung, mit Kopfzeile
(`<DATE> <TIME> <OPEN> ...`) oder ohne. Bei M1-Daten wird auf M5 verdichtet.

**Plausibilitätscheck nach dem Import:** `entry --now "<Tag> 09:20"` für die
London-Session laufen lassen. Das gemeldete Range-Hoch und -Tief muss zu dem
passen, was du im MT5-Chart von 09:00 bis 09:15 Uhr deutscher Zeit siehst.

**Achtung Cache:** Nach dem Import liegt die Datei unter `cfd/data/`. Solange
du dort MT5-Daten liegen hast, holt das Tool keine Yahoo-Daten mehr für dieses
Instrument. Für ein Live-Signal brauchst du also einen frischen Export, oder du
gibst mit `--data` gezielt die Yahoo-Datei an.
