---
description: Write an SEO-optimized blog post with consistent brand voice using cs-content-creator
---

Route to **cs-content-creator** — Blog Post Creation workflow.

1. Ask the user for: topic, target keyword, target audience, desired tone, and approximate word count (if not provided in $ARGUMENTS).
2. Read the skill documentation:
   ```bash
   cat marketing-skill/content-creator/SKILL.md
   ```
3. Read the content frameworks reference:
   ```bash
   cat marketing-skill/content-creator/references/content_frameworks.md
   ```
4. Draft the blog post in markdown following the how-to or listicle framework as appropriate.
5. Analyze brand voice:
   ```bash
   python marketing-skill/content-creator/scripts/brand_voice_analyzer.py <draft-file>
   ```
6. Optimize for SEO:
   ```bash
   python marketing-skill/content-creator/scripts/seo_optimizer.py <draft-file> "<primary keyword>"
   ```
7. Revise based on both analyses and deliver the final post.

Target: SEO score 80+, brand voice within target range.
