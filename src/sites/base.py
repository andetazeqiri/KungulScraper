from abc import ABC, abstractmethod
from typing import Iterable
from core.models import Product
from core.client import HttpClient


class SiteScraper(ABC):
    def __init__(self, client: HttpClient) -> None:
        self.client = client

    @abstractmethod
    def scrape_products(self, urls: Iterable[str]) -> Iterable[Product]:
        """Yield Product objects for the supplied product URLs."""
        raise NotImplementedError
