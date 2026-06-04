---
description: Plan and execute a product launch — strategy via cs-product-manager, content via cs-content-creator (sequential)
---

Route to **cs-product-manager → cs-content-creator** (sequential multi-agent).

**Phase 1 — Launch Strategy (cs-product-manager):**

1. Ask the user for: product/feature name, key differentiators, target segments, launch date, and success metrics (if not in $ARGUMENTS).
2. Read the product manager skill:
   ```bash
   cat product-team/product-manager-toolkit/SKILL.md
   ```
3. Produce the launch strategy:
   - Positioning statement (for whom / what / unlike / we provide / because)
   - Target segment priorities and messaging pillars per segment
   - Launch tiers (GA, early access, beta) and timeline
   - Success metrics (activation, adoption, retention targets)

**Phase 2 — Launch Content (cs-content-creator):**

4. Using positioning and messaging from Phase 1:
   ```bash
   cat marketing-skill/content-creator/references/content_frameworks.md
   ```
5. Create all launch assets:
   - Announcement blog post (SEO-optimized)
   - Product page copy update
   - Email announcement to existing users
   - Social media launch posts (LinkedIn, Twitter/X)
   - Internal release notes
6. Validate all assets:
   ```bash
   python marketing-skill/content-creator/scripts/brand_voice_analyzer.py announcement.md
   python marketing-skill/content-creator/scripts/seo_optimizer.py product-page.md "<feature keyword>"
   ```

**Deliver:** Complete launch kit — strategy brief + all copy assets ready to publish.
