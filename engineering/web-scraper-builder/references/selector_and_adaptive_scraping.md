# Selector Strategies and Adaptive Scraping

## CSS and XPath Basics

Scrapling's `Selector` (used transparently by every fetcher's returned page object) supports both CSS and XPath, plus a `::text`/`::attr()` extension syntax borrowed from Scrapy/parsel:

```python
page.css('.quote .text::text').getall()      # all matching text nodes
page.css('.quote .text::text').get()         # first match, or None
page.css('a::attr(href)').getall()           # attribute extraction
page.xpath('//div[@class="quote"]').getall() # XPath equivalent
```

`.get()` / `.getall()` never raise on no-match — always check for `None`/empty list rather than wrapping every call in try/except.

## Selector Robustness: What Breaks and Why

Ranked from most to least fragile:

1. **Auto-generated / hashed class names** — `css-1a2b3c`, `sc-bdVaJa`, `jsx-3ecfd2a1`. These regenerate on every build from CSS-in-JS tooling (styled-components, emotion, CSS modules). Never anchor a selector on them.
2. **Positional selectors** — `nth-child(3)`, `nth-of-type(2)`. Break the moment a sibling element is added/removed/reordered.
3. **Deep descendant chains** — `div > div > div:nth-child(2) > span`. Breaks on any intermediate markup change; also slow to evaluate.
4. **Presentational class names** — `.text-red`, `.mt-4`, `.flex`. Utility-CSS classes describe styling, not identity, and get reshuffled during redesigns.
5. **Semantic/stable attributes** — `id`, `data-testid`, `data-qa`, `aria-label`, `name`, `role`. These are the most stable because they're added deliberately for identification (often for the site's own test suite) and rarely change on redesign.

Preference order when multiple options exist: `data-testid`/`data-qa` > `id` > `aria-label`/`role` > semantic tag + stable class > positional.

Run `scripts/selector_robustness_checker.py` against a saved HTML snapshot to score a candidate selector and get concrete stable-attribute suggestions before shipping it.

## Adaptive Element Tracking

Scrapling's key differentiator: once an element is located, its structural/textual fingerprint can be saved and used to relocate it later even if the exact selector no longer matches (class renamed, wrapper `div` added, position shifted).

```python
# First run: locate normally and save a fingerprint for future relocation
products = page.css('.product-card', auto_save=True)

# Later runs (site may have redesigned since): relocate by similarity
# instead of failing when '.product-card' no longer matches anything
products = page.css('.product-card', adaptive=True)
```

Practical rules:
- Enable `auto_save=True` the first time you write a selector for a page you'll re-scrape regularly — retrofitting it later means re-locating every broken selector by hand anyway.
- `adaptive=True` degrades gracefully: if the fingerprinted element still exists (even under a new selector), it's found; if the element was genuinely removed, treat it as a real "not found" and alert rather than silently returning stale data.
- Adaptive matching is similarity-based, not magic — a complete redesign that removes the target content entirely will still fail. It protects against markup churn, not content removal.

## Finding Structurally Similar Elements

```python
first_product = page.css('.product-card').get()
similar = first_product.find_similar()  # other elements structurally similar to this one
```

Useful when a listing page's items don't share a clean common selector (e.g. mixed ad slots and real listings) — locate one confirmed real item, then find its siblings by structural similarity rather than guessing a selector that also matches ads.

## Extracting Structured Data Without Selectors

Many sites embed the data you want as JSON inside a `<script type="application/ld+json">` tag or a hydration payload (`__NEXT_DATA__`, `window.__INITIAL_STATE__`). Prefer parsing that JSON directly over scraping rendered HTML — it's faster, doesn't need a browser, and is immune to CSS/markup changes entirely:

```python
import json
raw = page.css('script#__NEXT_DATA__::text').get()
data = json.loads(raw) if raw else None
```

Always check for an embedded JSON payload before reaching for `DynamicFetcher` — it's the single most common way to avoid needing a browser at all.
