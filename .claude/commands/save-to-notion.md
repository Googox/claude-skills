---
description: Save any agent output (brief, plan, report, doc) to a Notion page — works after any other slash command
---

Route to **Notion MCP** — save the current conversation output to Notion.

1. Ask the user: which Notion page or database to save to (if not in $ARGUMENTS). If unknown, search for it.

2. **Find the target location in Notion:**
   - Use `mcp__ced01181-861e-4906-ab56-c4389119e8b1__search` with the user's page name or keyword
   - Show the user the top 3 matches to confirm the correct target

3. **Prepare the content:**
   - Use the output from the previous slash command or the current conversation
   - Format it as clean Notion blocks: headings, bullet lists, tables, code blocks
   - Add metadata: date created, source agent, sprint/project tag

4. **Save to Notion** (confirm with user before writing):
   - If saving as a **new page**: use `mcp__ced01181-861e-4906-ab56-c4389119e8b1__create_pages`
   - If updating an **existing page**: use `mcp__ced01181-861e-4906-ab56-c4389119e8b1__update_page`
   - If saving to a **database**: use `mcp__ced01181-861e-4906-ab56-c4389119e8b1__create_pages` with database parent

5. **Confirm** — Show the user the Notion page URL after saving.

**Typical usage after other commands:**
```
/sprint-plan          → /save-to-notion Sprint 23 Plan
/plan-campaign        → /save-to-notion Q3 Campaign
/ceo-brief            → /save-to-notion Board Deck Notes
/regulatory-audit     → /save-to-notion ISO 13485 Audit Report
```
