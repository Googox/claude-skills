# Spider Framework Patterns

Scrapling's `Spider` class provides a Scrapy-like crawl framework: concurrent requests, multi-session routing, pause/resume checkpoints, and robots.txt compliance, without needing the full Scrapy project structure.

## Minimal Spider

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

QuotesSpider().start()
```

`parse` can `yield` either plain dicts (collected as scraped items) or `Request` objects (to follow links / paginate):

```python
async def parse(self, response: Response):
    for quote in response.css('.quote'):
        yield {"text": quote.css('.text::text').get()}

    next_page = response.css('li.next a::attr(href)').get()
    if next_page:
        yield Request(response.urljoin(next_page), callback=self.parse)
```

## Pause/Resume via Checkpoints

Pass `crawldir` to persist crawl progress to disk. If the process crashes or is stopped, restarting with the same `crawldir` resumes from the last checkpoint instead of re-crawling from scratch:

```python
QuotesSpider(crawldir="./crawl_data").start()
```

Use this for any crawl expected to run more than a few minutes — cheap insurance against losing hours of progress to a transient network error.

## Multi-Session Routing

Route different request types through different fetcher sessions — e.g. cheap HTTP for listing pages, stealth browser only for detail pages that sit behind Cloudflare:

```python
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://example.com/catalog"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a.product-link::attr(href)').getall():
            # detail pages need stealth; listing pages didn't
            yield Request(response.urljoin(link), callback=self.parse_product, session="stealth")

    async def parse_product(self, response: Response):
        yield {"title": response.css('h1::text').get()}
```

`lazy=True` defers starting the stealth session until it's actually needed, avoiding the cost of launching a browser for crawls that never hit a gated page.

## Concurrency Tuning

- `concurrent_requests` controls how many requests are in flight at once — start conservatively (5-10) and raise only after confirming the target tolerates it (see `anti_detection_and_ethics.md`).
- Prefer per-session concurrency caps (`max_pages` on async browser sessions) separately from `concurrent_requests`, since browser-backed requests are far more expensive than plain HTTP ones.

## Item Export

Items yielded as plain dicts can be piped to standard output formats without extra pipeline code — collect them in `parse` and write with the standard library:

```python
import json

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            item = {"text": quote.css('.text::text').get()}
            with open("output.jsonl", "a") as f:
                f.write(json.dumps(item) + "\n")
            yield item
```

For larger crawls, prefer batching writes rather than opening/appending per item.

## robots.txt Compliance

`Spider` respects `robots.txt` by default. Only disable this for sites you own or have explicit written authorization to scrape regardless of the file's directives — treat disabling it as a deliberate, documented exception, not a default.
