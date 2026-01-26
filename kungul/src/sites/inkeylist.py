import json
import re
import time
from typing import Iterable, List
from bs4 import BeautifulSoup
from core.models import Product
from core.client import HttpClient
from .base import SiteScraper


class InkeyListScraper(SiteScraper):
    def __init__(self, client: HttpClient) -> None:
        super().__init__(client)

    def scrape_products(self, urls: Iterable[str]) -> Iterable[Product]:
        for url in urls:
            response = self.client.fetch(url)
            html = response.text
            yield self._parse_product(html, url)
            time.sleep(2.5)  # politeness delay to reduce 429s

    def _parse_product(self, html: str, url: str) -> Product:
        soup = BeautifulSoup(html, "lxml")
        
        # Extract product data from JSON-LD script
        product_data = self._extract_product_json(soup)
        
        # Get data from the JSON if available
        if product_data:
            barcode = product_data.get("barcode", "")
            product_name = product_data.get("title", "") or product_data.get("name", "")
            brand_name = product_data.get("brand", "") or product_data.get("vendor", "")
            image_url = product_data.get("featured_image", "")
            
            # If no featured_image, get from images array
            if not image_url and product_data.get("images"):
                images = product_data.get("images", [])
                if images:
                    image_url = images[0]
            
            # Get description from meta tags as fallback
            description = (
                self._get_meta_content(soup, "og:description") or 
                self._get_meta_content(soup, "description") or
                product_data.get("description", "")
            )
            
            # Clean up description HTML
            if description:
                description = BeautifulSoup(description, "lxml").get_text(" ", strip=True)
            
            # Extract product category from tags
            tags = product_data.get("tags", [])
            category = tags[0] if tags else product_data.get("type", "")
            
            # Extract full image URL
            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url
            elif image_url and not image_url.startswith("http"):
                image_url = "https://uk.theinkeylist.com" + image_url
                
            # Try to extract ingredients from the page (JSON description or HTML fallback)
            ingredients = self._extract_ingredients(soup, html, url)
            
            return Product(
                barcode=barcode,
                product_name=product_name,
                description=description,
                ingredients=ingredients,
                image=image_url,
                brand_name=brand_name or "The INKEY List",
                category=category,
                concerns=[],
            )
        
        # Fallback if JSON not found
        return Product(
            barcode="",
            product_name=self._get_meta_content(soup, "og:title") or "",
            description=self._get_meta_content(soup, "og:description") or "",
            ingredients=[],
            image=self._get_meta_content(soup, "og:image") or "",
            brand_name="The INKEY List",
            category="",
            concerns=[],
        )

    def _extract_product_json(self, soup: BeautifulSoup) -> dict:
        """Extract product data from window.SwymProductInfo.product JSON"""
        for script in soup.find_all("script"):
            text = script.string or ""
            # Look for the product JSON data in window.SwymProductInfo.product
            if "window.SwymProductInfo.product" in text:
                try:
                    # Extract the JSON object after the assignment
                    start_marker = "window.SwymProductInfo.product = "
                    start_idx = text.find(start_marker)
                    if start_idx == -1:
                        continue
                    
                    start_idx += len(start_marker)
                    
                    # Find the end of the JSON object
                    brace_count = 0
                    end_idx = start_idx
                    in_json = False
                    
                    for i in range(start_idx, len(text)):
                        char = text[i]
                        if char == '{':
                            brace_count += 1
                            in_json = True
                        elif char == '}':
                            brace_count -= 1
                            if in_json and brace_count == 0:
                                end_idx = i + 1
                                break
                    
                    json_text = text[start_idx:end_idx]
                    
                    try:
                        product_data = json.loads(json_text)
                        
                        # Extract barcode from variants if not at top level
                        if not product_data.get("barcode") and product_data.get("variants"):
                            variants = product_data.get("variants", [])
                            if variants and isinstance(variants, list) and len(variants) > 0:
                                product_data["barcode"] = variants[0].get("barcode", "")
                        
                        # Extract brand
                        if not product_data.get("brand"):
                            product_data["brand"] = product_data.get("vendor", "")
                        
                        # Extract featured image
                        if not product_data.get("featured_image") and product_data.get("images"):
                            images = product_data.get("images", [])
                            if images:
                                product_data["featured_image"] = images[0]
                        elif product_data.get("featured_image"):
                            pass  # Already has featured_image
                        
                        return product_data
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        continue
                except Exception as e:
                    print(f"Error extracting JSON: {e}")
                    continue
        return {}

    def _extract_ingredients(self, soup: BeautifulSoup, html_str: str, url: str) -> str:
        """Extract full ingredients list (INCI) from product page HTML."""
        
        # Find INCI list which starts with "Aqua (Water)" and contains comma-separated ingredients
        html_lower = html_str.lower()
        # Handle variants like "Aqua (Water/Eau)"
        idx = html_lower.find('aqua (water)')
        if idx == -1:
            idx = html_lower.find('aqua (water/eau')
        
        if idx != -1:
            # Extract from Aqua onwards, up to 3000 chars (should cover all ingredients)
            inci_section = html_str[idx:idx+3000]
            
            # Remove HTML tags
            inci_clean = re.sub(r'<[^>]+>', ' ', inci_section)
            
            # Normalize whitespace
            inci_clean = re.sub(r'\s+', ' ', inci_clean).strip()
            
            # Truncate at common end markers (period, HTML remnant, etc)
            for marker in ['.', '<', '©']:
                pos = inci_clean.find(marker)
                if pos > 100:  # Only cut if we have substantial content
                    inci_clean = inci_clean[:pos].strip()
                    break
            
            # Return if we have meaningful content
            if len(inci_clean) > 80:
                return inci_clean

        # Fallback 1: try to find a long comma-separated INCI list anywhere in the cleaned HTML
        # Avoid CSS selectors by excluding '.' in tokens
        cleaned = re.sub(r'<[^>]+>', ' ', html_str)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        pattern = r'([A-Za-z0-9 \-/\(\)%]+,\s*){6,}[A-Za-z0-9 \-/\(\)%]+'
        candidates = list(re.finditer(pattern, cleaned))
        if candidates:
            # Pick the longest candidate
            filtered = []
            for m in candidates:
                s = m.group(0)
                # Heuristics to avoid CSS lists and unrelated comma groups
                if s.count('(') < 2:
                    continue
                has_signal = any(k in s.lower() for k in [
                    'aqua', 'water', 'acid', 'alcohol', 'gly', 'oil', 'butyl', 'peptide', 'retin', 'vitamin', 'sodium'
                ])
                if not has_signal:
                    continue
                filtered.append(s)

            if filtered:
                best = max(filtered, key=len)
                inci = best.strip()
                # Heuristic: ensure it's not absurdly long or short
                if 100 <= len(inci) <= 3000 and inci.count(',') >= 7:
                    return inci

        # Fallback 2: keyword scan for common actives
        common_ingredients = [
            "Ceramides", "Bio-Active Ceramides", "Glycerin", "Hyaluronic Acid",
            "Vitamin C", "Retinol", "Niacinamide", "Caffeine", "Salicylic Acid",
            "Squalane", "Peptides", "Collagen", "Azelaic Acid", "Alanine",
            "Shea Butter", "Oat", "Polyglutamic Acid", "Ectoin", "Exosome",
            "PDRN", "Succinic Acid", "Tranexamic Acid", "Fulvic Acid"
        ]

        found_ingredients = []
        html_lower = html_str.lower()
        for ingredient in common_ingredients:
            if ingredient.lower() in html_lower:
                found_ingredients.append(ingredient)

        if found_ingredients:
            return ", ".join(found_ingredients)

        return ""

    def _get_meta_content(self, soup: BeautifulSoup, property_name: str) -> str:
        """Get content from meta tag by property or name"""
        tag = soup.find("meta", attrs={"property": property_name}) or \
              soup.find("meta", attrs={"name": property_name})
        if tag and tag.get("content"):
            return tag["content"].strip()
        return ""
