from pathlib import Path
from typing import Iterable, Set
from .models import Product


HEADER = "barcode|product_name|description|ingredients|image|brand_name|category|concerns"


def write_products(path: Path, products: Iterable[Product]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing products to avoid duplicates
    existing_products: Set[str] = set()
    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            lines = file.readlines()
            if len(lines) > 1:  # Skip header
                existing_products = set(line.strip() for line in lines[1:] if line.strip())
    
    # Write header if file doesn't exist, otherwise append
    mode = "w" if not path.exists() else "a"
    with path.open(mode, encoding="utf-8") as file:
        if mode == "w":
            file.write(f"{HEADER}\n")
        
        for product in products:
            product_row = product.to_pipe_row()
            if product_row not in existing_products:
                   # Skip empty products (404 errors, failed extractions)
                   if not product.product_name or not product.brand_name or not product.image:
                       continue
                   file.write(f"{product_row}\n")
