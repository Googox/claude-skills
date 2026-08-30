# Fetcher Selection Guide

Choosing the wrong fetcher tier is the most common source of wasted scraping time. Start cheap, escalate only when you observe a specific failure signal.

## Decision Tree

```
1. Fetch the URL with `Fetcher.get(url)` (plain HTTP + TLS impersonation).
   │
   ├─ 200 response, target data present in the raw HTML?
   │    └─ YES → done. Use `Fetcher` / `FetcherSession` for the whole scrape.
   │
   ├─ 200 response, but target data is missing from the raw HTML
   │  (only present after JS runs — check via "view source" vs rendered DOM)?
   │    └─ Escalate to `DynamicFetcher` (needs real rendering, not bot-blocked).
   │
   ├─ 403 / 503, CAPTCHA page, "checking your browser" interstitial,
   │  `cf-mitigated` header, or a JS challenge before content loads?
   │    └─ Escalate to `StealthyFetcher` (anti-bot bypass, Cloudflare Turnstile solving).
   │
   └─ Still blocked after StealthyFetcher, or requires real user interaction
      (login flow, infinite scroll, click-to-reveal)?
        └─ Use `DynamicFetcher` / `DynamicSession` with `headless=False` for debugging,
           then `headless=True` for production once the flow is confirmed working.
```

## Signals Cheat Sheet

| Signal | Meaning | Fetcher |
|---|---|---|
| Data visible in `curl`/raw HTML | Static or server-rendered page | `Fetcher` |
| Data only in `<script>` JSON blobs you can parse directly | Often still fine with `Fetcher` — parse the JSON, skip rendering entirely | `Fetcher` |
| Data appears only after JS executes, no bot-detection response codes | Client-side rendered (SPA/hydration) | `DynamicFetcher` |
| HTTP 403/429, CAPTCHA, Cloudflare/Turnstile challenge page | Bot mitigation active | `StealthyFetcher` |
| Requires clicking, scrolling, form submission, or session/cookie state built up through interaction | Needs a real browser session | `DynamicFetcher` / `DynamicSession` |

## Tier 1 — `Fetcher` / `FetcherSession`

Plain HTTP requests with TLS fingerprint impersonation (`impersonate='chrome'`). Fastest, cheapest, least detectable because it doesn't run a browser at all — no headless-browser fingerprint to leak.

```python
from scrapling.fetchers import Fetcher, FetcherSession

page = Fetcher.get('https://quotes.toscrape.com/')

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
```

Use for: APIs, static sites, server-rendered pages, most listing/detail pages that don't gate on JS execution.

## Tier 2 — `StealthyFetcher` / `StealthySession`

Real browser fingerprint with anti-detection patches and automatic Cloudflare Turnstile solving. Slower than Tier 1 but far cheaper than full `DynamicFetcher` for sites that only need to pass a bot check, not execute application logic.

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
```

Use for: sites behind Cloudflare/Turnstile/similar bot mitigation where you don't need to interact with the page beyond loading it.

## Tier 3 — `DynamicFetcher` / `DynamicSession`

Full Playwright/Chromium automation. Slowest and most resource-intensive; use only when the page genuinely requires JS execution, interaction, or complex session state.

```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

page = DynamicFetcher.fetch('https://quotes.toscrape.com/')

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
```

Key options:
- `network_idle=True` — wait until network activity settles before returning the page (JS-heavy sites)
- `disable_resources=True` — skip loading images/fonts/CSS for faster scraping when only text data is needed
- `load_dom=False` — skip full DOM construction when you only need the raw response

Use for: SPAs, infinite scroll, login-gated flows, anything requiring clicks/typing before data appears.

## Async & Concurrency

All three tiers have async equivalents (`AsyncFetcher`, `AsyncStealthySession`, `AsyncDynamicSession`) for concurrent scraping:

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_all(urls):
    async with AsyncStealthySession(max_pages=2) as session:
        tasks = [session.fetch(url) for url in urls]
        return await asyncio.gather(*tasks)
```

Cap concurrency (`max_pages`, `concurrent_requests` on `Spider`) to stay under target-site rate limits — see `anti_detection_and_ethics.md`.
