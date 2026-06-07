# Graph Analysis Patterns

Reference guide for interpreting and acting on code-review-graph output.

---

## Reading the Dependency Graph

The graph builder produces a **directed graph** where an edge `A → B` means file A imports file B. Both A and B are in the current diff.

### Key Patterns

#### Fan-Out Node (Hub)
```
utils/logger.py  -->  auth/login.py
utils/logger.py  -->  api/handler.py
utils/logger.py  -->  db/queries.py
```
A file with many outgoing edges is a shared utility changed in this PR. Every file that imports it is a review dependency — verify the change is backward-compatible.

#### Fan-In Node (Sink)
```
auth/login.py   -->  models/user.py
api/handler.py  -->  models/user.py
db/queries.py   -->  models/user.py
```
A file with many incoming edges is a core model/interface. Changes here risk breaking all importers. Require senior review and regression tests.

#### Chain
```
A.py --> B.py --> C.py
```
Changes to C may have been triggered by A. Review in chain order: C first (lowest level), then B, then A. Check that the interface contract is preserved at each link.

#### Isolated Files
Files with no edges to other changed files can be reviewed independently. Safe to parallelize.

---

## Risk Thresholds

| `total_edges` in graph | Interpretation | Action |
|------------------------|----------------|--------|
| 0 | No coupling between changed files | Low coordination risk |
| 1–3 | Minimal coupling | Note dependencies in review |
| 4–8 | Moderate coupling | Review dependency order explicitly |
| 9+ | High coupling | Consider splitting PR; require architect sign-off |

---

## Impact Radius Tiers

The impact analyzer classifies blast radius using affected file count:

| Risk Label | Affected Files | Recommended Action |
|------------|----------------|--------------------|
| LOW | 0 | Standard review process |
| MEDIUM | 1–5 | Add impacted file owners as reviewers |
| HIGH | 6–15 | Require senior + impacted team review; add regression tests |
| CRITICAL | 16+ | Mandatory architecture review; staged rollout recommended |

---

## Common Anti-Patterns

### Circular Imports
If the graph contains a cycle (A → B → A), the code has a circular dependency. This is a bug independent of the review — flag it.

Detection: if `graph_builder.py --json` shows A in B's deps and B in A's deps.

### God File Change
One file has 5+ edges pointing to it AND is changed in this PR. Any change to it is high-risk. Require explicit test coverage for each dependent path.

### Cross-Domain Coupling
A file in `auth/` imports from `payments/` which imports from `auth/`. Graph reveals this — flag for architectural debt and route to both team owners.

---

## Graphviz Rendering Tips

```bash
# Left-to-right layout (clearest for dependency chains)
dot -Tpng -Grankdir=LR review.dot -o graph.png

# Highlight changed files in a different color
# Edit the .dot file to add fillcolor=lightblue for changed nodes

# SVG for embedding in PRs (scalable, small file)
dot -Tsvg review.dot -o graph.svg
```

---

## Integration with Other Skills

- **pr-review-expert**: Run after graph analysis — use impact radius to set review depth
- **tech-debt-tracker**: High edge count in the graph = architectural debt signal
- **observability-designer**: CRITICAL blast radius changes need feature flags + monitoring
