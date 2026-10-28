---
typ: steuerung
geschaeft: aa
---

# Pipeline A/A Executive Search

Diese Seite rechnet, Claude bewertet. Voraussetzung: Community-Plugin Dataview.

## 1 Sofort dran (ueberfaellig)

```dataview
TABLE unternehmen AS "Unternehmen",
      naechste_aktion AS "Naechste Aktion",
      (date(today) - naechste_aktion_am).days AS "Tage ueberfaellig"
FROM "10-Kontakte"
WHERE typ = "kontakt" AND geschaeft = "aa"
  AND status != "abgesagt" AND naechste_aktion_am < date(today)
SORT naechste_aktion_am ASC
```

## 2 Diese Woche

```dataview
TABLE unternehmen AS "Unternehmen",
      naechste_aktion AS "Naechste Aktion",
      naechste_aktion_am AS "Zieldatum"
FROM "10-Kontakte"
WHERE typ = "kontakt" AND geschaeft = "aa"
  AND naechste_aktion_am >= date(today)
  AND naechste_aktion_am <= date(today) + dur(7 days)
SORT naechste_aktion_am ASC
```

## 3 Bestaetigte Pitch-Termine

```dataview
TABLE unternehmen AS "Unternehmen",
      naechste_aktion_am AS "Termin",
      temperatur AS "Temperatur"
FROM "10-Kontakte"
WHERE typ = "kontakt" AND status = "pitch_terminiert"
SORT naechste_aktion_am ASC
```

## 4 Ruhend

```dataview
TABLE unternehmen AS "Unternehmen",
      naechste_aktion_am AS "Naechste Beruehrung"
FROM "10-Kontakte"
WHERE typ = "kontakt" AND status = "ruhend"
SORT naechste_aktion_am ASC
```

## 5 Kernpipeline in gesetzter Reihenfolge

```dataview
TABLE pipeline_rang AS "Rang", temperatur AS "Temp",
      letzte_interaktion_am AS "Letzter Kontakt"
FROM "10-Kontakte"
WHERE welle = "kern" AND pipeline_rang
SORT pipeline_rang ASC
```

## Mandate nach Phase

```dataview
TABLE mandant, phase, fee_modell, ziel_platzierung_am
FROM "30-Mandate"
WHERE typ = "mandat" AND phase != "abgeschlossen"
SORT ziel_platzierung_am ASC
```

## Marktbeobachtungen, Entscheidung offen

```dataview
TABLE person, unternehmen_neu, relevanz, quelle
FROM "50-Markt"
WHERE typ = "marktbeobachtung" AND relevanz = "pipeline"
  AND kontakt_angelegt = false
SORT erfasst_am DESC
```

## Leck-Erkennung: aktiv, aber 30 Tage kein Kontakt

```dataview
TABLE unternehmen, letzte_interaktion_am, temperatur
FROM "10-Kontakte"
WHERE typ = "kontakt" AND status = "aktiv"
  AND letzte_interaktion_am < date(today) - dur(30 days)
SORT letzte_interaktion_am ASC
```
