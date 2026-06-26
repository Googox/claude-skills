# Morning Briefing Skill

> Fertige Skill-Datei — in deinen Vault unter `Skills/morning-briefing.md` kopieren.

---

## When to use

Morgens, oder wenn Nutzer sagt: "Guten Morgen", "Good morning", "Starte meinen Tag", "Was steht heute an?"

---

## Inputs

- `CLAUDE.md` (Vault-Root) — Ziele und aktive Projekte
- Google Calendar — heutige Termine (via MCP)
- `Tasks & Next Actions/` — offene Aufgaben
- Gestrige Daily Note (optional)

---

## Steps

1. Lies `CLAUDE.md` für aktuellen Kontext und Projekte
2. Rufe heutige Kalender-Events ab (Google Calendar MCP)
3. Rufe morgige Termine ab (für Vorausplanung)
4. Lese offene Tasks aus `Tasks & Next Actions/`
5. Erstelle Daily Note für heute: `Notes & Knowledge/Daily Notes/YYYY-MM-DD.md`
6. Befülle die Daily Note mit:
   - Heutiges Datum als Titel
   - Termine mit Uhrzeit und Teilnehmern
   - Vorbereitungshinweise für wichtige Meetings
   - Top 3 Prioritäten (abgeleitet aus Projekten + offenen Tasks)
   - Leere Abschnitte: ## Notes, ## Done, ## Daily Review

---

## Example

```
"Guten Morgen"
"Good morning. Start my day."
"Was steht heute an?"
```

---

## Output format

```markdown
---
date: 2026-06-24
type: daily-note
tags: [daily]
---

# Dienstag, 24. Juni 2026

## Termine heute
- 09:00 — Team Standup (30 Min)
- 14:00 — Kundengespräch mit [Name] (1h) → Vorbereitung: [[Projects & Areas/Projektname]]
- 16:30 — Review-Meeting

## Top 3 Prioritäten
- [ ] 
- [ ] 
- [ ] 

## Notes

## Done

## Daily Review
```

---

## Save to

`Notes & Knowledge/Daily Notes/YYYY-MM-DD.md` (neu erstellen oder aktualisieren)

---

*Tags: #skill #routine #morning #calendar*
