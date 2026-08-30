#!/usr/bin/env python3
"""
Scrape Extract - one-shot CLI extraction using Scrapling's fetcher tiers.

Mirrors the built-in `scrapling extract` CLI but returns structured JSON so
results can be piped into other tooling. Requires the `scrapling` package:

    pip install scrapling
    pip install "scrapling[fetchers]"   # for stealthy/dynamic fetchers
    scrapling install                    # one-time browser download
"""

import argparse
import json
import sys


FETCHER_CHOICES = ("fetch", "stealthy", "dynamic")


def load_fetcher(name: str):
    try:
        if name == "fetch":
            from scrapling.fetchers import Fetcher
            return Fetcher
        if name == "stealthy":
            from scrapling.fetchers import StealthyFetcher
            return StealthyFetcher
        if name == "dynamic":
            from scrapling.fetchers import DynamicFetcher
            return DynamicFetcher
    except ImportError as e:
        print(
            "Scrapling is not installed or missing an optional dependency.\n"
            "Install with:\n"
            "  pip install scrapling\n"
            "  pip install \"scrapling[fetchers]\"\n"
            "  scrapling install\n"
            f"\nOriginal error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
    raise ValueError(f"Unknown fetcher: {name}")


def fetch_page(fetcher_name: str, url: str, **kwargs):
    fetcher_cls = load_fetcher(fetcher_name)
    method = "get" if fetcher_name == "fetch" else "fetch"
    return getattr(fetcher_cls, method)(url, **kwargs)


def extract(page, css: list, xpath: list, adaptive: bool) -> dict:
    result = {"css": {}, "xpath": {}}
    for selector in css:
        matches = page.css(selector, adaptive=adaptive) if adaptive else page.css(selector)
        result["css"][selector] = matches.getall() if hasattr(matches, "getall") else matches
    for selector in xpath:
        matches = page.xpath(selector)
        result["xpath"][selector] = matches.getall() if hasattr(matches, "getall") else matches
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Fetch a URL with Scrapling and extract data via CSS/XPath selectors")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--css", action="append", default=[], help="CSS selector (repeatable)")
    parser.add_argument("--xpath", action="append", default=[], help="XPath selector (repeatable)")
    parser.add_argument("--fetcher", choices=FETCHER_CHOICES, default="fetch",
                         help="Fetcher tier: fetch (HTTP), stealthy (anti-bot), dynamic (browser)")
    parser.add_argument("--adaptive", action="store_true",
                         help="Use adaptive element relocation for CSS selectors")
    parser.add_argument("--headless", action="store_true", default=True,
                         help="Run stealthy/dynamic fetchers headless (default: true)")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    parser.add_argument("--output", help="Write output to file instead of stdout")
    args = parser.parse_args()

    if not args.css and not args.xpath:
        parser.error("Provide at least one --css or --xpath selector")

    fetch_kwargs = {}
    if args.fetcher in ("stealthy", "dynamic"):
        fetch_kwargs["headless"] = args.headless

    page = fetch_page(args.fetcher, args.url, **fetch_kwargs)
    data = extract(page, args.css, args.xpath, args.adaptive)

    if args.format == "json":
        output = json.dumps({"url": args.url, "fetcher": args.fetcher, "results": data}, indent=2)
    else:
        lines = [f"URL: {args.url}", f"Fetcher: {args.fetcher}"]
        for kind, selectors in data.items():
            for selector, values in selectors.items():
                lines.append(f"\n[{kind}] {selector}")
                for v in values:
                    lines.append(f"  {v}")
        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
