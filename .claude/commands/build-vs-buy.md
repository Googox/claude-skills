---
description: Evaluate a build vs buy (or make vs partner) decision with aligned CEO + CTO perspectives using parallel consultation
---

Route to **cs-ceo-advisor + cs-cto-advisor** (parallel multi-agent consultation).

1. Ask the user to describe: what capability is being evaluated, current alternatives, budget range, timeline, and strategic context (if not in $ARGUMENTS).

**CEO Perspective (cs-ceo-advisor):**
2. Read CEO advisor skill:
   ```bash
   cat c-level-advisor/ceo-advisor/SKILL.md
   ```
3. Evaluate from business lens:
   - Strategic differentiation: Is this a core competency or commodity?
   - Market timing: Does building create competitive advantage?
   - Financial impact: TCO build vs buy over 3 years
   - Investor/board optics
   - Risk if vendor fails or product pivots

**CTO Perspective (cs-cto-advisor):**
4. Read CTO advisor skill:
   ```bash
   cat c-level-advisor/cto-advisor/SKILL.md
   ```
5. Evaluate from technical lens:
   - Technical feasibility and team capability
   - Integration complexity and maintenance burden
   - Build timeline and resource requirements
   - Technical risk (lock-in, scalability, security)
   - Existing alternatives (open source, API, SaaS)

**Synthesis:**
6. Combine both perspectives into a unified decision brief:
   - Clear recommendation (Build / Buy / Partner / Hybrid)
   - Supporting evidence from both business and technical angles
   - Implementation next steps
   - Decision criteria for revisiting (if conditions change)

Deliver: One-page decision brief aligned across CEO and CTO perspectives.
