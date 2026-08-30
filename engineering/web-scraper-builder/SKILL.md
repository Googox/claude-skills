# Web Scraper Builder

**Tier:** POWERFUL
**Category:** Engineering
**Domain:** Data Extraction / Web Scraping

---

## Overview

Design and build resilient, production-grade web scrapers in Python using **[Scrapling](https://github.com/D4Vinci/Scrapling)** as the primary fetching/parsing engine, with BeautifulSoup/Scrapy/Playwright covered as fallback options. Scrapling combines a fast HTML parser, three tiers of fetchers (plain HTTP, anti-bot stealth, full browser), and "adaptive" element tracking that auto-relocates selectors after a site's markup changes — the single biggest source of scraper maintenance cost.

This skill covers choosing the right fetcher for a target site, writing selectors that survive redesigns, respecting legal/ethical scraping boundaries, and scaling from a one-off script to a full crawl with Scrapling's Spider framework.

## Core Capabilities

- **Fetcher selection** — match site defenses (static HTML, JS-rendered, Cloudflare/Turnstile) to the cheapest fetcher that works
- **Adaptive selectors** — `adaptive=True` / `auto_save=True` element relocation so selectors survive markup drift
- **Selector robustness analysis** — score CSS/XPath selectors for fragility and suggest stable alternatives (`scripts/selector_robustness_checker.py`)
- **Scraper scaffolding** — generate a ready-to-run Scrapling script or Spider project (`scripts/spider_scaffolder.py`)
- **CLI extraction** — one-shot scraping via `scrape_extract.py`, mirroring `scrapling extract`
- **Anti-bot & ethics guardrails** — robots.txt, rate limiting, ToS considerations, stealth vs. abuse boundary

---

## When to Use

- Building a new scraper for a site with unknown or changing markup
- A brittle BeautifulSoup/Scrapy scraper keeps breaking on selector changes
- A target site returns 403s, CAPTCHAs, or Cloudflare challenges to plain `requests`
- Scaling a single-page script into a multi-page/multi-domain crawl
- Deciding whether a target needs a full browser or can be scraped over plain HTTP (cost/speed tradeoff)

---

## Architecture: Three Fetcher Tiers

Scrapling exposes three fetchers of increasing cost/capability. Always start at the cheapest tier that works — browser automation is 10-50x slower and easier to fingerprint than it looks.

| Tier | Class | Use when | Cost |
|------|-------|----------|------|
| 1 | `Fetcher` | Static HTML, no JS rendering needed, basic bot checks | Fastest — plain HTTP + TLS/impersonation |
| 2 | `StealthyFetcher` | Cloudflare/Turnstile challenges, headless-detection scripts, no real interaction needed | Medium — real browser fingerprint, challenge solving |
| 3 | `DynamicFetcher` | Site requires JS execution, clicks/scrolls, SPA hydration | Slowest — full Playwright/Chromium |

```python
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher

# Tier 1 — plain HTTP with TLS fingerprint impersonation
page = Fetcher.get('https://quotes.toscrape.com/')

# Tier 2 — anti-bot bypass (Cloudflare Turnstile, headless detection)
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')

# Tier 3 — full browser automation
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
```

See `references/fetcher_selection_guide.md` for the full decision tree and detection signals.

### Session variants (persistent connections, cookies, concurrency)

```python
from scrapling.fetchers import FetcherSession, StealthySession, DynamicSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
```

Async equivalents (`AsyncFetcher`, `AsyncStealthySession`, `AsyncDynamicSession`) support concurrent scraping via `asyncio.gather`.

---

## Selecting Elements: CSS, XPath, and Adaptive Relocation

```python
# CSS / XPath, same as BeautifulSoup/lxml
quotes = page.css('.quote .text::text').getall()
data = page.xpath('//div[@class="quote"]').getall()

# Adaptive tracking: save the element's fingerprint on first extraction,
# then relocate it by similarity even if the selector or DOM position changes
products = page.css('.product', auto_save=True)   # first run — save fingerprint
products = page.css('.product', adaptive=True)     # later runs — relocate if markup drifted

# Find elements structurally similar to one you already located
similar = page.find_similar()
```

Use `scripts/selector_robustness_checker.py` before committing to a selector — it flags auto-generated/hashed class names, deep nth-child chains, and other fragile patterns, and surfaces stable attributes (`id`, `data-testid`, `aria-*`, `name`) present on the same element. See `references/selector_and_adaptive_scraping.md` for the full pattern catalog.

---

## Scaling to a Crawl: The Spider Framework

For multi-page/multi-domain crawls, use Scrapling's Scrapy-like `Spider` class instead of hand-rolled loops:

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {"text": quote.css('.text::text').get()}

QuotesSpider(crawldir="./crawl_data").start()  # crawldir enables pause/resume checkpoints
```

Multi-session spiders can route different request types through different fetchers (fast HTTP for listing pages, stealth browser for detail pages behind Cloudflare):

```python
def configure_sessions(self, manager):
    manager.add("fast", FetcherSession(impersonate="chrome"))
    manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)
```

Scaffold a new spider project with `scripts/spider_scaffolder.py` (see Workflows below). Full patterns in `references/spider_framework_patterns.md`.

---

## Workflows

### 1. One-off extraction from a single URL

```bash
python scripts/scrape_extract.py 'https://quotes.toscrape.com/' \
  --css '.quote .text::text' --fetcher fetch --format json
```

Mirrors the built-in CLI (`scrapling extract get URL output.md --css-selector '#id'`) but returns structured JSON for downstream tooling instead of writing a file.

### 2. Validate a selector before writing scraper code

```bash
python scripts/selector_robustness_checker.py page_snapshot.html \
  --selector '.product-card > div:nth-child(3) > span.css-1a2b3c'
```

Returns a fragility score, the reasons for it, and any stable attributes found on matched elements that should be used instead.

### 3. Scaffold a new scraper or Spider project

```bash
python scripts/spider_scaffolder.py my_scraper \
  --start-url 'https://example.com/' --mode spider
```

Generates `my_scraper/spider.py`, `requirements.txt`, and a config file ready to run with `python spider.py`.

### 4. Decide which fetcher tier a target needs

Walk `references/fetcher_selection_guide.md`'s decision tree using observed signals (response codes, `cf-mitigated` headers, presence of a JS challenge, whether content appears in the raw HTML response).

---

## Installation

```bash
pip install scrapling
pip install "scrapling[fetchers]"   # adds browser-based fetcher dependencies
scrapling install                   # downloads browser binaries (one-time)
```

Docker: `docker pull pyd4vinci/scrapling`

`scripts/scrape_extract.py` and `scripts/spider_scaffolder.py` require the `scrapling` package; `scripts/selector_robustness_checker.py` uses only the Python standard library and runs without it.

---

## Comparison to Alternatives

| Aspect | Scrapling | BeautifulSoup | Scrapy | Playwright |
|--------|-----------|---------------|--------|-----------|
| Parser speed | ~2ms / 5000 elements | ~1584ms | similar to bs4 | N/A |
| Built-in fetching | Yes (HTTP + browser) | No — bring your own | Yes | Browser only |
| Anti-bot bypass | Cloudflare Turnstile solving | No | No | Manual setup |
| Adaptive element relocation | Yes | No | No | No |
| Full crawl framework | Yes (`Spider`) | No | Yes | No |

Reach for plain `requests` + BeautifulSoup only for trivial, static, one-shot scrapes where adding a dependency isn't worth it. Reach for Scrapy directly only if you're already deep in its ecosystem (middlewares, item pipelines). Otherwise Scrapling's `Fetcher`/`StealthyFetcher`/`DynamicFetcher` tiers cover the same ground as Playwright plus adaptive selectors.

---

## Best Practices

1. **Start at the cheapest fetcher tier** — try `Fetcher` first; escalate to `StealthyFetcher`/`DynamicFetcher` only when the site actually requires it
2. **Use `auto_save`/`adaptive` from day one** — retrofitting adaptive tracking after a scraper breaks costs more than enabling it upfront
3. **Prefer stable attributes over position** — `id`, `data-testid`, `aria-label`, `name` over `nth-child`/auto-generated class names
4. **Rate-limit and respect `robots.txt`** — the Spider framework has built-in robots.txt compliance; don't disable it without a documented reason
5. **Persist crawl state** — use `crawldir` checkpoints on long crawls so a crash doesn't restart from zero
6. **Never scrape auth-walled or ToS-prohibited content** without explicit authorization — see `references/anti_detection_and_ethics.md`

## Common Pitfalls

- **Defaulting to `DynamicFetcher` for everything** — most sites don't need a full browser; this wastes time and increases detection surface
- **Selectors anchored to auto-generated CSS-in-JS class names** (e.g. `css-1x2y3z`, `sc-bdVaJa`) — these change on every deploy
- **Ignoring `network_idle`/`load_dom` options** on JS-heavy pages, causing scrapes to run before content renders
- **No backoff/rate limiting** — aggressive concurrency gets IPs blocked and can constitute abuse
- **Treating a Cloudflare challenge as a green light to hammer the site** — stealth capability is for legitimate access, not for evading rate limits at scale

---

## Reference Library

- `references/fetcher_selection_guide.md` — decision tree for choosing Fetcher vs. StealthyFetcher vs. DynamicFetcher
- `references/selector_and_adaptive_scraping.md` — CSS/XPath patterns, adaptive relocation, `find_similar`
- `references/anti_detection_and_ethics.md` — stealth techniques, legal/ethical boundaries, rate limiting
- `references/spider_framework_patterns.md` — Spider class, multi-session routing, checkpoints, concurrency

## Assets

- `assets/spider_template.py` — starter Spider project template
- `assets/sample_scraping_config.json` — example scraper configuration

## Expected Outputs

- `expected_outputs/sample_extract_output.json` — sample JSON output from `scrape_extract.py`
