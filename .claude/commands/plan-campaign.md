---
description: Plan a full marketing campaign end-to-end — strategy via cs-demand-gen-specialist, then copy via cs-content-creator
---

Route to **HubSpot MCP + Contact Enrichment → cs-demand-gen-specialist → cs-content-creator** (sequential).

**Phase 0 — CRM Context (optional, if HubSpot is connected):**

1. Pull relevant audience data from HubSpot:
   - Use `mcp__8f2d65aa-2677-4cb9-a737-0c262e56a201__query_crm_data` to find existing contacts matching the target segment
   - Use `mcp__8f2d65aa-2677-4cb9-a737-0c262e56a201__search_crm_objects` to find relevant companies or deals
   - Use `mcp__0b3a87ea-6e00-4875-b1d6-c25f6164a800__ask-question-about-accounts` for enrichment context if targeting new accounts
   - Summarise: segment size, avg deal size, typical buying journey length

**Phase 1 — Campaign Strategy (cs-demand-gen-specialist):**

2. Ask the user for: campaign goal, target audience, budget range, timeline, and primary channel (if not in $ARGUMENTS).
2. Read the demand acquisition skill:
   ```bash
   cat marketing-skill/marketing-demand-acquisition/SKILL.md
   ```
3. Produce:
   - Campaign brief (goal, audience, channels, budget split, KPIs)
   - Channel strategy with expected CPL/CPA per channel
   - Funnel map (awareness → consideration → conversion)

**Phase 2 — Campaign Content (cs-content-creator):**

4. Using the campaign brief from Phase 1:
   ```bash
   cat marketing-skill/content-creator/references/content_frameworks.md
   ```
5. Create all copy assets:
   - Ad headlines and descriptions (3 variants per channel)
   - Landing page copy
   - Email nurture sequence (3 emails)
   - Social media posts (LinkedIn + Twitter/X)
6. Validate brand voice and SEO on landing page:
   ```bash
   python marketing-skill/content-creator/scripts/brand_voice_analyzer.py landing-page.md
   python marketing-skill/content-creator/scripts/seo_optimizer.py landing-page.md "<campaign keyword>"
   ```

**Deliver:** Complete campaign kit — brief, channel plan, and all copy assets in one package.
