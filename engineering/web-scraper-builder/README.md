# Web Scraper Builder

Build resilient, production-grade web scrapers in Python using [Scrapling](https://github.com/D4Vinci/Scrapling) — a fast adaptive scraping framework with three fetcher tiers (HTTP, anti-bot stealth, full browser) and self-healing selectors that auto-relocate after a site's markup changes.

## What's in this skill

```
web-scraper-builder/
├── SKILL.md                          # Master documentation and workflows
├── scripts/
│   ├── selector_robustness_checker.py  # Score selector fragility (stdlib only)
│   ├── scrape_extract.py               # One-shot CLI extraction (needs scrapling)
│   └── spider_scaffolder.py            # Generate a scraper/Spider project (stdlib only)
├── references/
│   ├── fetcher_selection_guide.md      # Fetcher vs. StealthyFetcher vs. DynamicFetcher
│   ├── selector_and_adaptive_scraping.md
│   ├── anti_detection_and_ethics.md
│   └── spider_framework_patterns.md
├── assets/
│   ├── spider_template.py              # Starter Spider project
│   ├── sample_scraping_config.json     # Example config
│   └── sample_snapshot.html            # Sample HTML for the robustness checker
└── expected_outputs/
    ├── sample_extract_output.json
    └── sample_selector_report.txt
```

## Quick start

Validate a selector before writing scraper code (no dependencies needed):

```bash
python scripts/selector_robustness_checker.py assets/sample_snapshot.html \
  --selector '[data-testid="product-price"]'
```

Scaffold a new scraper project:

```bash
python scripts/spider_scaffolder.py my_scraper \
  --start-url 'https://quotes.toscrape.com/' --mode spider --item-selector '.quote'
```

One-shot extraction (requires `pip install scrapling`):

```bash
python scripts/scrape_extract.py 'https://quotes.toscrape.com/' \
  --css '.quote .text::text' --fetcher fetch --format json
```

## Installing Scrapling

```bash
pip install scrapling
pip install "scrapling[fetchers]"   # browser-based fetchers
scrapling install                    # download browser binaries (one-time)
```

`selector_robustness_checker.py` and `spider_scaffolder.py` use only the Python
standard library and run without Scrapling installed. `scrape_extract.py`
requires the `scrapling` package and fails with clear install instructions if
it is missing.

## Key ideas

- **Start at the cheapest fetcher tier.** Try `Fetcher` (plain HTTP) first;
  escalate to `StealthyFetcher` (anti-bot) or `DynamicFetcher` (browser) only
  when the target actually requires it. See `references/fetcher_selection_guide.md`.
- **Use adaptive selectors from day one.** `auto_save=True` on first extraction,
  `adaptive=True` afterward, so selectors relocate by similarity instead of
  breaking when the site changes its markup.
- **Prefer stable attributes.** `data-testid`, `id`, `aria-label` over
  positional (`nth-child`) or auto-generated (`css-1a2b3c`) selectors. The
  robustness checker scores this for you.
- **Scrape ethically.** Respect `robots.txt`, rate-limit, honor ToS. See
  `references/anti_detection_and_ethics.md`.

See [SKILL.md](SKILL.md) for full documentation.
