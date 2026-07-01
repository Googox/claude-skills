# Anti-Detection Techniques and Ethical Boundaries

Scrapling's stealth capabilities (TLS/browser fingerprint impersonation, Cloudflare Turnstile solving, headless-detection evasion) exist to let legitimate automated access work the same way a real browser would — not to defeat access controls a site owner has deliberately placed to keep automated traffic out entirely. Use this reference to stay on the right side of that line.

## Before Writing Any Scraper

1. **Check `robots.txt`** (`https://target-site.com/robots.txt`). Scrapling's `Spider` framework honors it by default — don't disable that without a documented, deliberate reason (e.g. scraping your own site).
2. **Check the site's Terms of Service** for explicit scraping prohibitions. A technical ability to bypass a block does not make it authorized.
3. **Prefer an official API** if one exists — it's more stable, faster, and unambiguously authorized.
4. **Identify what you actually need** — often a JSON payload embedded in the page (see `selector_and_adaptive_scraping.md`) avoids needing stealth/browser automation entirely.
5. **Get explicit authorization** before scraping login-gated content, paywalled content, or any data covered by an existing data-access agreement.

## Rate Limiting and Load

- Set `concurrent_requests` on `Spider` (or cap `max_pages` on async sessions) to a level the target site can absorb — start low (1-5) and increase only if you've confirmed it's not causing errors/slowdowns for the site.
- Add delays between requests to the same host; don't rely on stealth capability as a substitute for politeness.
- Cache responses locally during development so you're not re-fetching the same page repeatedly while iterating on selectors.
- Treat HTTP 429 responses as a hard signal to back off — implement exponential backoff, don't retry immediately.

## Fingerprinting and Stealth — What It's For

- **TLS/HTTP fingerprint impersonation** (`impersonate='chrome'`) — makes traffic look like a normal browser instead of a Python HTTP client, avoiding false-positive bot blocks common on CDNs/WAFs.
- **Headless detection evasion** — many sites block automation frameworks by detecting headless-browser tells (missing `navigator.webdriver` overrides, unusual plugin lists), not by detecting "is this a bot fetching my public page." Stealth mode closes that gap for legitimate access.
- **Cloudflare Turnstile solving** — handles a challenge that would otherwise block any automated client, including ones with entirely legitimate purposes (price monitoring, accessibility tooling, research with permission).

None of the above should be read as "any site's block can be bypassed" — sites that actively fight scraping at scale (aggressive rate limiting, IP bans, legal notices) are signaling they don't want automated access, and repeatedly working around that at volume crosses from "using a stealth fetcher" into abuse.

## Data Handling

- Don't store or republish personal data scraped from third-party sites without a lawful basis (GDPR/CCPA considerations apply to scraped PII exactly as they do to any other collection method).
- Attribute and respect copyright/licensing on scraped content if it will be redistributed or used for training/analysis beyond internal research.
- Discard scraped data you no longer need rather than accumulating indefinite archives "just in case."

## Red Flags That Mean Stop and Reassess

- The site's ToS explicitly prohibits automated access and there's no separate written authorization
- The target requires login credentials that aren't your own or a test account you were given for this purpose
- The scrape targets personal data at a scale that would require a privacy impact assessment
- You're being asked to defeat CAPTCHAs/paywalls specifically to access content the operator sells access to
- The request describes evading detection for a target where a competitor/business relationship makes intent obviously adversarial (e.g., scraping a competitor's pricing to undercut them in ways that violate the site's terms)

When any of these apply, ask the user for explicit confirmation of authorization before proceeding, or decline if authorization can't be confirmed.
