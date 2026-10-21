---
name: cfd-intraday-analyst
description: Intraday-Analyse für XAU/USD und NAS100 als CFD (z. B. Vantage/MT5). Opening-Range-Breakout an London- und NY-Eröffnung, Long und Short. Signal erst bei Kerzenschluss, Stop und Ziel vor dem Einstieg, Positionsgröße in Lots, 10.000 Replays plus echte Historie, Tageslimits als PASS/BLOCK. Reines Analyse-Werkzeug ohne Broker-Anbindung und ohne Orders. Nutzen bei "Gold Breakout", "NAS100 Signal", "London Open", "NY Open", "Opening Range", "wie viele Lots", "Stop und Ziel", "Replay", "ist das ein Münzwurf", "darf ich noch traden".
---

# CFD Intraday Analyst (XAU/USD, NAS100)

## Overview

Analyse-Werkzeug für den Intraday-Handel von **Gold (XAU/USD)** und **Nasdaq 100
(NAS100)** als CFD. Es beobachtet die ersten Minuten nach der **London-** und
**NY-Eröffnung**, meldet den Ausbruch aus der Opening Range (Long oder Short),
legt Stop und Ziel **vor** dem Einstieg fest, rechnet die Positionsgröße in Lots
und prüft vor jeder Order deine Tageslimits.

**Es platziert nie eine Order.** Die Ausführung bleibt bei dir in MT5.

| Baustein | Befehl | Ergebnis |
|---|---|---|
| Daten | `fetch` / `mt5-import` | 5-Minuten-Kerzen: Yahoo (Proxy) oder dein MT5-Export |
| Signal | `entry` | wartend / ausgelöst (Long/Short) / abgelaufen → `cfd/entry.json` |
| Exit-Plan | `exit` | Stop, Ziel, Chance:Risiko, spätester Ausstieg → `cfd/plan.json` |
| Größe | `size` | Lots aus Risiko, Stop-Abstand, Kontraktgröße → `cfd/size.json` |
| Realitäts-Check | `replay` | 10.000 Durchläufe + dieselbe Regel auf echten Sessions + Urteil |
| Freigabe | `risk` | PASS oder BLOCK mit Begründung |
| Journal | `journal` | Tagesergebnisse für die Tageslimits |

> **Disclaimer:** Software, die Kurse liest und rechnet. Keine Anlageberatung.
> CFDs sind gehebelt, und die Mehrheit der Privatkunden verliert damit Geld. Ein
> PASS ist eine Regelprüfung, keine Empfehlung. Ein Replay ist keine Prognose.

## Kernprinzipien

1. **Kerzenschluss, nicht Docht.** Ein Signal zählt erst, wenn eine
   5-Minuten-Kerze außerhalb der Range *schließt*.
2. **Stop und Ziel vor dem Einstieg.** Im schnellen Markt wird nichts mehr
   entschieden.
3. **Größe folgt dem Stop.** Weiter Stop heißt weniger Lots. Passt die
   Mindestgröße nicht ins Risiko, lautet die Antwort „kein Trade“ und nicht
   „Stop enger“.
4. **Ehrliche Statistik.** Das Replay-Urteil wird wörtlich wiedergegeben. Ein
   Münzwurf wird nicht schöngeredet.
5. **Keine erfundenen Broker-Werte.** Kontraktgröße, Lot-Schritt und Spread
   kommen aus deinem MT5. Fehlen sie, stoppt `size`.

## Workflow

### Phase 1: Einmalige Einrichtung

1. Config anlegen: `mkdir -p cfd && cp assets/config.example.json cfd/config.json`
2. In MT5 je Symbol die **Spezifikation** öffnen und `contract_size`,
   `min_lot`, `lot_step`, `max_lot`, `price_decimals`, `spread` eintragen
   (siehe [references/positionsgroesse.md](references/positionsgroesse.md)).
3. Risiko setzen: `risk_per_trade_usd` (oder `risk_per_trade_pct` plus
   `balance_usd`), `max_daily_loss_usd`, `max_trades_per_day`.
4. Optional MT5-Daten importieren und den Serverzeit-Offset bestimmen (siehe
   [references/mt5-export.md](references/mt5-export.md)).
5. `python3 scripts/cfd_analyst.py selftest` muss „Alle Prüfungen bestanden“
   melden.

### Phase 2: Pro Session (London ab 09:00 Uhr, NY ab 15:30 Uhr deutscher Zeit)

```bash
S=scripts/cfd_analyst.py
python3 $S entry --instrument XAUUSD --session london --write    # Status nach der Range
python3 $S exit --stop or-mid --target 2R --write                # Stop/Ziel vor dem Einstieg
python3 $S replay --write                                        # Münzwurf oder Kante?
python3 $S size --write                                          # Lots
python3 $S risk                                                  # PASS / BLOCK
```

Ablauf für Claude:

1. `entry` ausführen und den Status in einer Zeile nennen. Ist das Signal
   mehr als 2 Kerzen alt, das ausdrücklich sagen: Ein später Einstieg ist ein
   anderer Trade.
2. Bei einem Signal `exit`, dann `replay`. Das Urteil **wörtlich**
   wiedergeben, dazu den Seed und den Hinweis „Simulation, keine Prognose“.
   Bei „Münzwurf“ oder „Richtung Stop“ deutlich davon abraten, statt den Trade
   schönzureden.
3. `size`, dann `risk`. Bei BLOCK die Begründung nennen und nichts lockern.
4. Bei PASS die Eckdaten zusammenfassen: Richtung, Einstieg, Stop, Ziel, Lots,
   Verlust am Stop, spätester Ausstieg. Die Order gibt Aaron selbst in MT5 ein.
5. Nach dem Trade: `journal add --instrument XAUUSD --pnl -48.50`.

### Phase 3: Wöchentlich

- `replay` für beide Instrumente und Sessions mit den aktuellen Daten laufen
  lassen und die Historienzeile vergleichen. Driftet die Bilanz einer
  Kombination dauerhaft unter Break-even, wird diese Session gestrichen und
  nicht die Regel nachjustiert.

## Befehle im Detail

| Befehl | Wichtige Optionen |
|---|---|
| `entry` | `--instrument`, `--session london\|ny`, `--data FILE`, `--now "YYYY-MM-DD HH:MM"` (deutsche Zeit, zum Nachspielen), `--write` |
| `exit` | `--stop or-mid\|or-opposite\|atr:K\|pct:X\|price:X`, `--target 2R\|1.5R\|price:X`; vorplanen mit `--entry --direction --or-high --or-low` |
| `size` | `--balance USD`, `--write` |
| `replay` | `--replays 10000`, `--seed 19`, `--window 2`, `--min-sessions 20`, `--data FILE` |
| `risk` | `--now` |
| `journal` | `add --instrument --pnl [--date --note]`, `show [--date]` |
| `fetch` | `--instrument`, `--range 60d` |
| `mt5-import` | `FILE --instrument --server-offset ny-close\|2` |

Alle Befehle haben `--format json`, `--dir` (Standard `cfd`) und `--config`.
Exit-Codes: 0 ok/PASS, 1 Eingabefehler, 2 BLOCK oder Ablehnung.

## So rechnet `replay`

1. **Pool:** alle vollständigen vergangenen Sessions (Eröffnung bis
   `flat_by`) in den Daten, mindestens 20.
2. **Ein Durchlauf:** Vom Einstiegspreis aus wird für jede restliche Kerze
   eine historische Kerze derselben Tageszeit (±2 Kerzen) gezogen und
   prozentual übertragen. Berührt eine Kerze Stop und Ziel zugleich, zählt
   der Stop.
3. **Historie:** Dieselbe Regel (Range, Stop-Regel, Ziel-R) läuft auf jeder
   echten Session, getrennt nach Long und Short.
4. **Urteil:** Unter den Durchläufen, die Stop oder Ziel erreichen, wird die
   Ziel-Quote mit dem Break-even `1/(1+R)` verglichen (50 % bei 1R, 33 % bei 2R).
   Unter 5 Punkten Abstand heißt das „Münzwurf“ bzw. „Break-even“, 5 bis 15
   Punkte „tendiert“, ab 15 Punkten „deutlich“.

## Datenquellen

- **Yahoo `GC=F` / `NQ=F` (Standard):** kostenlos, inoffiziell und mit
  möglicher Verzögerung. Es sind **Futures-Kurse als Proxy**, die Level
  weichen vom Vantage-CFD ab. Abstände und R-Werte sind vergleichbar.
- **MT5-Export (empfohlen für echte Level):** deine Vantage-Kurse, mit
  Serverzeit-Offset.
- **Abweichung von der Finance-Konvention:** `fetch` und das automatische
  Nachladen rufen Yahoo über das Netz ab. Alles andere läuft lokal. Ohne
  Netz geht es mit `--data` bzw. `mt5-import`.

## Reference Documentation

- [references/session-logik.md](references/session-logik.md): Zeiten,
  Sommerzeit-Verschiebung, die Regel, News-Termine, Grenzen der Datenquellen
- [references/positionsgroesse.md](references/positionsgroesse.md): Lot-Formel,
  MT5-Spezifikation, Risiko-Parameter
- [references/mt5-export.md](references/mt5-export.md): Export, Serverzeit-Offset,
  Import, Plausibilitätscheck

## Assets

- [assets/config.example.json](assets/config.example.json): Vorlage für
  `cfd/config.json`. Broker-Werte sind bewusst `null`.

## Was dieses Werkzeug nie tut

Es platziert keine Order, verbindet sich mit keinem Broker, liest keine
Zugangsdaten, verschiebt keinen Stop nachträglich, rundet Lots nie auf und
verkauft eine Simulation nicht als Prognose.

## Technisches

- Python 3.8+, nur Standardbibliothek, eine Datei: `scripts/cfd_analyst.py`
- Zeitzonen-Regeln (EU/UK/USA) eingebaut, ohne `zoneinfo`
- Offline-Selbsttest auf synthetischen Daten: `python3 scripts/cfd_analyst.py selftest`

## Herkunft

Die Methodik (Signal erst bei Kerzenschluss, Stop und Ziel vor dem Einstieg,
Replay aus der eigenen Historie mit festem Seed, Break-even-Urteil) ist
angelehnt an [Jakeschincariol/day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill)
(MIT, © 2026 Jake Schincariol). Der Code ist neu geschrieben, und zwar für CFDs,
Long und Short, London und NY sowie Lots statt Aktien.
