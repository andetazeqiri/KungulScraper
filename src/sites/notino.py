import json
import time
from html import unescape
from typing import Iterable, List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from core.models import Product
from .base import SiteScraper


class NotinoScraper(SiteScraper):
    """Selenium-based scraper for Notino (bypasses Cloudflare protection)."""

    def scrape_products(self, urls: Iterable[str]) -> Iterable[Product]:
        chrome_options = Options()
        # Try without headless - more likely to bypass Cloudflare
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        service = Service(ChromeDriverManager().install())

        for url in urls:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            try:
                driver.get(url)
                # Wait longer for Cloudflare challenge to complete
                print(f"Waiting for Cloudflare challenge to complete for {url}...")
                time.sleep(10)
                # If we got redirected to generic/404 page, retry once
                if "Parfum & Kosmetik online shop" in driver.title or "nichts beschädigt" in driver.page_source:
                    print("Detected generic/404 page, retrying once...")
                    time.sleep(5)
                    driver.get(url)
                    time.sleep(8)
                
                # Wait for product content to appear (checking for specific element)
                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1[data-testid='pd-title'], h1"))
                    )
                    print("Product page loaded successfully")
                except:
                    print(f"Warning: Timeout waiting for content on {url}")
                    print(f"Page title: {driver.title}")
                
                html = driver.page_source
                yield self._parse_product(html, url)
                time.sleep(2)  # Rate limiting
            finally:
                driver.quit()

    def _parse_product(self, html: str, url: str) -> Product:
        soup = BeautifulSoup(html, "lxml")

        # Check if page is a 404 error page
        error_heading = soup.select_one("h1")
        if error_heading and "nichts beschädigt" in error_heading.get_text(strip=True):
            print(f"⚠️  Warning: Product page is 404 error page for {url}")
            return Product()  # Return empty product

        json_entries = self._extract_json_ld(soup)
        product_ld = self._find_ld(json_entries, {"Product"})
        breadcrumbs_ld = self._find_ld(json_entries, {"BreadcrumbList"})

        barcode = (
            self._safe_get(product_ld, ["gtin13", "gtin", "sku"]) or
            self._extract_apollo_ean(soup) or
            self._pick_meta(soup, ["gtin13", "product:retailer_item_id"]) or
            ""
        )

        product_name = (
            self._clean_string(self._safe_get(product_ld, ["name"]))
            or self._pick_meta(soup, ["og:title", "twitter:title"]) 
            or self._text(soup.select_one("h1[data-testid*='title']"))
            or self._text(soup.select_one("h1"))
            or self._text(soup.select_one("[data-testid='product-name']"))
        )

        description = (
            self._clean_string(self._safe_get(product_ld, ["description"]))
            or self._pick_meta(soup, ["og:description", "description"]) 
            or self._text(soup.select_one("[itemprop='description']"))
            or self._text(soup.select_one("[data-testid='product-description']"))
        )

        image = (
            self._pick_image_from_ld(product_ld)
            or self._pick_meta(soup, ["og:image", "twitter:image"])
            or self._get_src(soup.select_one("[itemprop='image']"))
            or self._get_src(soup.select_one("[data-testid*='image']"))
            or self._get_src(soup.select_one("[data-testid='product-image']"))
        )

        brand_name = (
            self._clean_string(self._safe_get(product_ld, ["brand", "name"]))
            or self._clean_string(self._safe_get(product_ld, ["brand"]))
            or self._text(soup.select_one("[itemprop='brand']"))
            or self._text(soup.select_one("[data-testid='brand-name']"))
            or self._text(soup.select_one(".pd-brand"))
            or self._extract_brand_from_breadcrumb(soup)
        )

        category = (
            self._breadcrumb_category(breadcrumbs_ld)
            or self._clean_string(self._safe_get(product_ld, ["category"]))
        )

        if not category:
            breadcrumbs = soup.select("nav[aria-label*='read'] a, .breadcrumb a")
            category = self._text(breadcrumbs[-1]) if breadcrumbs else ""

        ingredients = self._extract_ingredients(soup)

        return Product(
            barcode=barcode,
            product_name=product_name,
            description=description,
            ingredients=ingredients,
            image=image or "",
            brand_name=brand_name,
            category=category or "",
            concerns=[],
        )

    def _extract_json_ld(self, soup: BeautifulSoup) -> List[dict]:
        entries: List[dict] = []
        for tag in soup.find_all("script", type="application/ld+json"):
            content = tag.string or tag.get_text()
            if not content:
                continue
            try:
                parsed = json.loads(content)
            except Exception:
                continue
            if isinstance(parsed, list):
                entries.extend([item for item in parsed if isinstance(item, dict)])
            elif isinstance(parsed, dict):
                entries.append(parsed)
        return entries

    def _find_ld(self, entries: List[dict], target_types: set) -> Optional[dict]:
        for entry in entries:
            type_field = entry.get("@type") if isinstance(entry, dict) else None
            types = type_field if isinstance(type_field, list) else [type_field]
            if any(t in target_types for t in types if t):
                return entry
        return None

    def _clean_string(self, value: Optional[str]) -> str:
        if value is None:
            return ""
        text = unescape(str(value))
        return BeautifulSoup(text, "lxml").get_text(" ", strip=True)

    def _pick_image_from_ld(self, product_ld: Optional[dict]) -> str:
        if not isinstance(product_ld, dict):
            return ""
        image = product_ld.get("image")
        if isinstance(image, list):
            for item in image:
                if item:
                    return str(item)
        elif isinstance(image, str):
            return image
        return ""

    def _breadcrumb_category(self, breadcrumb_ld: Optional[dict]) -> str:
        if not isinstance(breadcrumb_ld, dict):
            return ""
        items = breadcrumb_ld.get("itemListElement")
        if not isinstance(items, list):
            return ""
        for item in reversed(items):
            if not isinstance(item, dict):
                continue
            entry = item.get("item") if isinstance(item.get("item"), dict) else item
            name = self._clean_string(self._safe_get(entry, ["name"]))
            if name:
                return name
        return ""

    def _extract_apollo_ean(self, soup: BeautifulSoup) -> str:
        script = soup.find("script", id="__APOLLO_STATE__")
        if not script:
            return ""
        content = script.string or script.get_text()
        if not content:
            return ""
        try:
            state = json.loads(content)
        except Exception:
            return ""
        if isinstance(state, dict):
            for value in state.values():
                if isinstance(value, dict):
                    ean = value.get("eanCode") or value.get("gtin13")
                    if ean:
                        return str(ean)
        return ""

    def _safe_get(self, data: Optional[dict], keys: List[str]):
        if not isinstance(data, dict):
            return None
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def _pick_meta(self, soup: BeautifulSoup, names: List[str]) -> str:
        for name in names:
            node = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
            if node and node.get("content"):
                return node["content"].strip()
        return ""

    def _text(self, node) -> str:
        return node.get_text(strip=True) if node else ""
    
    def _get_src(self, node) -> str:
        if not node:
            return ""
        return node.get("src", "") or node.get("data-src", "")
    
    def _extract_brand_from_breadcrumb(self, soup: BeautifulSoup) -> str:
        """Extract brand name from breadcrumb navigation."""
        breadcrumbs = soup.select("nav a, .breadcrumb a")
        if breadcrumbs and len(breadcrumbs) > 1:
            # Usually brand is in second breadcrumb
            return self._text(breadcrumbs[1])
        return ""

    def _extract_ingredients(self, soup: BeautifulSoup) -> List[str]:
        # Try multiple patterns for ingredients section
        heading = None
        for tag in soup.find_all(["h2", "h3", "h4", "strong", "span"]):
            text = tag.get_text(strip=True).lower()
            if any(word in text for word in ["ingredients", "inhaltsstoffe", "zutaten"]):
                heading = tag
                break
        
        if not heading:
            return []
        
        # Look for ingredients in next siblings
        container = heading.find_next(["p", "div", "ul", "ol", "span"])
        if not container:
            return []
        
        text = container.get_text(" ", strip=True)
        parts = [part.strip() for part in text.split(",") if part.strip()]
        return parts
