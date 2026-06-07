#!/usr/bin/env python3
"""
Suggest code reviewers per changed file using CODEOWNERS (preferred) or git blame fallback.

Usage:
    python review_router.py [repo_path] [--base REF] [--head REF] [--exclude email ...] [--json]
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple


def get_changed_files(repo_path: str, base: str, head: str) -> List[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base}..{head}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        return []


def load_codeowners(repo_path: str) -> List[Tuple[str, List[str]]]:
    candidates = [
        os.path.join(repo_path, "CODEOWNERS"),
        os.path.join(repo_path, ".github", "CODEOWNERS"),
        os.path.join(repo_path, "docs", "CODEOWNERS"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            rules = []
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        rules.append((parts[0], parts[1:]))
            return list(reversed(rules))  # last rule wins
    return []


def match_codeowner(file_path: str, rules: List[Tuple[str, List[str]]]) -> List[str]:
    for pattern, owners in rules:
        p = pattern.lstrip("/")
        if (
            fnmatch.fnmatch(file_path, p)
            or fnmatch.fnmatch(file_path, f"**/{p}")
            or (not p.endswith("*") and fnmatch.fnmatch(file_path, f"{p}*"))
        ):
            return owners
    return []


def git_blame_authors(repo_path: str, file_path: str, top_n: int = 3) -> List[str]:
    try:
        result = subprocess.run(
            ["git", "log", "--follow", "--format=%ae", "-n", "20", "--", file_path],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        emails = [e.strip() for e in result.stdout.strip().split("\n") if e.strip()]
        if not emails:
            return []
        counter = Counter(emails)
        return [email for email, _ in counter.most_common(top_n)]
    except subprocess.CalledProcessError:
        return []


def route_reviewers(
    repo_path: str,
    changed_files: List[str],
    exclude: Optional[List[str]] = None,
) -> Dict:
    rules = load_codeowners(repo_path)
    has_codeowners = bool(rules)
    excluded = set(exclude or [])

    file_routing: Dict[str, Dict] = {}
    reviewer_files: Dict[str, List[str]] = defaultdict(list)

    for file_path in changed_files:
        owners: List[str] = []
        source = "git-blame"

        if has_codeowners:
            owners = match_codeowner(file_path, rules)
            if owners:
                source = "CODEOWNERS"

        if not owners:
            owners = git_blame_authors(repo_path, file_path)

        owners = [o for o in owners if o not in excluded]
        file_routing[file_path] = {"reviewers": owners, "source": source}

        for owner in owners[:1]:  # assign primary reviewer
            reviewer_files[owner].append(file_path)

    return {
        "has_codeowners": has_codeowners,
        "file_routing": file_routing,
        "reviewer_summary": dict(reviewer_files),
        "changed_files": changed_files,
    }


def format_report(data: Dict) -> str:
    lines = [
        "Reviewer Routing Report",
        "=" * 40,
        f"CODEOWNERS: {'found' if data['has_codeowners'] else 'not found (using git blame)'}",
        "",
    ]
    if data["reviewer_summary"]:
        lines.append("Suggested assignments:")
        for reviewer, files in sorted(data["reviewer_summary"].items()):
            lines.append(f"\n  {reviewer}")
            for f in sorted(files):
                lines.append(f"    • {f}")
    else:
        lines.append("No reviewers found — add a CODEOWNERS file for better routing.")

    lines.append("\nPer-file routing:")
    for file_path, info in sorted(data["file_routing"].items()):
        reviewers = ", ".join(info["reviewers"]) if info["reviewers"] else "(none)"
        lines.append(f"  {file_path}: {reviewers} [{info['source']}]")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Route code review to suggested reviewers"
    )
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to git repository")
    parser.add_argument("--base", default="HEAD~1", help="Base git ref")
    parser.add_argument("--head", default="HEAD", help="Head git ref")
    parser.add_argument("--exclude", nargs="+", help="Author emails to exclude (e.g., PR author)")
    parser.add_argument("--json", action="store_true", dest="json_flag", help="Output JSON")
    args = parser.parse_args()

    changed = get_changed_files(args.repo_path, args.base, args.head)
    if not changed:
        print("No changed files.", file=sys.stderr)
        sys.exit(0)

    result = route_reviewers(args.repo_path, changed, args.exclude)

    if args.json_flag:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
