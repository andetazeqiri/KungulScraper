import json
from bs4 import BeautifulSoup
import requests

url = 'https://uk.theinkeylist.com/products/1-percent-retinol-serum'
html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
soup = BeautifulSoup(html, 'lxml')

# Extract handle
handle = url.rstrip("/").split("/")[-1]
print(f"Handle from URL: {handle}\n")

# Find search index script
found = False
for script in soup.find_all('script', {'type': 'application/json'}):
    text = script.string or ''
    if '"products"' in text and 'search_terms' in text:
        print("Found search index script")
        data = json.loads(text)
        products = data.get('products', [])
        print(f"Total products in index: {len(products)}")
        
        # Find matching product
        matching = [p for p in products if p.get('handle') == handle]
        print(f"Found matching product by handle: {bool(matching)}\n")
        
        if matching:
            p = matching[0]
            desc_html = p.get('description', '')
            desc_text = BeautifulSoup(desc_html, 'lxml').get_text(' ', strip=True)
            idx = desc_text.lower().find('ingredients')
            print(f"Found 'ingredients' at index: {idx}")
            if idx != -1:
                ing_text = desc_text[idx:idx+800]
                print("\n=== INGREDIENTS SECTION ===")
                print(ing_text)
                found = True
        break

if not found:
    print("WARNING: Could not extract full ingredients from JSON!")
