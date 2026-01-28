# INKEY List Scraping Guide

This document explains how we collect product URLs from The INKEY List and how we scrape product data into the pipe-delimited dataset.

## Libraries and why
- requests: fast HTTP client with session headers for consistent fingerprinting.
- urllib3 Retry (via requests adapters): backoff and retry on transient 5xx responses.
- beautifulsoup4 + lxml parser: resilient HTML parsing and CSS selection for link discovery and content extraction.
- re: ingredient heuristics using regex.
- time: lightweight crawl pacing to reduce 429s.

## URL discovery (inkey_all_urls.txt)
- Script: [crawl_inkey.py](crawl_inkey.py).
- Start page: https://uk.theinkeylist.com/products.
- Approach: issue a single GET with a desktop user agent, parse with BeautifulSoup, and collect anchors containing `/products/` using multiple selectors to hedge against markup changes (e.g., `.product-link`, `[data-product-url]`).
- Filtering: normalize with `urljoin`, exclude the collection root (`/products`), and de-duplicate via a set.
- Safety: logs counts per selector and keeps a fallback scan of all `<a>` tags for any `/products/` pattern.
- Output: sorted unique URLs written to `inkey_all_urls.txt` when running the script directly.

## Product scraping (products_inkey_all.txt)
- Entrypoint: CLI in [src/main.py](src/main.py) with site slug `inkeylist` and a URL list file.
- Scraper: [src/sites/inkeylist.py](src/sites/inkeylist.py) implements `InkeyListScraper`.
- HTTP layer: [src/core/client.py](src/core/client.py) sets UA headers and retries 5xx; handles 429 with exponential backoff (3.0s * 1.8^n) up to 12 attempts.
- Crawl pacing: 2.5s delay between product requests to avoid throttling.

### Parsing workflow
- Load HTML with BeautifulSoup (`lxml` parser).
- Primary data source: JSON assigned to `window.SwymProductInfo.product` in script tags; parse to extract barcode, title/name, vendor/brand, featured image, tags/type for category, and variants fallback for barcode.
- Description: prefer JSON description; otherwise use `og:description` or standard meta description, then strip HTML.
- Images: normalize protocol-relative or root-relative URLs to absolute `https://uk.theinkeylist.com`.
- Ingredients: `_extract_ingredients` searches for an INCI block starting with “Aqua (Water)” and cleans it; falls back to longest comma-separated chemical list; final fallback is a keyword scan for common actives.
- Fallback path: if JSON is missing, use Open Graph meta tags for name/description/image and default brand to The INKEY List.

### Data hygiene and output
- Writing: [src/core/writer.py](src/core/writer.py) emits pipe-delimited rows with header `barcode|product_name|description|ingredients|image|brand_name|category|concerns`.
- Deduplication: existing rows are read to avoid duplicates; blank products (missing name/brand/image) are skipped.
- Cleaning: shared helpers in [src/core/cleaning.py](src/core/cleaning.py) collapse whitespace, strip HTML, and replace pipe characters to keep delimiter safety.

## How to run
1) Generate URLs (optional if `inkey_all_urls.txt` already exists):
   - `PYTHONPATH=src python crawl_inkey.py`
2) Scrape products from the URL list:
   - `PYTHONPATH=src python -m main inkeylist inkey_all_urls.txt --output products_inkey_all.txt`

## Notes and caveats
- The site can rate-limit; keep the built-in 2.5s delay and leave retries enabled.
- If markup changes and `window.SwymProductInfo.product` disappears, extend the scraper to handle alternative JSON-LD or API endpoints before relying on meta-tag fallback data.
- Ingredients heuristics are best-effort; consider manual QA for edge cases or when new formulations appear.
