#!/usr/bin/env python3
"""Crawl The Inkey List website to find all product URLs"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

BASE_URL = "https://uk.theinkeylist.com"
PRODUCTS_URL = f"{BASE_URL}/products"

def crawl_products():
    """Crawl all product pages and extract product URLs"""
    product_urls = set()
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    
    print(f"Starting crawl from {PRODUCTS_URL}")
    
    try:
        # Try to fetch the products page
        response = session.get(PRODUCTS_URL, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        
        # Find all product links - look for common patterns
        # Try different selectors
        selectors = [
            'a[href*="/products/"]',
            '.product-link',
            '[data-product-url]',
            'a.product-card',
            'a[class*="product"]'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            if links:
                print(f"Found {len(links)} links using selector: {selector}")
                for link in links:
                    href = link.get('href') or link.get('data-product-url')
                    if href and '/products/' in href:
                        full_url = urljoin(BASE_URL, href)
                        # Only keep actual product pages
                        if '/products/' in full_url and not full_url.endswith('/products'):
                            product_urls.add(full_url)
        
        # Also check for pagination and product grid
        print(f"Found {len(product_urls)} unique product URLs")
        
        # Look for pagination links
        pagination_links = soup.find_all('a', {'rel': 'next'})
        for link in pagination_links:
            href = link.get('href')
            if href:
                next_page = urljoin(BASE_URL, href)
                print(f"Found pagination link: {next_page}")
                # Optionally follow pagination
        
        # Alternative: Look for all product links in the page
        all_links = soup.find_all('a', href=True)
        product_pattern_count = 0
        for link in all_links:
            href = link['href']
            if '/products/' in href and not href.endswith('/products'):
                full_url = urljoin(BASE_URL, href)
                product_urls.add(full_url)
                product_pattern_count += 1
        
        print(f"Total product URLs found: {len(product_urls)}")
        
        return sorted(list(product_urls))
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {PRODUCTS_URL}: {e}")
        return []

if __name__ == "__main__":
    urls = crawl_products()
    
    # Save to file
    output_file = "inkey_all_urls.txt"
    with open(output_file, "w") as f:
        for url in urls:
            f.write(url + "\n")
    
    print(f"\nSaved {len(urls)} product URLs to {output_file}")
    
    # Print first 10
    if urls:
        print("\nFirst 10 product URLs:")
        for url in urls[:10]:
            print(f"  {url}")
