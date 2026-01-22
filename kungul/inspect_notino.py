#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://www.notino.de/cerave/moisturizers-feuchtigkeitscreme-spf-50/p-16130224/')
time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'lxml')

# Try to find h1
h1 = soup.find('h1')
print('Page title (h1):', h1.get_text(strip=True) if h1 else 'NOT FOUND')

# Find all links with brand in href or text
print('\n=== Brand candidates ===')
for link in soup.find_all('a', href=True):
    text = link.get_text(strip=True)
    if text and len(text) < 50 and ('cerave' in link['href'].lower() or 'brand' in link.get('class', [])):
        print(f'  {text} -> {link["href"]}')

# Find anything with EAN in text
print('\n=== EAN candidates ===')
for elem in soup.find_all(string=lambda x: x and 'EAN' in str(x).upper()):
    parent = elem.find_parent()
    if parent:
        print(f'  {parent.name}: {parent.get_text(strip=True)[:100]}')

# All h2, h3, h4 headings
print('\n=== All headings ===')
for tag in soup.find_all(['h2', 'h3', 'h4'])[:10]:
    print(f'  {tag.name}: {tag.get_text(strip=True)}')

driver.quit()
print('\nInspection complete')
