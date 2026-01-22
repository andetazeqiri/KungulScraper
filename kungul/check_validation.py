#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.models import Product
from core.validation import ProductValidator

# Read products
products = []
file_path = Path(__file__).parent / "products.txt"

with file_path.open("r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if idx == 0:  # Skip header
            continue
        line = line.strip()
        if not line:
            continue
        
        parts = line.split("|")
        if len(parts) < 8:
            continue
        
        product = Product(
            barcode=parts[0],
            product_name=parts[1],
            description=parts[2],
            ingredients=[],
            image=parts[4],
            brand_name=parts[5],
            category=parts[6],
            concerns=[],
        )
        products.append(product)

# Validate
print("\n" + "="*60)
print("PRODUCT DATA VALIDATION REPORT")
print("="*60 + "\n")

results = ProductValidator.validate_batch(products)

print(f"Total products: {len(products)}")
print(f"Valid products: {results['valid']}")
print(f"Invalid products: {results['invalid']}")
print(f"Validity rate: {results['validity_rate']:.1f}%\n")

if results["errors"]:
    print("="*60)
    print("ISSUES FOUND:")
    print("="*60 + "\n")
    for error in results["errors"][:20]:
        print(f"  • {error}")
    if len(results["errors"]) > 20:
        print(f"  ... and {len(results['errors']) - 20} more issues")
else:
    print("✨ No issues found!")

print("\n" + "="*60)
print("PRODUCT DETAILS:")
print("="*60 + "\n")

for idx, product in enumerate(products, 1):
    is_valid, issues = ProductValidator.validate(product)
    status = "✅" if is_valid else "❌"
    
    print(f"{status} Product {idx}:")
    print(f"   Name: {product.product_name[:50]}")
    print(f"   Brand: {product.brand_name}")
    print(f"   Barcode: {product.barcode or '(empty)'}")
    print(f"   Category: {product.category or '(empty)'}")
    print(f"   Image: {product.image[:40] if product.image else '(empty)'}...")
    print(f"   Description length: {len(product.description)} chars")
    
    if issues:
        print(f"   Issues:")
        for issue in issues:
            print(f"      ⚠️  {issue}")
    print()
