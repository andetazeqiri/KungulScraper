import scrapy
from typing import Iterator, Dict, Any
from scrapy.http import Response


class NotinoSpider(scrapy.Spider):
    name = "notino"
    custom_settings = {
        "USER_AGENT": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 2,
        "COOKIES_ENABLED": True,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        },
    }

    def __init__(self, urls: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = []
        if urls:
            with open(urls, "r", encoding="utf-8") as f:
                self.start_urls = [line.strip() for line in f if line.strip()]

    def parse(self, response: Response) -> Iterator[Dict[str, Any]]:
        barcode = (
            response.xpath('//meta[@property="product:retailer_item_id"]/@content').get()
            or response.xpath('//meta[@property="gtin13"]/@content').get()
            or ""
        )
        
        product_name = (
            response.xpath('//meta[@property="og:title"]/@content').get()
            or response.xpath('//h1[@itemprop="name"]/text()').get()
            or response.css("h1::text").get()
            or ""
        )
        
        description = (
            response.xpath('//meta[@property="og:description"]/@content').get()
            or response.xpath('//*[@itemprop="description"]//text()').getall()
        )
        if isinstance(description, list):
            description = " ".join(description)
        description = description or ""
        
        image = (
            response.xpath('//meta[@property="og:image"]/@content').get()
            or response.xpath('//img[@itemprop="image"]/@src').get()
            or ""
        )
        
        brand_name = (
            response.xpath('//*[@itemprop="brand"]//text()').get()
            or response.css('[data-testid="brand-name"]::text').get()
            or ""
        )
        
        # Try breadcrumb for category
        breadcrumbs = response.css("nav[aria-label*='read'] li::text").getall()
        category = breadcrumbs[-1].strip() if breadcrumbs else ""
        
        # Extract ingredients - common patterns
        ingredients = []
        ingredients_section = response.xpath(
            '//*[contains(translate(text(), "INGREDIENTS", "ingredients"), "ingredients")]'
            '/following-sibling::*[1]//text()'
        ).getall()
        
        if ingredients_section:
            ingredients_text = " ".join(ingredients_section).strip()
            ingredients = [i.strip() for i in ingredients_text.split(",") if i.strip()]
        
        yield {
            "barcode": barcode.strip(),
            "product_name": product_name.strip(),
            "description": description.strip(),
            "ingredients": ingredients,
            "image": image.strip(),
            "brand_name": brand_name.strip(),
            "category": category.strip(),
            "concerns": [],
        }
