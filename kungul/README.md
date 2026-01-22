# Cosmetic Product Scraper

Python scaffolding for extracting cosmetic product data from multiple e-commerce sites. It follows the provided schema and exports `products.txt` as pipe-delimited UTF-8 text.

## Setup
- Python 3.11+
- Install dependencies: `python -m pip install -r requirements.txt`

## Usage
1) Place product URLs (one per line) in `urls.txt`.
2) Run a scraper (example uses the Notino heuristic scraper):
   - `PYTHONPATH=src python -m main notino urls.txt --output products.txt`
   - Available site slugs (placeholders unless implemented): notino, sephora, sisley, korres, adaherbs, rossmann, caudalie, altanatura, dermedic, inkeylist, apivita, goodjuju, yesstyle, theordinary, versed.
3) Output follows the schema:
   - `barcode|product_name|description|ingredients|image|brand_name|category|concerns`

## Known Limitations
- **Notino**: Uses Cloudflare bot protection. Scrapy-based approach gets blocked. Options:
  - Use browser automation (Selenium/Playwright) with stealth plugins
  - Use cloudscraper library to bypass Cloudflare
  - Manually solve the challenge and export cookies for session reuse
  - Find alternative data sources or product APIs

## Adding a site
- Implement a subclass of `SiteScraper` in `src/sites/`.
- Register it in `SCRAPERS` inside `src/main.py`.
- Prefer API/JSON responses discovered via DevTools Network tab; fall back to HTML parsing with BeautifulSoup; reserve Selenium/Playwright for JS-heavy pages.

## Data hygiene rules
- Strip HTML, collapse whitespace, replace `|` with `/` when needed.
- Ingredients and concerns must be JSON arrays (e.g., `["Water", "Glycerin"]`) or empty.
- Leave missing fields empty instead of fabricating values.

## Project layout
- `src/core/` - shared utilities (HTTP client, cleaning, models, writer)
- `src/sites/` - site-specific scrapers (Notino example included)
- `src/main.py` - CLI entrypoint
- `products.txt` - pipe-delimited output (generated)

## Next steps
- Build scrapers for each target domain using the base class.
- Add retries/rate limits or Selenium/Playwright adapters if a site blocks static requests.
- Create a test set of 20–30 products and validate output format and ingredient fidelity.
