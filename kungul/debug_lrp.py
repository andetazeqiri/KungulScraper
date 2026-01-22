#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import json

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://www.notino.de/la-roche-posay/effaclar-reinigungsgel-fur-fettige-haut/p-75718/')
print("Waiting for Effaclar product page...")
time.sleep(10)

soup = BeautifulSoup(driver.page_source, 'lxml')

print("\n=== Page Title ===")
print(f"Page title tag: {driver.title}")

print("\n=== JSON-LD Data ===")
for tag in soup.find_all("script", type="application/ld+json"):
    content = tag.string or tag.get_text()
    if content:
        try:
            data = json.loads(content)
            if isinstance(data, dict) and data.get("@type"):
                print(f"Type: {data.get('@type')}")
                print(f"Name: {data.get('name', 'N/A')}")
                print(f"Brand: {data.get('brand', 'N/A')}")
                print(f"Image: {str(data.get('image', 'N/A'))[:80]}")
                print()
        except:
            pass

print("\n=== Meta Tags ===")
for tag in soup.find_all("meta"):
    name = tag.get("property") or tag.get("name")
    content = tag.get("content", "")
    if name in ["og:title", "og:description", "og:image", "product:retailer_item_id"]:
        print(f"{name}: {content[:80]}")

print("\n=== Headings ===")
for h1 in soup.find_all("h1")[:3]:
    text = h1.get_text(strip=True)
    print(f"H1: {text[:80]}")

print("\n=== Product Name Candidates ===")
for selector in ["[data-testid='product-name']", "[data-testid='pd-title']", "h1[data-testid*='title']"]:
    elem = soup.select_one(selector)
    if elem:
        print(f"{selector}: {elem.get_text(strip=True)[:80]}")

print("\n=== Brand Candidates ===")
for elem in soup.find_all(["a", "span"], {"data-testid": lambda x: x and "brand" in str(x).lower()}):
    text = elem.get_text(strip=True)
    print(f"[{elem.get('data-testid')}]: {text[:80]}")

print("\n=== Image Candidates ===")
for selector in ["[data-testid*='image']", "img[src*='notino']"]:
    elems = soup.select(selector)[:2]
    for elem in elems:
        src = elem.get("src") or elem.get("data-src") or ""
        print(f"{selector}: {src[:80]}")

driver.quit()
