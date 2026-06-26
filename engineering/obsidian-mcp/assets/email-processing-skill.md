# Email Processing Skill

> Fertige Skill-Datei — in deinen Vault unter `Skills/email-processing.md` kopieren.

---

## When to use

Wenn Nutzer sagt: "Check my emails", "E-Mails verarbeiten", "Was habe ich verpasst?", "E-Mail-Zusammenfassung"

---

## Inputs

- Gmail (via MCP) — ungelesene oder wichtige E-Mails (Standard: letzte 24h)
- `CLAUDE.md` — aktive Projekte (für Relevanz-Einschätzung)
- `Projects & Areas/` — aktive Projekte (für Verlinkung)

---

## Steps

1. Durchsuche Gmail nach wichtigen E-Mails der letzten 24h
   - Filter: ungelesen ODER wichtig ODER mit direkter Ansprache
2. Analysiere jede relevante E-Mail:
   - Braucht es eine Antwort? (Ja/Nein, Dringlichkeit: hoch/mittel/niedrig)
   - Welche Action Items enthält sie?
   - Welches aktive Projekt ist betroffen?
3. Erstelle Zusammenfassung in `Notes & Knowledge/Inbox/email-actions-DATUM.md`
4. Dringende Tasks (heute/morgen fällig) → `Tasks & Next Actions/urgent-DATUM.md`
5. Projekt-relevante Infos → als Backlink in betroffene Projekt-Notiz eintragen

---

## Example

```
"Check my emails"
"Schau durch meine E-Mails der letzten 24 Stunden"
"Was muss ich heute noch beantworten?"
```

---

## Output format

```markdown
---
date: 2026-06-24
type: email-digest
tags: [email, inbox]
---

# E-Mail Digest — 24. Juni 2026

## Antwort erforderlich (dringend)
- [ ] **[Absender]** — [Betreff] → Antwort bis: heute
  - Action: ...

## Antwort erforderlich (diese Woche)  
- [ ] **[Absender]** — [Betreff]
  - Action: ...

## Nur zur Kenntnis
- **[Absender]** — [Betreff] (relevant für [[Projekt]])

## Keine Aktion nötig
- [Anzahl] E-Mails ignoriert (Newsletter, CC, Automatisch)
```

---

## Save to

`Notes & Knowledge/Inbox/email-actions-YYYY-MM-DD.md`

Dringende Tasks zusätzlich in: `Tasks & Next Actions/`

---

*Tags: #skill #email #inbox #productivity*
