# Obsidian Skills - Claude Code Guidance

This guide covers the Obsidian skills for authoring notes, databases, canvases, and vault automation.

**Source:** Vendored from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) (MIT). Conform to the Agent Skills specification.

## Obsidian Skills Overview

**Available Skills:**
1. **obsidian-markdown/** — Create/edit Obsidian Flavored Markdown: wikilinks, embeds, callouts, properties, comments (3 reference guides: CALLOUTS, EMBEDS, PROPERTIES)
2. **obsidian-bases/** — Create/edit Obsidian Bases (`.base`): views, filters, formulas, summaries (1 reference: FUNCTIONS_REFERENCE)
3. **json-canvas/** — Create/edit JSON Canvas (`.canvas`): nodes, edges, groups, connections — mind maps, flowcharts (1 reference: EXAMPLES)
4. **obsidian-cli/** — Interact with a running Obsidian vault via the `obsidian` CLI: read, create, search, manage notes/tasks/properties; plugin & theme development (reload, run JS, capture errors, screenshots, inspect DOM)
5. **defuddle/** — Extract clean markdown from web pages via the Defuddle CLI, removing clutter/navigation to save tokens (use instead of WebFetch for standard web pages; not for `.md` URLs)

**Total:** 5 skills, 5 reference knowledge bases. No Python tools — these skills rely on external CLIs (`obsidian`, `defuddle`) and structured-file authoring.

## Skill Structure

Each skill is a self-contained package following the repo pattern:

```
obsidian/
├── .claude-plugin/plugin.json    # Plugin manifest (obsidian-skills)
├── obsidian-markdown/
│   ├── SKILL.md
│   └── references/               # CALLOUTS.md, EMBEDS.md, PROPERTIES.md
├── obsidian-bases/
│   ├── SKILL.md
│   └── references/FUNCTIONS_REFERENCE.md
├── json-canvas/
│   ├── SKILL.md
│   └── references/EXAMPLES.md
├── obsidian-cli/SKILL.md
└── defuddle/SKILL.md
```

## External Dependencies

Unlike most skills in this library (standard-library Python only), two Obsidian skills wrap external CLIs:

| Skill | Requires | Install |
|-------|----------|---------|
| **obsidian-cli** | `obsidian` CLI + a running Obsidian instance | See the [obsidian-cli](https://github.com/kepano/obsidian-cli) project |
| **defuddle** | `defuddle` CLI (Node) | `npm install -g defuddle-cli` |

The three authoring skills (**obsidian-markdown**, **obsidian-bases**, **json-canvas**) have no runtime dependencies — they document file formats and are applied by reading/writing the relevant files directly.

## When to Use

- Working with `.md` files inside an Obsidian vault (wikilinks, callouts, frontmatter, tags, embeds) → **obsidian-markdown**
- Building database-like table/card views over notes → **obsidian-bases**
- Creating visual canvases, mind maps, or flowcharts (`.canvas`) → **json-canvas**
- Automating vault operations or developing/debugging Obsidian plugins & themes → **obsidian-cli**
- Reading/analyzing a web page URL with minimal token cost → **defuddle**

## Maintenance

These skills are vendored copies. To refresh from upstream, re-run `npx skills add https://github.com/kepano/obsidian-skills` and reconcile any changes into `obsidian/` (keep the domain-folder layout; the CLI's `.agents/`/`.claude/skills` install artifacts are not tracked here).
