#!/usr/bin/env python3
"""
Build a dependency graph from git diff to help reviewers understand change impact.
Supports Python, JavaScript/TypeScript, and Go.

Usage:
    python graph_builder.py [repo_path] [--base REF] [--head REF] [--format ascii|dot|json]
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
        print(f"Error getting git diff: {e}", file=sys.stderr)
        return []


def _parse_python_imports(content: str) -> List[str]:
    imports = []
    pattern = re.compile(
        r"^(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import)",
        re.MULTILINE,
    )
    for m in pattern.finditer(content):
        mod = m.group(1) or m.group(2)
        if mod:
            imports.append(mod.replace(".", "/"))
    return imports


def _parse_js_imports(content: str) -> List[str]:
    imports = []
    pattern = re.compile(r"""(?:import\s.*?from\s+|require\s*\(\s*)['"]([^'"]+)['"]""")
    for m in pattern.finditer(content):
        imports.append(m.group(1))
    return imports


def _parse_go_imports(content: str) -> List[str]:
    imports = []
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
                imports.append(m.group(1))
        else:
            m = re.match(r'^import\s+"([^"]+)"', s)
            if m:
                imports.append(m.group(1))
    return imports


def parse_imports(file_path: str) -> List[str]:
    ext = Path(file_path).suffix.lower()
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return []

    if ext == ".py":
        return _parse_python_imports(content)
    if ext in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
        return _parse_js_imports(content)
    if ext == ".go":
        return _parse_go_imports(content)
    return []


def resolve_import(import_path: str, source_file: str, all_repo_files: Set[str]) -> Optional[str]:
    if not import_path.startswith("."):
        return None
    source_dir = Path(source_file).parent
    base = (source_dir / import_path).resolve()
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
        if str(c) in all_repo_files:
            return str(c)
    return None


def build_graph(repo_path: str, changed_files: List[str]) -> Dict[str, Set[str]]:
    abs_repo = os.path.abspath(repo_path)
    changed_abs = {os.path.normpath(os.path.join(abs_repo, f)) for f in changed_files}

    all_repo_files: Set[str] = set()
    skip = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
    for root, dirs, files in os.walk(abs_repo):
        dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".")]
        for fname in files:
            all_repo_files.add(os.path.normpath(os.path.join(root, fname)))

    graph: Dict[str, Set[str]] = {f: set() for f in changed_abs}

    for src in changed_abs:
        if not os.path.isfile(src):
            continue
        for imp in parse_imports(src):
            resolved = resolve_import(imp, src, all_repo_files)
            if resolved:
                resolved = os.path.normpath(resolved)
                if resolved in changed_abs and resolved != src:
                    graph[src].add(resolved)

    def rel(p: str) -> str:
        try:
            return os.path.relpath(p, abs_repo)
        except ValueError:
            return p

    return {rel(k): {rel(v) for v in vs} for k, vs in graph.items()}


def to_ascii(graph: Dict[str, Set[str]]) -> str:
    lines = ["Code Review Dependency Graph", "=" * 40]
    has_edges = {k for k, vs in graph.items() if vs}
    all_nodes = set(graph.keys())
    isolated = all_nodes - has_edges - {v for vs in graph.values() for v in vs}

    lines.append(f"\nChanged files : {len(all_nodes)}")

    if has_edges:
        lines.append("\nDependency edges (A -> B means A imports B):")
        for src in sorted(has_edges):
            lines.append(f"\n  {src}")
            for dst in sorted(graph[src]):
                lines.append(f"    └─> {dst}")

    if isolated:
        lines.append("\nIsolated files (no internal deps):")
        for f in sorted(isolated):
            lines.append(f"  • {f}")

    return "\n".join(lines)


def to_dot(graph: Dict[str, Set[str]]) -> str:
    lines = [
        "digraph code_review_graph {",
        "  rankdir=LR;",
        "  node [shape=box, style=filled, fillcolor=lightyellow];",
    ]
    all_nodes = set(graph.keys()) | {v for vs in graph.values() for v in vs}
    for node in sorted(all_nodes):
        lines.append(f'  "{node}";')
    for src, dsts in sorted(graph.items()):
        for dst in sorted(dsts):
            lines.append(f'  "{src}" -> "{dst}";')
    lines.append("}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Build a dependency graph from git diff for code review"
    )
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to git repository")
    parser.add_argument("--base", default="HEAD~1", help="Base git ref (default: HEAD~1)")
    parser.add_argument("--head", default="HEAD", help="Head git ref (default: HEAD)")
    parser.add_argument("--format", choices=["ascii", "dot", "json"], default="ascii")
    parser.add_argument("--json", action="store_true", dest="json_flag", help="Alias for --format json")
    args = parser.parse_args()

    if args.json_flag:
        args.format = "json"

    changed = get_changed_files(args.repo_path, args.base, args.head)
    if not changed:
        print("No changed files found.", file=sys.stderr)
        sys.exit(0)

    graph = build_graph(args.repo_path, changed)

    if args.format == "json":
        print(json.dumps({
            "base": args.base,
            "head": args.head,
            "changed_files": changed,
            "graph": {k: sorted(v) for k, v in graph.items()},
            "stats": {
                "total_changed": len(changed),
                "files_with_internal_deps": sum(1 for v in graph.values() if v),
                "total_edges": sum(len(v) for v in graph.values()),
            },
        }, indent=2))
    elif args.format == "dot":
        print(to_dot(graph))
    else:
        print(to_ascii(graph))


if __name__ == "__main__":
    main()
