from typing import Iterable
from core.models import Product
from core.client import HttpClient
from .base import SiteScraper


class VersedScraper(SiteScraper):
    def __init__(self, client: HttpClient) -> None:
        super().__init__(client)

    def scrape_products(self, urls: Iterable[str]) -> Iterable[Product]:
        raise NotImplementedError("Implement Versed scraper based on network analysis or HTML parsing.")
