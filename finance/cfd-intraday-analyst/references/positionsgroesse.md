# Positionsgröße in Lots (USD-Konto)

## Formel

Beide Instrumente notieren in USD und das Konto läuft in USD, also gibt es
keine Wechselkurs-Umrechnung.

```
Gewinn/Verlust je Lot = Kontraktgröße x Kursbewegung
Effektiver Abstand     = |Einstieg - Stop| + Spread
Lots (roh)             = Risiko pro Trade USD / (Effektiver Abstand x Kontraktgröße)
Lots                   = auf lot_step abgerundet, nie aufgerundet
```

Ist das Ergebnis kleiner als `min_lot`, **lehnt das Tool ab**. Es rundet nicht
auf die Mindestgröße hoch, denn das würde dein Risiko-Limit überschreiten.

## Rechenbeispiel (Platzhalter-Werte, NICHT Vantage-Werte)

| Größe | Wert |
|---|---|
| Risiko pro Trade | 50 USD |
| Einstieg / Stop | 102,10 / 100,40, also Abstand 1,70 |
| Spread | 0 (im Beispiel) |
| Kontraktgröße | 100 |
| Lot-Schritt | 0,01 |

`50 / (1,70 x 100) = 0,294`, abgerundet **0,29 Lots**. Verlust am Stop:
`0,29 x 100 x 1,70 = 49,30 USD`.

## Pflichtwerte aus MT5 übernehmen

In MT5: **Marktübersicht**, Rechtsklick auf das Symbol (z. B. `XAUUSD` oder
`NAS100`, bei Vantage je nach Kontotyp mit Suffix), dann **Spezifikation**.

| Config-Feld | MT5-Bezeichnung |
|---|---|
| `contract_size` | Kontraktgröße |
| `min_lot` | Minimales Volumen |
| `lot_step` | Volumen-Schritt |
| `max_lot` | Maximales Volumen |
| `price_decimals` | Nachkommastellen (Digits) |
| `spread` | aktueller Spread, umgerechnet in Preiseinheiten (Punkte x Tick-Größe) |
| `leverage` | Hebel deines Kontos für dieses Symbol (optional, nur für die Margin-Schätzung) |

**Kontrolle:** Rechne einmal von Hand nach. Öffne in MT5 ein Order-Fenster mit
`min_lot` und vergleiche den angezeigten Wert je Punkt mit
`min_lot x contract_size`. Stimmt das nicht überein, stimmt die Config nicht.

## Risiko-Grenzen

| Parameter | Wirkung |
|---|---|
| `risk_per_trade_usd` | fester Betrag je Trade (hat Vorrang) |
| `risk_per_trade_pct` + `balance_usd` | Prozent vom Konto |
| `max_daily_loss_usd` | `risk` blockt, wenn der nächste Stop das Tageslimit reißen würde |
| `max_trades_per_day` | `risk` blockt den Trade, der darüber liegt |
| `max_spread_share_of_stop` | `risk` blockt, wenn der Spread mehr als diesen Anteil des Stop-Abstands frisst |

Ein Stop begrenzt den Verlust nur am Stop-Preis. Bei Gaps (Wochenende,
News-Spikes) kann er deutlich schlechter gefüllt werden.
