---
description: Build or review a product roadmap with RICE prioritization using cs-product-manager
---

Route to **cs-product-manager** — Roadmap Planning workflow.

1. Ask the user for: list of feature candidates (or backlog items), team capacity per sprint, and planning horizon (if not in $ARGUMENTS).
2. Read the product manager skill:
   ```bash
   cat product-team/product-manager-toolkit/SKILL.md
   ```
3. Apply RICE scoring to each feature candidate:
   - Reach, Impact, Confidence, Effort (1-10 scale)
   - RICE score = (Reach × Impact × Confidence) / Effort
   ```bash
   python product-team/product-manager-toolkit/scripts/rice_prioritizer.py features.csv --capacity 20
   ```
4. Build the roadmap:
   - Now / Next / Later buckets
   - OKR alignment for each initiative
   - Dependencies and risks flagged
5. Generate user stories for top 3 prioritized features:
   ```bash
   python product-team/product-manager-toolkit/scripts/user_story_generator.py "<feature-name>" "<user-type>"
   ```
6. Deliver: Prioritized roadmap with RICE scores, OKR mapping, and user stories.
