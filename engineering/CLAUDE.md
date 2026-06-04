# Engineering Skills — Developer Guide

This guide covers the **24 practical engineering tool skills** in the `engineering/` domain. These are tool-focused skills (CI/CD, database design, MCP servers, RAG, observability) distinct from the role-based skills in `engineering-team/`.

## Domain Overview

| Aspect | Detail |
|--------|--------|
| **Skills** | 24 production-ready tool skills |
| **Focus** | Practical engineering workflows and tooling |
| **Differs from** | `engineering-team/` — that domain covers engineering *roles* (senior-backend, senior-devops, etc.) |
| **Plugin** | `.claude-plugin/plugin.json` for Claude Code marketplace |

## Skills Index

| Skill | Purpose |
|-------|---------|
| agent-designer | Design Claude Code agent architectures |
| agent-workflow-designer | Multi-agent coordination and workflow patterns |
| api-design-reviewer | REST/GraphQL API review and best practices |
| api-test-suite-builder | Automated API test generation |
| changelog-generator | Automated changelog from git history |
| ci-cd-pipeline-builder | GitHub Actions, GitLab CI pipeline scaffolding |
| codebase-onboarding | New developer onboarding documentation |
| database-designer | Database schema and ER diagram design |
| database-schema-designer | Advanced schema design with migrations |
| dependency-auditor | Dependency vulnerability and update audit |
| env-secrets-manager | Environment variable and secrets management |
| git-worktree-manager | Git worktree workflows for parallel development |
| interview-system-designer | Technical interview system design |
| mcp-server-builder | Build custom MCP servers for Claude Code |
| migration-architect | Database and system migration planning |
| monorepo-navigator | Monorepo tooling (Nx, Turborepo, pnpm workspaces) |
| observability-designer | Logging, metrics, tracing architecture |
| performance-profiler | Application performance analysis and optimization |
| pr-review-expert | Structured pull request review workflows |
| rag-architect | Retrieval-Augmented Generation system design |
| release-manager | Release planning, versioning, deployment |
| runbook-generator | Operational runbook creation |
| skill-tester | Validate and test new skills |
| tech-debt-tracker | Technical debt identification and prioritization |

## Skill Package Structure

Each skill follows the standard pattern:
```
engineering/skill-name/
├── SKILL.md              # Workflows, usage, examples
├── scripts/              # Python CLI tools (standard library only)
├── references/           # Expert knowledge bases
└── assets/               # Templates and output examples
```

## Creating New Skills in This Domain

1. Pick a name that describes the **tool or task** (not the role)
2. Create the folder: `engineering/your-skill-name/`
3. Start from `../../templates/agent-template.md` as structural reference
4. Follow the skill package structure above
5. Commit with: `feat(engineering): add your-skill-name skill`

## Key Conventions

- **Python scripts:** standard library only, CLI-first, support `--json` flag
- **No LLM calls** in scripts — keeps skills portable and fast
- **Self-contained:** no imports from other skill folders
- **SKILL.md** must include: purpose, workflows (min. 3), examples, success metrics

## Relationship to Other Domains

- **`engineering-team/`** — role-based skills (who you are: senior-backend, senior-devops)
- **`engineering/`** — tool-based skills (what you build: ci-cd-pipeline, mcp-server)
- **`agents/`** — future cs-engineering agents will orchestrate skills from both domains

## Additional Resources

- **Main Documentation:** `../CLAUDE.md`
- **Agent Development:** `../agents/CLAUDE.md`
- **Standards:** `../standards/CLAUDE.md`
- **Plugin Manifest:** `.claude-plugin/plugin.json`

---

**Last Updated:** June 2026
**Skills Deployed:** 24/24 engineering tool skills production-ready
**Focus:** Practical engineering workflows, tooling, and infrastructure design
