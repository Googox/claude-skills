---
description: Draft a professional email using cs-content-creator and save it to Gmail Drafts
---

Route to **cs-content-creator → Gmail MCP**.

1. Ask the user for: email purpose, recipient (role/name), key message or ask, and desired tone (if not in $ARGUMENTS).

2. **Search for relevant context in Gmail** (optional):
   - Use `mcp__5c59a741-7084-4188-a9af-4546d6957875__search_threads` to find previous correspondence with this person/topic
   - Summarise thread history if found, so the draft is contextually aware

3. **Read content creation references:**
   ```bash
   cat marketing-skill/content-creator/references/brand_guidelines.md
   ```

4. **Draft the email as cs-content-creator:**
   - Subject line (2-3 variants)
   - Opening that references context or shared ground
   - Clear body with one primary message
   - Specific, low-friction call to action
   - Professional sign-off

5. **Validate brand voice:**
   ```bash
   python marketing-skill/content-creator/scripts/brand_voice_analyzer.py <draft-file>
   ```

6. **Save to Gmail Drafts** (confirm with user before saving):
   - Use `mcp__5c59a741-7084-4188-a9af-4546d6957875__create_draft` with the final draft
   - Include all subject variants as a note at the top of the draft body

7. **Deliver:** Confirm draft is saved + show the final email text.

**Common use cases:**
- Investor outreach → use with `/ceo-brief` context
- Partnership proposal → use with cs-demand-gen context
- Customer follow-up → pull HubSpot context first with `/campaign-report`
- Hiring outreach → use with Company Data MCP research
