# Cosmetic Product Scraper

Python scaffolding for extracting cosmetic product data from multiple e-commerce sites. It follows the provided schema and exports `products.txt` as pipe-delimited UTF-8 text.

## Contributors

- **[andetazeqiri](https://github.com/andetazeqiri)** - Repository Owner
- **[orgito1015](https://github.com/orgito1015)** - Collaborator

## Setup

### Requirements
- Python 3.11 or higher
- Internet connection for scraping

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/andetazeqiri/KungulScraper.git
   cd KungulScraper
   ```

2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Usage

### Basic Usage
1. Place product URLs (one per line) in `urls.txt`.
2. Run a scraper (example uses the Notino scraper):
   ```bash
   PYTHONPATH=src python -m main notino urls.txt --output products.txt
   ```

### Available Site Scrapers
Currently implemented and placeholder scrapers:
- `notino` - Notino (fully implemented with Selenium)
- `inkeylist` - The INKEY List (fully implemented)
- `sephora`, `sisley`, `korres`, `adaherbs`, `rossmann`, `caudalie`, `altanatura`, `dermedic`, `apivita`, `goodjuju`, `yesstyle`, `theordinary`, `versed` - (placeholders)

### Output Format
The scraper outputs data in pipe-delimited format:
```
barcode|product_name|description|ingredients|image|brand_name|category|concerns
```

## Known Limitations
- **Notino**: Uses Cloudflare bot protection. Scrapy-based approach gets blocked. Options:
  - Use browser automation (Selenium/Playwright) with stealth plugins
  - Use cloudscraper library to bypass Cloudflare
  - Manually solve the challenge and export cookies for session reuse
  - Find alternative data sources or product APIs

## Adding a Site

To add a new scraper for a website:

1. Create a new Python file in `src/sites/` (e.g., `newsite.py`)
2. Implement a subclass of `SiteScraper` from `src/sites/base.py`
3. Register it in the `SCRAPERS` dictionary inside `src/main.py`

### Scraping Strategy
- **Preferred**: Use API/JSON responses discovered via DevTools Network tab
- **Fallback**: HTML parsing with BeautifulSoup
- **Last Resort**: Selenium/Playwright for JavaScript-heavy pages

See `src/sites/inkeylist.py` for a complete implementation example.

## Data Hygiene Rules

The scraper follows strict data quality standards:
- Strip all HTML tags from text content
- Collapse whitespace (multiple spaces/newlines to single space)
- Replace pipe characters (`|`) with forward slash (`/`) to preserve delimiter integrity
- Ingredients and concerns must be JSON arrays (e.g., `["Water", "Glycerin"]`) or empty strings
- Leave missing fields empty rather than fabricating placeholder values

## Project Layout

```
KungulScraper/
├── src/
│   ├── core/              # Shared utilities
│   │   ├── client.py      # HTTP client with retries
│   │   ├── cleaning.py    # Data cleaning functions
│   │   ├── models.py      # Product data model
│   │   ├── validation.py  # Product validation logic
│   │   └── writer.py      # Output file writer
│   ├── sites/             # Site-specific scrapers
│   │   ├── base.py        # Base scraper class
│   │   ├── notino.py      # Notino scraper (fully implemented)
│   │   ├── inkeylist.py   # INKEY List scraper (fully implemented)
│   │   └── ...            # Other site scrapers
│   └── main.py            # CLI entrypoint
├── requirements.txt       # Python dependencies
├── urls.txt              # Input URLs (one per line)
├── products.txt          # Output file (generated)
└── README.md             # This file
```

## Next Steps

### Development Roadmap
- [ ] Build scrapers for each target domain using the base class
- [ ] Add retries/rate limits or Selenium/Playwright adapters for sites that block static requests
- [ ] Create a test set of 20–30 products to validate output format and ingredient fidelity
- [ ] Implement more robust error handling and logging
- [ ] Add unit tests for core functionality

### Contributing
Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available for educational purposes.
