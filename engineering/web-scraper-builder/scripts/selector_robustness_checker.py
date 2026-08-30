#!/usr/bin/env python3
"""
Selector Robustness Checker - score a CSS selector's fragility against a saved
HTML snapshot and suggest more stable alternatives.

Standard library only (html.parser) - no Scrapling/lxml dependency required,
so it can validate selectors before a scraper's real dependencies are installed.
"""

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from typing import Dict, List, Optional


STABLE_ATTRS = ("data-testid", "data-qa", "data-cy", "id", "aria-label", "name", "role")

# CSS-in-JS / build-tool generated class name patterns (styled-components,
# emotion, CSS modules, JSS, etc.) - these regenerate on every build.
HASHED_CLASS_PATTERNS = [
    re.compile(r"^css-[a-z0-9]{5,}$"),        # emotion
    re.compile(r"^sc-[A-Za-z0-9]{6,}$"),      # styled-components
    re.compile(r"^jsx-\d+$"),                  # styled-jsx
    re.compile(r"^[a-zA-Z]+-[a-f0-9]{6,}$"),   # generic hash suffix, e.g. Button-a1b2c3
    re.compile(r"^_[a-zA-Z0-9]{5,}_[a-z0-9]{5,}$"),  # CSS modules, e.g. _button_1a2b3
]

UTILITY_CLASS_PATTERN = re.compile(
    r"^(mt|mb|ml|mr|pt|pb|pl|pr|p|m|w|h|flex|grid|text|bg|border|rounded|gap|font)-"
)


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "index_in_parent")

    def __init__(self, tag: str, attrs: Dict[str, str], parent: Optional["Node"]):
        self.tag = tag
        self.attrs = attrs
        self.children: List["Node"] = []
        self.parent = parent
        self.index_in_parent = 0

    @property
    def classes(self) -> List[str]:
        return self.attrs.get("class", "").split()


class TreeBuilder(HTMLParser):
    """Builds a minimal DOM tree from raw HTML using only the stdlib parser."""

    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
                 "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        parent = self.stack[-1]
        node = Node(tag, dict(attrs), parent)
        node.index_in_parent = sum(1 for c in parent.children if c.tag == tag)
        parent.children.append(node)
        if tag not in self.VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        parent = self.stack[-1]
        node = Node(tag, dict(attrs), parent)
        node.index_in_parent = sum(1 for c in parent.children if c.tag == tag)
        parent.children.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break


def walk(node: Node):
    yield node
    for child in node.children:
        yield from walk(child)


SIMPLE_SELECTOR_RE = re.compile(
    r"^(?P<tag>[a-zA-Z0-9]*)"
    r"(?P<rest>(?:[.#][\w-]+|\[[^\]]+\]|:[\w-]+(?:\([^)]*\))?)*)$"
)
PART_RE = re.compile(r"[.#][\w-]+|\[[^\]]+\]|:[\w-]+(?:\([^)]*\))?")


def parse_simple_selector(simple: str) -> Dict:
    m = SIMPLE_SELECTOR_RE.match(simple.strip())
    if not m:
        return {"tag": None, "id": None, "classes": [], "attrs": [], "pseudos": []}
    tag = m.group("tag") or None
    parsed = {"tag": tag, "id": None, "classes": [], "attrs": [], "pseudos": []}
    for part in PART_RE.findall(m.group("rest") or ""):
        if part.startswith("#"):
            parsed["id"] = part[1:]
        elif part.startswith("."):
            parsed["classes"].append(part[1:])
        elif part.startswith("["):
            parsed["attrs"].append(part[1:-1])
        elif part.startswith(":"):
            parsed["pseudos"].append(part[1:])
    return parsed


def node_matches_simple(node: Node, parsed: Dict) -> bool:
    if parsed["tag"] and parsed["tag"] != "*" and node.tag != parsed["tag"]:
        return False
    if parsed["id"] and node.attrs.get("id") != parsed["id"]:
        return False
    node_classes = set(node.classes)
    if parsed["classes"] and not set(parsed["classes"]).issubset(node_classes):
        return False
    for attr_expr in parsed["attrs"]:
        if "=" in attr_expr:
            key, _, val = attr_expr.partition("=")
            val = val.strip("'\"")
            if node.attrs.get(key.strip()) != val:
                return False
        else:
            if attr_expr.strip() not in node.attrs:
                return False
    for pseudo in parsed["pseudos"]:
        name, _, arg = pseudo.partition("(")
        arg = arg.rstrip(")")
        if name in ("nth-child", "nth-of-type"):
            try:
                target = int(arg) - 1
            except ValueError:
                continue
            if node.index_in_parent != target:
                return False
    return True


def select(root: Node, selector: str) -> List[Node]:
    """Supports descendant (' ') and direct-child ('>') combinators of simple selectors."""
    tokens = [t for t in re.split(r"\s*(>)\s*|\s+", selector.strip()) if t]
    candidates = [root]
    combinator = None
    for token in tokens:
        if token == ">":
            combinator = ">"
            continue
        parsed = parse_simple_selector(token)
        next_candidates: List[Node] = []
        for c in candidates:
            pool = c.children if combinator == ">" else list(walk(c))[1:]
            next_candidates.extend(n for n in pool if node_matches_simple(n, parsed))
        candidates = next_candidates
        combinator = None
    return candidates


def score_selector(selector: str, matched: List[Node]) -> Dict:
    reasons = []
    score = 100

    parts = [p for p in re.split(r"\s*>\s*|\s+", selector.strip()) if p]
    if len(parts) > 4:
        score -= 15
        reasons.append(f"Deep selector chain ({len(parts)} combinators) - "
                        "breaks on any intermediate markup change")

    for part in parts:
        parsed = parse_simple_selector(part)
        for pseudo in parsed["pseudos"]:
            if pseudo.startswith("nth-child") or pseudo.startswith("nth-of-type"):
                score -= 25
                reasons.append(f"Positional pseudo-class ':{pseudo}' - "
                                "breaks if siblings are added/removed/reordered")
        for cls in parsed["classes"]:
            if any(p.match(cls) for p in HASHED_CLASS_PATTERNS):
                score -= 35
                reasons.append(f"Auto-generated/hashed class name '.{cls}' - "
                                "regenerates on every build from CSS-in-JS tooling")
            elif UTILITY_CLASS_PATTERN.match(cls):
                score -= 10
                reasons.append(f"Utility/presentational class '.{cls}' - "
                                "describes styling, not identity")

    stable_found = set()
    for node in matched:
        # Check the matched node itself, then walk up ancestors - a stable
        # attribute on a nearby ancestor is often enough to build a robust
        # selector even when the exact matched element has none of its own.
        current, depth = node, 0
        while current is not None and depth <= 3:
            for attr in STABLE_ATTRS:
                if attr in current.attrs:
                    prefix = "" if depth == 0 else f"(ancestor +{depth}) "
                    stable_found.add(f'{prefix}[{attr}="{current.attrs[attr]}"]')
            current = current.parent
            depth += 1

    score = max(0, min(100, score))
    if score >= 80:
        verdict = "robust"
    elif score >= 50:
        verdict = "moderate"
    else:
        verdict = "fragile"

    return {
        "selector": selector,
        "matched_count": len(matched),
        "fragility_score": score,
        "verdict": verdict,
        "reasons": reasons or ["No fragility patterns detected"],
        "suggested_stable_selectors": sorted(stable_found),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Score a CSS selector's fragility against an HTML snapshot")
    parser.add_argument("html_file", help="Path to a saved HTML snapshot")
    parser.add_argument("--selector", required=True, action="append", dest="selectors",
                         help="CSS selector to check (repeatable)")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    try:
        with open(args.html_file, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
    except OSError as e:
        print(f"Error reading {args.html_file}: {e}", file=sys.stderr)
        sys.exit(1)

    builder = TreeBuilder()
    builder.feed(html)

    results = []
    for selector in args.selectors:
        matched = select(builder.root, selector)
        results.append(score_selector(selector, matched))

    if args.format == "json":
        print(json.dumps(results, indent=2))
        return

    for r in results:
        print(f"\nSelector: {r['selector']}")
        print(f"  Matches: {r['matched_count']}")
        print(f"  Fragility score: {r['fragility_score']}/100 ({r['verdict']})")
        for reason in r["reasons"]:
            print(f"    - {reason}")
        if r["suggested_stable_selectors"]:
            print("  Stable alternatives found on matched elements:")
            for s in r["suggested_stable_selectors"]:
                print(f"    {s}")


if __name__ == "__main__":
    main()
