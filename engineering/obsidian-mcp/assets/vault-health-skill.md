# Vault Health Skill

> Fertige Skill-Datei — in deinen Vault unter `Skills/vault-health.md` kopieren.

---

## When to use

Wöchentlich oder wenn Nutzer sagt: "Analysiere meinen Vault", "Vault-Gesundheit", "Knowledge Graph", "Verwaiste Notizen finden"

---

## Inputs

- Alle `.md`-Dateien im Vault (Volltext-Scan)
- `CLAUDE.md` — für Kontext welche Projekte aktiv sind

---

## Steps

1. Scanne alle Notizen im Vault
2. Analysiere und kategorisiere:
   - **Verwaiste Notizen** — keine eingehenden `[[Links]]`
   - **Tote Links** — `[[Links]]` die auf nicht-existierende Notizen zeigen
   - **Notizen ohne Tags** — kein `#tag` oder YAML `tags:`
   - **Veraltete Notizen** — nicht aktualisiert seit >30 Tagen (prüfe Datum im Frontmatter)
   - **Potenzielle Verbindungen** — Notizen die ähnliche Begriffe enthalten aber nicht verlinkt sind
3. Erstelle Health Report in `Resources & Assets/vault-health-DATUM.md`
4. Frage ob automatische Reparaturen durchgeführt werden sollen:
   - Tote Links markieren (mit `[broken link]`)
   - Fehlende Tags vorschlagen
   - Neue `[[Links]]` zwischen zusammengehörenden Notizen einfügen

---

## Example

```
"Analysiere meinen Vault"
"Vault Health Check"
"Welche Notizen hängen zusammen aber sind nicht verlinkt?"
"Finde alle verwaisten Notizen"
```

---

## Output format

```markdown
---
date: 2026-06-24
type: vault-health
tags: [meta, maintenance]
---

# Vault Health Report — 24. Juni 2026

## Zusammenfassung
- Gesamt-Notizen: [n]
- Verwaiste Notizen: [n] (x%)
- Tote Links: [n]
- Notizen ohne Tags: [n]
- Veraltete Notizen (>30 Tage): [n]

## Verwaiste Notizen
- [[Notiz 1]] — zuletzt bearbeitet: ...
- [[Notiz 2]] — ...

## Tote Links
- In [[Quelle-Notiz]]: broken link → `[[Ziel-Notiz]]`

## Verbindungsvorschläge
- [[Notiz A]] und [[Notiz B]] — beide erwähnen "Thema X", noch nicht verlinkt

## Empfohlene Aktionen
- [ ] [[Notiz X]] mit [[Notiz Y]] verlinken
- [ ] Tag `#projekt` zu [n] Notizen hinzufügen
- [ ] [[Veraltete Notiz]] archivieren oder aktualisieren
```

---

## Save to

`Resources & Assets/vault-health-YYYY-MM-DD.md`

---

*Tags: #skill #maintenance #knowledge-graph #weekly*
