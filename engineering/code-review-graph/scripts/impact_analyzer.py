#!/usr/bin/env python3
"""
Analyze the blast radius of code changes — find all repo files that import any changed file.
Supports Python, JavaScript/TypeScript, and Go.

Usage:
    python impact_analyzer.py [repo_path] [--base REF] [--head REF] [--json]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set


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
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        return []


_SOURCE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".go"}
_SKIP_DIRS = {"node_modules", "__pycache__", ".git", ".venv", "venv", "dist", "build", ".next"}


def iter_source_files(repo_path: str):
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS and not d.startswith(".")]
        for fname in files:
            if Path(fname).suffix.lower() in _SOURCE_EXTS:
                yield os.path.join(root, fname)


def extract_imports(file_path: str) -> List[str]:
    ext = Path(file_path).suffix.lower()
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return []

    if ext == ".py":
        results = []
        for m in re.finditer(
            r"^(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import)", content, re.MULTILINE
        ):
            mod = m.group(1) or m.group(2)
            if mod:
                results.append(mod.replace(".", "/"))
        return results

    if ext in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
        return re.findall(r"""(?:import\s.*?from\s+|require\s*\(\s*)['"]([^'"]+)['"]""", content)

    if ext == ".go":
        results = []
        in_block = False
        for line in content.split("\n"):
            s = line.strip()
            if "import (" in s:
                in_block = True
                continue
            if in_block:
                if s == ")":
                    in_block = False
                    continue
                m = re.match(r'"([^"]+)"', s)
                if m:
                    results.append(m.group(1))
            else:
                m = re.match(r'^import\s+"([^"]+)"', s)
                if m:
                    results.append(m.group(1))
        return results

    return []


def resolve_relative(import_str: str, source_file: str) -> Optional[str]:
    if not import_str.startswith("."):
        return None
    base = (Path(source_file).parent / import_str).resolve()
    candidates = [
        base,
        base.with_suffix(".py"),
        base.with_suffix(".ts"),
        base.with_suffix(".js"),
        base / "index.ts",
        base / "index.js",
        base / "__init__.py",
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def compute_impact(repo_path: str, changed_files: List[str]) -> Dict:
    abs_repo = os.path.abspath(repo_path)
    changed_abs = {os.path.abspath(os.path.join(abs_repo, f)) for f in changed_files}

    direct_dependents: Dict[str, List[str]] = {}

    for src_file in iter_source_files(abs_repo):
        src_abs = os.path.abspath(src_file)
        if src_abs in changed_abs:
            continue
        for imp in extract_imports(src_file):
            resolved = resolve_relative(imp, src_file)
            if resolved:
                resolved_abs = os.path.abspath(resolved)
                if resolved_abs in changed_abs:
                    changed_rel = os.path.relpath(resolved_abs, abs_repo)
                    dep_rel = os.path.relpath(src_abs, abs_repo)
                    direct_dependents.setdefault(changed_rel, [])
                    if dep_rel not in direct_dependents[changed_rel]:
                        direct_dependents[changed_rel].append(dep_rel)

    total_affected = sum(len(v) for v in direct_dependents.values())

    if total_affected == 0:
        risk_label, risk_score = "LOW", 1
    elif total_affected <= 5:
        risk_label, risk_score = "MEDIUM", 4
    elif total_affected <= 15:
        risk_label, risk_score = "HIGH", 7
    else:
        risk_label, risk_score = "CRITICAL", 10

    return {
        "changed_files": changed_files,
        "changed_count": len(changed_files),
        "direct_dependents": {k: sorted(v) for k, v in direct_dependents.items()},
        "total_affected_files": total_affected,
        "risk_score": risk_score,
        "risk_label": risk_label,
    }


def format_report(data: Dict) -> str:
    lines = [
        "Impact Analysis Report",
        "=" * 40,
        f"Changed files   : {data['changed_count']}",
        f"Affected files  : {data['total_affected_files']}",
        f"Risk level      : {data['risk_label']} ({data['risk_score']}/10)",
        "",
    ]
    if data["direct_dependents"]:
        lines.append("Files with dependents in repo:")
        for changed, deps in sorted(data["direct_dependents"].items()):
            lines.append(f"\n  CHANGED: {changed}")
            for dep in sorted(deps):
                lines.append(f"    <-- {dep}")
    else:
        lines.append("No external dependents found — low blast radius.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze change impact radius in a git repository"
    )
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to git repository")
    parser.add_argument("--base", default="HEAD~1", help="Base git ref")
    parser.add_argument("--head", default="HEAD", help="Head git ref")
    parser.add_argument("--json", action="store_true", dest="json_flag", help="Output JSON")
    args = parser.parse_args()

    changed = get_changed_files(args.repo_path, args.base, args.head)
    if not changed:
        print("No changed files.", file=sys.stderr)
        sys.exit(0)

    result = compute_impact(args.repo_path, changed)

    if args.json_flag:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
