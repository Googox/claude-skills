---
description: Show available cs-* agents and slash commands, or route any task to the right specialist
---

Show the user what's available in this skills library and route their task.

1. Display the available agents and commands:

**Available CS-* Agents:**
| Agent | Domain | Best for |
|-------|--------|---------|
| cs-orchestrator | All | Any task — auto-routes to the right agent |
| cs-content-creator | Marketing | Blog posts, copy, SEO, brand voice |
| cs-demand-gen-specialist | Marketing | Campaigns, lead gen, demand strategy |
| cs-product-manager | Product | Roadmap, backlog, sprints, user stories |
| cs-ceo-advisor | C-Level | Strategy, board, investor prep, vision |
| cs-cto-advisor | C-Level | Architecture, tech stack, engineering team |

**Available Slash Commands:**
| Command | What it does |
|---------|-------------|
| `/write-blog` | Write an SEO-optimized blog post |
| `/plan-campaign` | Full campaign: strategy + all copy assets |
| `/demand-gen` | Demand generation strategy for any channel |
| `/product-roadmap` | RICE-prioritized roadmap with OKR mapping |
| `/sprint-plan` | Sprint planning with user stories |
| `/product-launch` | Launch strategy + all announcement content |
| `/ceo-brief` | CEO strategic advisory |
| `/cto-review` | CTO technical advisory |
| `/build-vs-buy` | CEO + CTO parallel decision analysis |
| `/skill-help` | This help screen |

2. If the user described a task in $ARGUMENTS, identify which command or agent best fits and offer to run it now.

3. For any task not covered by the commands above, read the routing rules and route directly:
   ```bash
   cat agents/orchestrator/routing-rules.yaml
   ```
