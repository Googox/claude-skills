# Code Review Graph Report

**PR / MR:** <!-- #PR_NUMBER or link -->  
**Branch:** <!-- feature/branch-name -->  
**Base:** <!-- main / develop -->  
**Date:** <!-- YYYY-MM-DD -->  
**Reviewer(s):** <!-- @reviewer1 @reviewer2 -->

---

## Impact Summary

| Metric | Value |
|--------|-------|
| Changed files | <!-- N --> |
| Internal dependency edges | <!-- N --> |
| Affected files (blast radius) | <!-- N --> |
| Risk level | <!-- LOW / MEDIUM / HIGH / CRITICAL --> |

---

## Dependency Graph

<!-- Paste ASCII output from graph_builder.py or embed graph image -->

```
# Run: python engineering/code-review-graph/scripts/graph_builder.py . --base main
```

---

## Impact Radius

<!-- Paste text output from impact_analyzer.py or list affected files -->

```
# Run: python engineering/code-review-graph/scripts/impact_analyzer.py . --base main
```

**Files potentially affected:**
- <!-- list files or "None" -->

---

## Reviewer Assignments

<!-- Paste output from review_router.py -->

```
# Run: python engineering/code-review-graph/scripts/review_router.py . --base main
```

| File | Suggested Reviewer | Source |
|------|--------------------|--------|
| <!-- path --> | <!-- @reviewer --> | <!-- CODEOWNERS / git-blame --> |

---

## Review Checklist

Adjust depth based on risk level:

### For all PRs
- [ ] Changed files make sense together (single concern)
- [ ] Tests added/updated for changed logic
- [ ] No secrets or credentials in diff

### For MEDIUM risk (1–5 affected files)
- [ ] Affected file owners notified as reviewers
- [ ] No breaking changes to shared interfaces
- [ ] Regression risk documented in PR description

### For HIGH risk (6–15 affected files)
- [ ] Senior engineer signed off on approach
- [ ] Impacted teams reviewed their sections
- [ ] Integration test covers main affected paths
- [ ] Rollback plan documented

### For CRITICAL risk (16+ affected files)
- [ ] Architecture review completed
- [ ] Staged rollout plan in place
- [ ] Monitoring / alerting in place for affected paths
- [ ] Feature flag available for quick disable

---

## Notes

<!-- Reviewer observations, architectural concerns, follow-up items -->

---

*Generated with `engineering/code-review-graph` skill*
