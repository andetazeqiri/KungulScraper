#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://www.notino.de/cerave/moisturizers-feuchtigkeitscreme-spf-50/p-16130224/')
print("Waiting 10s for page load...")
time.sleep(10)

try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, 'h1'))
    )
    print("Page loaded!")
except:
    print("Timeout waiting for h1")

soup = BeautifulSoup(driver.page_source, 'lxml')

# Save HTML
with open('notino_real.html', 'w', encoding='utf-8') as f:
    f.write(driver.page_source)

# Look for brand
print("\n=== Brand candidates ===")
for link in soup.find_all('a', {'data-testid': lambda x: x and 'brand' in str(x).lower()})[:5]:
    print(f"  {link.get('data-testid')}: {link.get_text(strip=True)}")

# Look for EAN/barcode
print("\n=== EAN/Barcode candidates ===")
for elem in soup.find_all(string=lambda x: x and 'EAN' in str(x).upper()):
    parent = elem.find_parent()
    siblings = parent.find_next_siblings() if parent else []
    print(f"  Found 'EAN' in {parent.name if parent else '?'}")
    for sib in siblings[:3]:
        text = sib.get_text(strip=True)
        if text and text != 'EAN':
            print(f"    Next sibling: {text[:50]}")

# Look for all headings
print("\n=== All H2/H3/H4 headings ===")
for tag in soup.find_all(['h2', 'h3', 'h4'])[:15]:
    print(f"  {tag.name}: {tag.get_text(strip=True)[:60]}")

driver.quit()
print("\nHTML saved to notino_real.html")
