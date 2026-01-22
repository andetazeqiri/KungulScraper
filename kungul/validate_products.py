#!/usr/bin/env python3
"""
Validation tool to check extracted product data quality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import Product
from core.validation import ProductValidator


def parse_products_file(file_path: Path):
    """Parse pipe-delimited products file."""
    products = []
    
    with file_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            return products
        
        # Skip header
        for line in lines[1:]:
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
                ingredients=[],  # Will be parsed from JSON
                image=parts[4],
                brand_name=parts[5],
                category=parts[6],
                concerns=[],  # Will be parsed from JSON
            )
            products.append(product)
    
    return products


def print_report(file_path: Path):
    """Print validation report for products file."""
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    products = parse_products_file(file_path)
    
    if not products:
        print(f"⚠️  No products found in {file_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"📋 PRODUCT DATA VALIDATION REPORT")
    print(f"{'='*60}\n")
    
    print(f"File: {file_path}")
    print(f"Total products: {len(products)}\n")
    
    # Validate each product
    results = ProductValidator.validate_batch(products)
    
    print(f"✅ Valid products: {results['valid']}")
    print(f"❌ Invalid products: {results['invalid']}")
    print(f"📊 Validity rate: {results['validity_rate']:.1f}%\n")
    
    # Print errors if any
    if results['errors']:
        print(f"{'='*60}")
        print("🔍 ISSUES FOUND:")
        print(f"{'='*60}\n")
        for error in results['errors']:
            print(f"  • {error}")
    else:
        print("✨ No issues found!")
    
    # Print detailed product info
    print(f"\n{'='*60}")
    print("📦 PRODUCT DETAILS:")
    print(f"{'='*60}\n")
    
    for idx, product in enumerate(products, 1):
        is_valid, issues = ProductValidator.validate(product)
        status = "✅" if is_valid else "❌"
        
        print(f"{status} Product {idx}:")
        print(f"   Name: {product.product_name[:50]}")
        print(f"   Brand: {product.brand_name}")
        print(f"   Barcode: {product.barcode or '(empty)'}")
        print(f"   Category: {product.category or '(empty)'}")
        print(f"   Image: {product.image[:50] if product.image else '(empty)'}")
        print(f"   Description: {len(product.description)} chars")
        print(f"   Ingredients: {len(product.ingredients)} items")
        
        if issues:
            print(f"   Issues:")
            for issue in issues:
                print(f"      ⚠️  {issue}")
        print()


if __name__ == "__main__":
    products_file = Path(__file__).parent.parent.parent / "products.txt"
    print_report(products_file)
