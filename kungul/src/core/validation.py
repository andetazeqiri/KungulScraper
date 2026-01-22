from typing import List, Tuple
from .models import Product


class ValidationError:
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
    
    def __str__(self) -> str:
        return f"{self.field}: {self.message}"


class ProductValidator:
    """Validates extracted product data against required schema."""
    
    # Required fields that must not be empty
    REQUIRED_FIELDS = ["product_name", "brand_name", "image"]
    
    # Fields that should contain data when possible
    RECOMMENDED_FIELDS = ["barcode", "category", "description"]
    
    # Minimum length requirements
    MIN_LENGTHS = {
        "product_name": 3,
        "brand_name": 2,
        "description": 10,
        "barcode": 5,
    }
    
    @staticmethod
    def validate(product: Product) -> Tuple[bool, List[ValidationError]]:
        """
        Validate a product against the schema.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        for field in ProductValidator.REQUIRED_FIELDS:
            value = getattr(product, field, "").strip()
            if not value:
                errors.append(ValidationError(field, "Required field is empty"))
                continue
            
            # Check minimum length
            if field in ProductValidator.MIN_LENGTHS:
                min_len = ProductValidator.MIN_LENGTHS[field]
                if len(value) < min_len:
                    errors.append(
                        ValidationError(
                            field, 
                            f"Too short (min {min_len} chars, got {len(value)})"
                        )
                    )
        
        # Check image URL format
        if product.image:
            if not product.image.startswith("http"):
                errors.append(
                    ValidationError("image", "Invalid URL format (must start with http)")
                )
        
        # Check barcode format (should be numeric if present)
        if product.barcode:
            if not product.barcode.isdigit():
                errors.append(
                    ValidationError("barcode", "Barcode should be numeric only")
                )
        
        # Check ingredients format
        if product.ingredients:
            # Ingredients should be a list of strings, not a string
            if isinstance(product.ingredients, list):
                if len(product.ingredients) == 0:
                    errors.append(
                        ValidationError(
                            "ingredients", 
                            "Ingredients list is empty"
                        )
                    )
                # Check for suspiciously long ingredient entries (likely unparsed strings)
                for ingredient in product.ingredients:
                    if len(ingredient) > 200:
                        errors.append(
                            ValidationError(
                                "ingredients",
                                f"Ingredient entry too long ({len(ingredient)} chars): likely unparsed"
                            )
                        )
        
        # Warn about empty recommended fields
        warnings = []
        for field in ProductValidator.RECOMMENDED_FIELDS:
            value = getattr(product, field, "").strip()
            if not value:
                warnings.append(ValidationError(field, "Recommended field is empty"))
        
        is_valid = len(errors) == 0
        all_issues = errors + warnings
        
        return is_valid, all_issues
    
    @staticmethod
    def validate_batch(products: List[Product]) -> dict:
        """
        Validate a batch of products and return statistics.
        
        Returns:
            dict with validation statistics
        """
        valid_count = 0
        invalid_count = 0
        all_errors = []
        
        for idx, product in enumerate(products, 1):
            is_valid, issues = ProductValidator.validate(product)
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                for issue in issues:
                    all_errors.append(f"Product {idx}: {issue}")
        
        return {
            "total": len(products),
            "valid": valid_count,
            "invalid": invalid_count,
            "validity_rate": (valid_count / len(products) * 100) if products else 0,
            "errors": all_errors,
        }
