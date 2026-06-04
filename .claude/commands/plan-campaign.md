---
description: Plan a full marketing campaign end-to-end — strategy via cs-demand-gen-specialist, then copy via cs-content-creator
---

Route to **cs-demand-gen-specialist → cs-content-creator** (sequential multi-agent).

**Phase 1 — Campaign Strategy (cs-demand-gen-specialist):**

1. Ask the user for: campaign goal, target audience, budget range, timeline, and primary channel (if not in $ARGUMENTS).
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
