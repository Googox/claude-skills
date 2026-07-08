# Reviewer Routing Guide

Best practices for CODEOWNERS setup and git-blame-based reviewer routing.

---

## CODEOWNERS File Format

CODEOWNERS files follow GitHub's syntax. Place in one of:
- `/CODEOWNERS`
- `/.github/CODEOWNERS`
- `/docs/CODEOWNERS`

```
# Format: <pattern>  <owner1> [owner2 ...]

# Catch-all fallback — owns everything not matched below
*                       @team-lead

# Directory ownership
/src/auth/              @security-team
/src/payments/          @payments-team @compliance
/src/api/               @backend-team

# File type ownership
*.go                    @go-guild
*.sql                   @dba-team

# Specific critical files
/src/config/secrets.py  @security-team @cto
/src/models/user.py     @backend-team @security-team
```

**Rules:**
- Last matching rule wins (file is processed bottom-up)
- Owners can be GitHub usernames (`@username`), teams (`@org/team`), or emails
- Patterns follow `.gitignore` glob syntax

---

## Routing Strategy Tiers

### Tier 1: CODEOWNERS-Based (Preferred)
Explicit, auditable, version-controlled. Use for teams of 5+.

**Setup time:** 30–60 minutes  
**Maintenance:** Update when team structure changes  
**Accuracy:** High — ownership is intentional

### Tier 2: Git Blame / Log (Fallback)
Automatic but noisy — frequent contributors aren't always the right reviewer.

**When useful:** New repos, small teams, rapid prototyping  
**Limitation:** Doesn't know about knowledge domains; last author ≠ best reviewer

### Tier 3: Manual Override
Always allow PR author to override routing when:
- Expert is unavailable (use `--exclude`)
- Change crosses multiple domains with no single clear owner
- New team member needs onboarding review (pair with tech lead)

---

## Ownership Anti-Patterns

### Too Many Owners
```
# Bad: 8 owners means nobody feels responsible
/src/core/  @alice @bob @carol @dave @eve @frank @grace @heidi
```
Fix: assign 1–2 primary + 1 backup, not the entire team.

### Single Point of Failure
```
# Bad: one person owns all critical paths
/src/auth/        @alice
/src/payments/    @alice
/src/api/         @alice
```
Fix: distribute ownership; Alice is a bottleneck and vacation risk.

### Stale CODEOWNERS
Owners who left the team still listed — PRs get assigned to inactive accounts.
Fix: quarterly CODEOWNERS audit; remove leavers within 1 sprint.

---

## Excluding the PR Author

Always pass `--exclude <author-email>` to avoid self-review assignments:

```bash
# Get PR author email from git
PR_AUTHOR=$(git log -1 --format="%ae" HEAD)

python scripts/review_router.py . \
  --base main --head HEAD \
  --exclude "$PR_AUTHOR"
```

In GitHub Actions:
```yaml
- name: Route reviewers
  run: |
    PR_AUTHOR="${{ github.event.pull_request.user.login }}@users.noreply.github.com"
    python engineering/code-review-graph/scripts/review_router.py . \
      --base ${{ github.base_ref }} --head HEAD \
      --exclude "$PR_AUTHOR" --json
```

---

## Interpreting JSON Output

```json
{
  "has_codeowners": true,
  "reviewer_summary": {
    "@security-team": ["src/auth/login.py", "src/auth/token.py"],
    "@backend-team": ["src/api/handler.py"]
  },
  "file_routing": {
    "src/auth/login.py": {
      "reviewers": ["@security-team"],
      "source": "CODEOWNERS"
    }
  }
}
```

- `source: "CODEOWNERS"` — explicit owner match; high confidence
- `source: "git-blame"` — inferred from authorship; lower confidence
- Empty `reviewers` — file has no history and no CODEOWNERS entry; assign tech lead

---

## Sample CODEOWNERS for Common Stacks

### Full-Stack Web App
```
*                       @fullstack-team
/src/frontend/          @frontend-team
/src/backend/           @backend-team
/src/backend/auth/      @security-team
/src/backend/payments/  @payments-team
/migrations/            @dba-team
/.github/               @devops-team
/Dockerfile             @devops-team
```

### Microservices Monorepo
```
*                           @platform-team
/services/auth-service/     @identity-team
/services/payment-service/  @billing-team
/services/notification/     @comms-team
/libs/shared-proto/         @platform-team @all-backend
/infra/                     @sre-team
```
