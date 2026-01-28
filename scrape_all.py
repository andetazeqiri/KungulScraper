#!/usr/bin/env python3
"""Direct scraper script for all Inkey List products"""
import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sites.inkeylist import InkeyListScraper
from core.client import HttpClient
from core.writer import write_products

def main():
    parser = argparse.ArgumentParser(description="Scrape The Inkey List products")
    parser.add_argument(
        "--output",
        default="products_inkey_all.txt",
        help="Output pipe-delimited TXT file (default: products_inkey_all.txt)",
    )
    args = parser.parse_args()
    # Read URLs
    with open('inkey_all_urls.txt', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(urls)} URLs to scrape")
    
    # Initialize scraper
    client = HttpClient()
    scraper = InkeyListScraper(client)
    
    # Scrape and collect
    products = []
    try:
        for i, product in enumerate(scraper.scrape_products(urls), 1):
            products.append(product)
            print(f"  [{i}/{len(urls)}] {product.product_name}")
    except KeyboardInterrupt:
        print(f"\nInterrupted after {len(products)} products")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Write output
    if products:
        from pathlib import Path
        output_file = Path(args.output)
        write_products(output_file, products)
        print(f"\nSaved {len(products)} products to {output_file}")
    
if __name__ == '__main__':
    main()
