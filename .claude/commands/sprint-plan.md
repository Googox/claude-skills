---
description: Plan a sprint with user stories, acceptance criteria, and capacity allocation using cs-product-manager
---

Route to **cs-product-manager** — Sprint Planning workflow.

1. Ask the user for: sprint goal, team capacity (story points or days), candidate backlog items, and sprint duration (if not in $ARGUMENTS).
2. Read the product manager skill:
   ```bash
   cat product-team/product-manager-toolkit/SKILL.md
   ```
3. Prioritize backlog items for this sprint:
   - Apply effort/value scoring to candidates
   - Check against sprint capacity
   ```bash
   python product-team/product-manager-toolkit/scripts/rice_prioritizer.py backlog.csv --capacity <team-capacity>
   ```
4. Generate user stories for selected items:
   ```bash
   python product-team/product-manager-toolkit/scripts/user_story_generator.py "<feature>" "<user-type>"
   ```
5. Structure the sprint:
   - Sprint goal statement
   - Committed items with story points
   - Definition of Done checklist
   - Risks and dependencies flagged
6. Deliver: Sprint plan ready for team kickoff.
