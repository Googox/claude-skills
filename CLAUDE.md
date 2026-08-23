# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a **comprehensive skills library** for Claude AI — reusable, production-ready skill packages that bundle domain expertise, best practices, analysis tools, and strategic frameworks. The repository provides modular skills that teams can download and use directly in their workflows.

**Current Scope:** 88 production-ready skills across 9 domains with 5 production agents.

**Key Distinction**: This is NOT a traditional application. It's a library of skill packages meant to be extracted and deployed by users into their own Claude workflows. It supports Claude Code natively, and also integrates with OpenAI Codex and OpenClaw.

## Navigation Map

This repository uses **modular documentation**. For domain-specific guidance, see:

| Domain | CLAUDE.md Location | Skills | Focus |
|--------|-------------------|--------|-------|
| **Agent Development** | [agents/CLAUDE.md](agents/CLAUDE.md) | 5 agents | cs-* agent creation, YAML frontmatter, relative paths |
| **Engineering (Tools)** | [engineering/CLAUDE.md](engineering/CLAUDE.md) | 24 | Practical tools: CI/CD, MCP, RAG, observability, scaffolding |
| **Engineering Team** | [engineering-team/CLAUDE.md](engineering-team/CLAUDE.md) | 21 | Role-based: fullstack, backend, ML, devops, security |
| **Marketing Skills** | [marketing-skill/CLAUDE.md](marketing-skill/CLAUDE.md) | 7 | Content creation, SEO, demand gen, campaign analytics |
| **Product Team** | [product-team/CLAUDE.md](product-team/CLAUDE.md) | 8 | RICE, OKRs, user stories, UX research tools |
| **C-Level Advisory** | [c-level-advisor/CLAUDE.md](c-level-advisor/CLAUDE.md) | 2 | CEO/CTO strategic decision-making |
| **Project Management** | [project-management/CLAUDE.md](project-management/CLAUDE.md) | 6 | Atlassian MCP, Jira/Confluence integration |
| **RA/QM Compliance** | [ra-qm-team/CLAUDE.md](ra-qm-team/CLAUDE.md) | 12 | ISO 13485, MDR, FDA compliance workflows |
| **Business & Growth** | [business-growth/CLAUDE.md](business-growth/CLAUDE.md) | 4 | Customer success, sales engineering, revenue operations |
| **Finance** | [finance/CLAUDE.md](finance/CLAUDE.md) | 3 | Financial analysis, DCF valuation, budgeting, German self-employment taxes and net income |
| **Standards Library** | [standards/CLAUDE.md](standards/CLAUDE.md) | 5 docs | Communication, quality, git, security standards |
| **Templates** | [templates/CLAUDE.md](templates/CLAUDE.md) | — | Agent template system |

## Architecture Overview

### Repository Structure

```
claude-skills/
├── agents/                    # 5 cs-* prefixed production agents
│   ├── c-level/               #   cs-ceo-advisor, cs-cto-advisor
│   ├── marketing/             #   cs-content-creator, cs-demand-gen-specialist
│   └── product/               #   cs-product-manager
├── engineering/               # 24 practical engineering tool skills
├── engineering-team/          # 21 role-based engineering skills
├── marketing-skill/           # 7 marketing skills
├── product-team/              # 8 product skills
├── c-level-advisor/           # 2 C-level skills
├── project-management/        # 6 PM skills + Atlassian MCP
├── ra-qm-team/                # 12 RA/QM compliance skills
├── business-growth/           # 4 business & growth skills
├── finance/                   # 3 finance skills
├── standards/                 # 5 standards documents
├── templates/                 # agent-template.md for new agent creation
├── documentation/             # Implementation plans, sprints, delivery
│   ├── delivery/              #   sprint-11-05-2025/ (complete)
│   │   └── sprint-11-06-2025/ #   sprint-11-06-2025/ (in progress)
│   └── implementation/        #   refactoring plans, implementation guides
├── scripts/                   # Installation + utility scripts
│   ├── codex-install.sh       #   OpenAI Codex install
│   ├── codex-install.bat      #   Windows Codex install
│   ├── openclaw-install.sh    #   OpenClaw install
│   └── sync-codex-skills.py  #   Codex skills sync utility
├── .claude/                   # Claude Code configuration (slash commands)
├── .claude-plugin/            # Root marketplace manifest
├── .codex/                    # OpenAI Codex integration (skills-index.json)
└── .github/                   # CI/CD workflows (6 total)
```

### Skill Package Pattern

Each skill follows this structure:
```
skill-name/
├── SKILL.md              # Master documentation
├── scripts/              # Python CLI tools (no ML/LLM calls)
├── references/           # Expert knowledge bases
└── assets/               # User templates
```

**Design Philosophy**: Skills are self-contained packages. Each includes executable tools (Python scripts), knowledge bases (markdown references), and user-facing templates. Teams can extract a skill folder and use it immediately.

**Key Pattern**: Knowledge flows from `references/` → into `SKILL.md` workflows → executed via `scripts/` → applied using `assets/` templates.

### Plugin Architecture

Each domain has a `.claude-plugin/plugin.json` manifest enabling Claude Code plugin installation. The root `.claude-plugin/marketplace.json` aggregates all domains for marketplace discovery. The `.codex/skills-index.json` (27K) indexes all 87 skills for Codex integration.

## Skills Inventory

| Domain | Skills | Key Skills |
|--------|--------|------------|
| **engineering/** | 24 | agent-designer, rag-architect, mcp-server-builder, ci-cd-pipeline-builder, database-designer, dependency-auditor, observability-designer, performance-profiler, pr-review-expert, release-manager, runbook-generator, skill-tester, tech-debt-tracker… |
| **engineering-team/** | 21 | senior-fullstack, senior-backend, senior-frontend, senior-devops, senior-ml-engineer, senior-data-engineer, senior-secops, aws-solution-architect, code-reviewer, incident-commander, tdd-guide… |
| **ra-qm-team/** | 12 | quality-manager-iso13485, mdr-745-specialist, fda-consultant, gdpr-expert, capa-officer, risk-management-specialist, isms-audit-expert… |
| **marketing-skill/** | 7 | content-creator, marketing-strategy-pmm, campaign-analytics, social-media-analyzer, app-store-optimization, marketing-demand-acquisition, prompt-engineer-toolkit |
| **product-team/** | 8 | product-manager-toolkit, agile-product-owner, product-strategist, competitive-teardown, ux-researcher-designer, ui-design-system, landing-page-generator, saas-scaffolder |
| **project-management/** | 6 | jira-expert, confluence-expert, scrum-master, senior-pm, atlassian-admin, atlassian-templates |
| **business-growth/** | 4 | customer-success-manager, sales-engineer, revenue-operations, contract-and-proposal-writer |
| **c-level-advisor/** | 2 | ceo-advisor, cto-advisor |
| **finance/** | 3 | financial-analyst, steuerrechner-selbststaendigkeit, brutto-netto-selbststaendige |

## Agent Architecture

**5 Production Agents** (`agents/` directory):

| Agent | Domain | Skill Referenced |
|-------|--------|-----------------|
| cs-content-creator | Marketing | marketing-skill/content-creator |
| cs-demand-gen-specialist | Marketing | marketing-skill/marketing-demand-acquisition |
| cs-ceo-advisor | C-Level | c-level-advisor/ceo-advisor |
| cs-cto-advisor | C-Level | c-level-advisor/cto-advisor |
| cs-product-manager | Product | product-team/product-manager-toolkit |

**Agent conventions:**
- Filename: `cs-{name}.md` (cs- prefix required)
- Required YAML frontmatter: `name`, `description`, `skills`, `domain`, `model`, `tools`
- Relative paths use `../../` pattern from `agents/domain/` to root
- Minimum 3 documented workflows per agent
- See [agents/CLAUDE.md](agents/CLAUDE.md) for full spec and template

## Git Workflow

**Branch Strategy:** feature → main (PR required)

**Branch Protection Active:** Main branch requires PR approval. Direct pushes blocked.

### Quick Start

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# 2. Work and commit (conventional commits required)
feat(engineering): add new ci-cd-pipeline-builder skill
fix(agents): correct relative path in cs-product-manager
docs(standards): update git workflow standards

# 3. Push and create PR to main
git push -u origin feature/your-feature-name
# Create PR via GitHub
```

**Conventional commit scopes:** `agents`, `engineering`, `marketing`, `product`, `pm`, `ra-qm`, `business`, `finance`, `standards`, `docs`, `scripts`, `tools`

**Branch Protection Rules:**
- Main: Requires PR approval, no direct push
- Feature branches: Conventional commits enforced by CI

See [documentation/WORKFLOW.md](documentation/WORKFLOW.md) for complete workflow guide.
See [standards/git/git-workflow-standards.md](standards/git/git-workflow-standards.md) for commit standards.

## Development Environment

**No build system or test frameworks** — intentional design choice for portability.

**Python Scripts:**
- Standard library only (minimal external dependencies)
- CLI-first design for easy automation
- Support both JSON and human-readable output
- No ML/LLM calls (keeps skills portable and fast)
- Python 3.8+ compatible

**If adding dependencies:**
- Document all dependencies in SKILL.md
- Keep runnable with `pip install package` at most
- Prefer standard library implementations

**CI/CD Workflows** (`.github/workflows/`):
- `ci-quality-gate.yml` — quality checks on PRs
- `claude-code-review.yml` — automated code review
- `claude.yml` — Claude Code integration
- `pr-issue-auto-close.yml` — PR/issue automation
- `smart-sync.yml` — cross-platform sync
- `sync-codex-skills.yml` — Codex skill index sync

## Active Sprint

**Sprint:** sprint-11-06-2025 (CS- Orchestrator Framework)
**Status:** 🔄 IN PROGRESS — Day 1 only (sprint docs created, orchestrator not yet built)
**Goal:** Build production-ready orchestration system for the 5 existing cs-* agents

**Planned deliverables (incomplete):**
- cs-orchestrator agent with hybrid routing (rule-based + AI)
- 10+ task-based slash commands
- Multi-agent coordination patterns (sequential handoffs, parallel execution)
- 60%+ token savings via prompt caching
- Documentation: USER_GUIDE, ARCHITECTURE, TOKEN_OPTIMIZATION, TROUBLESHOOTING

**Previous Sprint:** sprint-11-05-2025 — ✅ COMPLETE
- Delivered 5 production agents, modular CLAUDE.md structure, branch protection

**Progress Tracking:**
- [sprint-11-06-2025 context](documentation/delivery/sprint-11-06-2025/context.md)
- [sprint-11-06-2025 progress](documentation/delivery/sprint-11-06-2025/PROGRESS.md)

## Roadmap

**Current state (88 skills, 5 agents):**
- Engineering (24+21=45), RA/QM (12), Product (8), Marketing (7), PM (6), Business (4), Finance (3), C-Level (2)
- 5 production agents orchestrating core domains

**Next Priorities:**
- **Phase 3 (Q2 2026):** CS- Orchestrator + remaining agents for engineering, PM, RA/QM domains
- **Phase 4 (Q3 2026):** Mobile, blockchain, web3, advanced analytics skills
- **Target:** 60+ skills baseline already exceeded; next milestone is full agent coverage

## Key Principles

1. **Skills are products** — Each skill deployable as standalone package
2. **Documentation-driven** — Success depends on clear, actionable docs
3. **Algorithm over AI** — Use deterministic analysis (code) vs LLM calls
4. **Template-heavy** — Provide ready-to-use templates users customize
5. **Platform-specific** — Specific best practices > generic advice
6. **Self-contained** — No inter-skill dependencies; each folder is portable

## Anti-Patterns to Avoid

- Creating dependencies between skills (keep each self-contained)
- Adding complex build systems or test frameworks (maintain simplicity)
- Generic advice in SKILL.md (focus on specific, actionable frameworks)
- LLM calls in Python scripts (defeats portability and speed)
- Hardcoding absolute paths in agent files (use `../../` relative paths)
- Duplicating skill content inside agent files (agents orchestrate, not replicate)

## Working with This Repository

**Creating New Skills:** Follow the target domain's CLAUDE.md guide (see Navigation Map). Use an existing SKILL.md as structural reference.

**Creating New Agents:** Use [templates/agent-template.md](templates/agent-template.md) and follow [agents/CLAUDE.md](agents/CLAUDE.md).

**Editing Existing Skills:** Maintain consistency across markdown files — same voice, formatting, and structure patterns.

**Quality Standard:** Each skill should save users 40%+ time while improving consistency/quality by 30%+.

## Additional Resources

- **.gitignore:** Excludes `.vscode/`, `.DS_Store`, `AGENTS.md`, `PROMPTS.md`, `.env*`
- **Standards Library:** [standards/](standards/) — communication, quality, git, documentation, security
- **Implementation Plans:** [documentation/implementation/](documentation/implementation/)
- **Sprint Delivery:** [documentation/delivery/](documentation/delivery/)
- **CHANGELOG:** [CHANGELOG.md](CHANGELOG.md) — version history
- **Installation Guide:** [INSTALLATION.md](INSTALLATION.md) — Claude Code, Codex, OpenClaw setup

---

**Last Updated:** June 2026
**Skills:** 88 production-ready across 9 domains
**Agents:** 5 production agents (cs-* prefixed)
**Active Sprint:** sprint-11-06-2025 (CS- Orchestrator Framework — in progress)
