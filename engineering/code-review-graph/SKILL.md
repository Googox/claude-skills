# Code Review Graph

**Tier:** POWERFUL
**Category:** Engineering
**Domain:** Code Review / Developer Tooling

---

## Overview

Code review graph converts a pull request diff into a visualized dependency graph — mapping which changed files import each other, which repo files are impacted downstream, and which team members own each area. It compresses the mental model of a large PR into a navigable picture so reviewers spend time on logic, not on manually tracing dependencies.

This skill sits **before** structured review in the workflow. Use it first to understand blast radius and assign reviewers, then use `pr-review-expert` for checklist-based review and `engineering-team/code-reviewer` for code quality scoring.

---

## Core Capabilities

- **Dependency graph** — directed graph of import relationships among changed files, output as ASCII, DOT (Graphviz), or JSON
- **Impact radius** — full-repo scan to find files that depend on any changed file, with risk labeling (LOW → CRITICAL)
- **Reviewer routing** — CODEOWNERS-first matching with git-blame fallback; excludes PR author automatically
- **Multi-language** — Python, JavaScript, TypeScript, Go
- **CI-ready** — all scripts output `--json` for machine consumption; non-zero exit on CRITICAL risk

---

## When to Use

- PR touches shared utilities, core models, or central interfaces
- PR has more than 10 changed files and reviewers need a navigation map
- Assigning reviewers across team ownership boundaries
- Pre-merge blast radius check for risky changes
- Generating impact reports for architecture decisions or post-incident review

---

## Tools

### 1. Graph Builder (`scripts/graph_builder.py`)

Build a directed dependency graph among the files changed in a diff.

```bash
# ASCII output — current branch vs HEAD~1
python scripts/graph_builder.py /path/to/repo

# Compare named branches
python scripts/graph_builder.py /path/to/repo --base main --head feature/my-feature

# DOT format — pipe to Graphviz for PNG/SVG
python scripts/graph_builder.py /path/to/repo --format dot | dot -Tpng -o graph.png

# JSON output — for CI or further processing
python scripts/graph_builder.py /path/to/repo --json
```

**JSON output fields:**
- `changed_files` — list of files in the diff
- `graph` — adjacency list: `{ "src/a.py": ["src/b.py"] }`
- `stats.total_changed` — count of changed files
- `stats.files_with_internal_deps` — files that import another changed file
- `stats.total_edges` — total import relationships within the changed set

---

### 2. Impact Analyzer (`scripts/impact_analyzer.py`)

Scan the entire repo to find files that import any changed file (blast radius analysis).

```bash
# Text report — current branch
python scripts/impact_analyzer.py /path/to/repo

# Compare named branches
python scripts/impact_analyzer.py /path/to/repo --base main --head feature/my-feature

# JSON for CI integration
python scripts/impact_analyzer.py /path/to/repo --json
```

**Risk labels:**

| Affected files | Label    | Recommended action |
|---------------|----------|--------------------|
| 0             | LOW      | Standard review |
| 1–5           | MEDIUM   | Add affected file owners as reviewers |
| 6–15          | HIGH     | Senior review + regression tests |
| 16+           | CRITICAL | Architecture review + staged rollout |

**JSON output fields:**
- `changed_count`, `total_affected_files`, `risk_label`, `risk_score` (1/4/7/10)
- `direct_dependents` — map from changed file to list of files that import it

---

### 3. Review Router (`scripts/review_router.py`)

Suggest reviewers per file using CODEOWNERS (preferred) or git log authorship (fallback).

```bash
# Route reviewers for current diff
python scripts/review_router.py /path/to/repo

# Exclude the PR author by email
python scripts/review_router.py /path/to/repo --exclude author@company.com

# JSON output
python scripts/review_router.py /path/to/repo --json
```

CODEOWNERS is auto-detected from `/CODEOWNERS`, `/.github/CODEOWNERS`, or `/docs/CODEOWNERS`.

Sample CODEOWNERS:
```
/src/auth/        @security-team
/src/payments/    @payments-team @finance-lead
*.go              @go-guild
*                 @backend-team
```

---

## Workflows

### Workflow 1: Pre-Review Blast Radius Check

**Goal:** Understand change scope and risk before assigning or conducting a review.

**Steps:**
1. **Fetch branch** — `git fetch origin && git checkout feature/my-branch`
2. **Check impact** — run `impact_analyzer.py` to get risk label and affected file count
3. **Build graph** — run `graph_builder.py` to map internal dependencies
4. **Route reviewers** — run `review_router.py --exclude <pr-author-email>`
5. **Fill report template** — copy `assets/review-report-template.md` into PR description

**Expected Output:** Risk label, reviewer assignments, and dependency map for the PR

**Time Estimate:** 30–90 seconds

```bash
#!/bin/bash
REPO="."
BASE="main"
HEAD="HEAD"

echo "=== Impact Radius ==="
python scripts/impact_analyzer.py $REPO --base $BASE --head $HEAD

echo ""
echo "=== Dependency Graph ==="
python scripts/graph_builder.py $REPO --base $BASE --head $HEAD

echo ""
echo "=== Reviewer Routing ==="
python scripts/review_router.py $REPO --base $BASE --head $HEAD
```

---

### Workflow 2: Generate Graphviz Visualization

**Goal:** Produce a visual graph image for large PRs or architecture discussions.

**Steps:**
1. **Check Graphviz** — `dot -V` (install: `brew install graphviz` / `apt install graphviz`)
2. **Generate DOT** — `python scripts/graph_builder.py . --format dot > review.dot`
3. **Render** — `dot -Tpng review.dot -o review-graph.png`
4. **Attach** — upload `review-graph.png` to PR description or Slack thread

**Expected Output:** PNG or SVG dependency graph for the PR

**Time Estimate:** 1–2 minutes

```bash
python scripts/graph_builder.py . --base main --format dot \
  | dot -Tsvg -o /tmp/review-graph.svg
```

---

### Workflow 3: CI Gate — Block CRITICAL Blast Radius PRs

**Goal:** Automatically flag PRs with dangerous blast radius before they can be merged.

**Steps:**
1. **Add workflow file** to `.github/workflows/`
2. **Run impact_analyzer with `--json`**
3. **Parse `risk_label`** from JSON
4. **Exit non-zero** if CRITICAL; post warning comment if HIGH

**Expected Output:** CI check passes for LOW/MEDIUM, warns for HIGH, fails for CRITICAL

**Time Estimate:** 10 minutes to set up

```yaml
# .github/workflows/code-review-graph.yml
name: Code Review Graph
on: [pull_request]
jobs:
  blast-radius:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check blast radius
        run: |
          RESULT=$(python engineering/code-review-graph/scripts/impact_analyzer.py . \
            --base ${{ github.base_ref }} --head HEAD --json)
          RISK=$(echo "$RESULT" | python -c \
            "import json,sys; print(json.load(sys.stdin)['risk_label'])")
          echo "Blast radius: $RISK"
          if [ "$RISK" = "CRITICAL" ]; then
            echo "::error::CRITICAL blast radius — architecture review required"
            exit 1
          fi
          if [ "$RISK" = "HIGH" ]; then
            echo "::warning::HIGH blast radius — senior review required"
          fi
```

---

### Workflow 4: Weekly Coupling Trend Report

**Goal:** Track which modules accumulate coupling over time as a tech debt signal.

**Steps:**
1. **Loop over recent merges** — `git log --merges -20 main`
2. **Run graph_builder per merge** — capture `stats.total_edges`
3. **Spot rising trend** — increasing edges in a module = growing coupling
4. **Feed into tech-debt-tracker** — log high-coupling modules as architecture debt

**Expected Output:** Edge count per merge commit, trend visible over last 20 merges

**Time Estimate:** 2–5 minutes

```bash
#!/bin/bash
echo "Coupling trend (last 10 merges to main):"
git log --merges --format="%H %s" -10 main | while read HASH MSG; do
  EDGES=$(python scripts/graph_builder.py . \
    --base ${HASH}^ --head ${HASH} --json 2>/dev/null \
    | python -c "import json,sys; print(json.load(sys.stdin)['stats']['total_edges'])" 2>/dev/null \
    || echo 0)
  printf "  %3s edges — %s\n" "$EDGES" "$MSG"
done
```

---

## Integration Examples

### Example 1: Full Pre-Review Script

```bash
#!/bin/bash
# pre-review.sh — Run before starting any code review

REPO=${1:-.}
BASE=${2:-main}
HEAD=${3:-HEAD}
PR_AUTHOR=${4:-""}

echo "=============================="
echo "Code Review Graph — $(date +%Y-%m-%d)"
echo "=============================="

python engineering/code-review-graph/scripts/impact_analyzer.py "$REPO" \
  --base "$BASE" --head "$HEAD"

echo ""
python engineering/code-review-graph/scripts/graph_builder.py "$REPO" \
  --base "$BASE" --head "$HEAD"

echo ""
if [ -n "$PR_AUTHOR" ]; then
  python engineering/code-review-graph/scripts/review_router.py "$REPO" \
    --base "$BASE" --head "$HEAD" --exclude "$PR_AUTHOR"
else
  python engineering/code-review-graph/scripts/review_router.py "$REPO" \
    --base "$BASE" --head "$HEAD"
fi
```

### Example 2: JSON Pipeline for Slack Notification

```bash
#!/bin/bash
# Summarize blast radius and post to Slack

RESULT=$(python engineering/code-review-graph/scripts/impact_analyzer.py . --json)
RISK=$(echo "$RESULT" | python -c "import json,sys; d=json.load(sys.stdin); print(d['risk_label'])")
COUNT=$(echo "$RESULT" | python -c "import json,sys; d=json.load(sys.stdin); print(d['total_affected_files'])")

case "$RISK" in
  LOW)      EMOJI="✅" ;;
  MEDIUM)   EMOJI="⚠️" ;;
  HIGH)     EMOJI="🔴" ;;
  CRITICAL) EMOJI="🚨" ;;
esac

echo "$EMOJI PR blast radius: $RISK ($COUNT files affected)"
```

### Example 3: DOT Graph to Embedded SVG

```bash
#!/bin/bash
# Generate SVG and print embed snippet for PR description

python engineering/code-review-graph/scripts/graph_builder.py . \
  --base main --format dot | dot -Tsvg -o /tmp/review-graph.svg

echo "SVG graph saved to /tmp/review-graph.svg"
echo "Embed in PR description:"
echo '![Dependency Graph](review-graph.svg)'
```

---

## Success Metrics

**Review Efficiency:**
- Context-building time: from 20+ minutes to under 5 minutes for 10+ file PRs
- Missed dependencies: 0 surprise breakages from unreviewed affected files
- Reviewer routing accuracy: 80%+ correct match when CODEOWNERS is present

**Quality:**
- Blast radius awareness: 100% of HIGH/CRITICAL PRs flagged before merge
- Language coverage: Python, JS/TS, Go — accounts for 80%+ of typical repos
- CI overhead: under 30 seconds added per PR

**Team Adoption:**
- Time saved per large PR: 15–40 minutes
- Reviewer assignment automation: 70%+ of files when CODEOWNERS is configured

---

## Language Support

| Language | Patterns Detected |
|----------|-------------------|
| Python | `import X`, `from X import Y` |
| JavaScript | `import X from 'Y'`, `require('Y')` |
| TypeScript | `import X from 'Y'`, `import type X from 'Y'` |
| Go | `import "pkg/path"`, multi-import blocks |

**Planned:** Ruby (`require`), Java/Kotlin (`import`), Rust (`use`)

---

## Related Skills

- [`pr-review-expert`](../pr-review-expert/SKILL.md) — Structured checklist review after mapping the graph
- [`engineering-team/code-reviewer`](../../engineering-team/code-reviewer/SKILL.md) — Code quality scoring for changed files
- [`tech-debt-tracker`](../tech-debt-tracker/SKILL.md) — Use high coupling counts as tech debt signals
- [`observability-designer`](../observability-designer/SKILL.md) — Monitor runtime impact for CRITICAL blast radius changes

---

**Last Updated:** June 2026
**Sprint:** sprint-11-06-2025
**Status:** Production Ready
**Version:** 1.0
