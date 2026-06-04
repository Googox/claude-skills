---
description: Pull live HubSpot campaign analytics and get cs-demand-gen-specialist recommendations on what to optimise
---

Route to **HubSpot MCP → cs-demand-gen-specialist**.

1. Ask the user for: campaign name or ID (if not in $ARGUMENTS). If unknown, search for it.

2. **Pull campaign performance data from HubSpot:**
   - Use `mcp__8f2d65aa-2677-4cb9-a737-0c262e56a201__get_campaign_analytics` with the campaign ID
   - Use `mcp__8f2d65aa-2677-4cb9-a737-0c262e56a201__get_campaign_asset_metrics` for asset-level breakdown (emails, landing pages, ads)
   - Use `mcp__8f2d65aa-2677-4cb9-a737-0c262e56a201__get_campaign_contacts_by_type` to see enrolled vs. converted contacts

3. **Enrich with CRM context:**
   - Use `mcp__8f2d65aa-2677-4cb9-a737-0c262e56a201__query_crm_data` to cross-reference deal pipeline impact if relevant

4. **Read the demand acquisition skill for analysis framework:**
   ```bash
   cat marketing-skill/marketing-demand-acquisition/SKILL.md
   ```

5. **Analyse and interpret** the data as cs-demand-gen-specialist:
   - Overall performance vs. KPIs (CTR, conversion rate, CPL, CPA)
   - Best and worst performing assets with reasons
   - Funnel drop-off points
   - Budget efficiency analysis

6. **Deliver** a campaign performance report with:
   - Executive summary (3-5 bullet points)
   - Top 3 optimisation actions ranked by impact
   - Assets to pause, scale, or A/B test
   - Recommended next steps for the campaign
