# Session-Logik: London- und NY-Eröffnung

Das Tool rechnet intern in UTC und gibt Zeiten in **deutscher Zeit** plus Ortszeit
der Börse aus. Sommer- und Winterzeit sind eingebaut (EU: letzter Sonntag im März
bis letzter Sonntag im Oktober; USA: zweiter Sonntag im März bis erster Sonntag im
November).

## Eröffnungszeiten in deutscher Zeit

| Session | Ortszeit | Deutsche Zeit (Normalfall) | In den Verschiebe-Wochen |
|---|---|---|---|
| London | 08:00 London | 09:00 Uhr | 09:00 Uhr (EU und UK wechseln gleichzeitig) |
| New York | 09:30 New York | 15:30 Uhr | 14:30 Uhr |

**Verschiebe-Wochen:** Die USA stellen früher auf Sommerzeit und später auf
Winterzeit um als Europa. 2026 öffnet New York deshalb vom 09.03. bis 27.03.
und vom 26.10. bis 30.10. bereits um **14:30 Uhr deutscher Zeit**. Das Tool
berücksichtigt das automatisch. Wer sich nach der Uhr richtet, verpasst in
diesen Wochen die Eröffnung.

## Standard-Fenster (Vorschläge, in der Config änderbar)

| Parameter | London | New York | Bedeutung |
|---|---|---|---|
| `or_minutes` | 15 | 15 | Länge der Opening Range |
| `no_entries_after` | 11:00 | 11:30 | Kein neues Signal danach (Ortszeit) |
| `flat_by` | 16:00 | 15:55 | Spätester Ausstieg, egal wie (Ortszeit) |

Die Fenster sind Startwerte, kein geprüftes Optimum. Mit `replay` auf eigenen
Daten testen, bevor du sie veränderst, und immer nur einen Parameter auf einmal.

## Die Regel

1. **Opening Range:** Hoch und Tief der ersten `or_minutes` ab Eröffnung
   (bei 15 Minuten die ersten drei 5-Minuten-Kerzen).
2. **Signal:** die erste abgeschlossene Kerze nach der Range, die **über dem
   Hoch schließt** (Long) oder **unter dem Tief schließt** (Short). Ein Docht
   über die Marke zählt nicht.
3. **Ein Signal pro Session.** Spätere Schlüsse setzen es nicht zurück.
4. **Nach `no_entries_after`** ist das Setup abgelaufen.

## Termine, die das Setup sprengen

Diese US-Termine liegen in oder kurz vor dem NY-Fenster und treiben beide
Instrumente. Vor allem an diesen Tagen kennt der Replay-Pool den Ausnahmezustand
nicht.

| Termin | Uhrzeit New York | Deutsche Zeit (Normalfall) |
|---|---|---|
| Arbeitsmarkt (NFP), CPI | 08:30 | 14:30 Uhr, also vor der Eröffnung |
| FOMC-Zinsentscheid | 14:00 | 20:00 Uhr, also im laufenden Trade bis flat_by |

Für Gold kommen dazu: Dollar-Index (DXY), US-Realzinsen und geopolitische Schlagzeilen.
Für NAS100: Quartalszahlen der großen Tech-Werte (meist nach US-Börsenschluss,
wirken also auf den nächsten Tag).

## Datenquellen und ihre Grenzen

| Quelle | Instrument | Grenze |
|---|---|---|
| Yahoo `GC=F` | Gold-Future (COMEX), Proxy für XAU/USD | Future-Preis liegt um die Terminprämie über Spot-Gold. Level weichen vom Vantage-Chart ab, Abstände sind vergleichbar. |
| Yahoo `NQ=F` | Nasdaq-100-Future, Proxy für NAS100 | CFD-Preis kann um den Fair-Value-Aufschlag abweichen. |
| MT5-Export | Dein echtes Vantage-Symbol | Exakte Preise, aber ein manueller Export. Serverzeit-Offset muss stimmen (siehe mt5-export.md). |

Faustregel: **Level zum Handeln aus MT5, Statistik (`replay`) aus der Quelle mit
der längsten sauberen Historie.** Yahoo liefert 5-Minuten-Kerzen nur für etwa
60 Tage. Ein MT5-Export kann deutlich mehr liefern.
