import argparse
from pathlib import Path
from typing import List, Type

from core.client import HttpClient
from core.writer import write_products
from sites.base import SiteScraper
from sites.notino import NotinoScraper
from sites.sephora import SephoraScraper
from sites.sisley import SisleyScraper
from sites.korres import KorresScraper
from sites.adaherbs import AdaherbsScraper
from sites.rossmann import RossmannScraper
from sites.caudalie import CaudalieScraper
from sites.altanatura import AltanaturaScraper
from sites.dermedic import DermedicScraper
from sites.inkeylist import InkeyListScraper
from sites.apivita import ApivitaScraper
from sites.goodjuju import GoodJujuScraper
from sites.yesstyle import YesStyleScraper
from sites.theordinary import TheOrdinaryScraper
from sites.versed import VersedScraper


SCRAPERS: dict[str, Type[SiteScraper]] = {
    "notino": NotinoScraper,
    "sephora": SephoraScraper,
    "sisley": SisleyScraper,
    "korres": KorresScraper,
    "adaherbs": AdaherbsScraper,
    "rossmann": RossmannScraper,
    "caudalie": CaudalieScraper,
    "altanatura": AltanaturaScraper,
    "dermedic": DermedicScraper,
    "inkeylist": InkeyListScraper,
    "apivita": ApivitaScraper,
    "goodjuju": GoodJujuScraper,
    "yesstyle": YesStyleScraper,
    "theordinary": TheOrdinaryScraper,
    "versed": VersedScraper,
}


def load_urls(file_path: Path) -> List[str]:
    with file_path.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cosmetic product scraper")
    parser.add_argument("site", choices=SCRAPERS.keys(), help="Site slug to scrape")
    parser.add_argument("url_file", type=Path, help="Text file with one product URL per line")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("products.txt"),
        help="Output file (pipe-delimited)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    urls = load_urls(args.url_file)
    client = HttpClient()
    scraper_class = SCRAPERS[args.site]
    scraper = scraper_class(client)
    products = list(scraper.scrape_products(urls))
    write_products(args.output, products)
    print(f"Saved {len(products)} products to {args.output}")


if __name__ == "__main__":
    main()
