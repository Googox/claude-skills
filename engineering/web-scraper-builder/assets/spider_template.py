#!/usr/bin/env python3
"""
Starter Scrapling Spider template.

Copy this file, rename the class, set start_urls and selectors, then run:

    pip install scrapling
    pip install "scrapling[fetchers]"   # if any session uses a browser
    scrapling install                    # one-time browser download
    python spider_template.py

See engineering/web-scraper-builder/references/spider_framework_patterns.md
for multi-session routing, checkpoints, and concurrency tuning.
"""

from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession


class ExampleSpider(Spider):
    name = "example"
    start_urls = ["https://quotes.toscrape.com/"]

    # Start conservative; raise only after confirming the target tolerates it.
    concurrent_requests = 5

    def configure_sessions(self, manager):
        # Cheap HTTP for listing pages; stealth browser only when needed.
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for item in response.css(".quote"):
            yield {
                "text": item.css(".text::text").get(),
                "author": item.css(".author::text").get(),
                "tags": item.css(".tag::text").getall(),
            }

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield Request(response.urljoin(next_page), callback=self.parse)


if __name__ == "__main__":
    # crawldir persists progress so a crash resumes instead of restarting.
    ExampleSpider(crawldir="./crawl_data").start()
