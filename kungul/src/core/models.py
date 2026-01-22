from dataclasses import dataclass, field
from typing import List
import json
from .cleaning import clean_text, clean_list


@dataclass
class Product:
    barcode: str = ""
    product_name: str = ""
    description: str = ""
    ingredients: List[str] = field(default_factory=list)
    image: str = ""
    brand_name: str = ""
    category: str = ""
    concerns: List[str] = field(default_factory=list)

    def normalized(self) -> "Product":
        return Product(
            barcode=clean_text(self.barcode),
            product_name=clean_text(self.product_name),
            description=clean_text(self.description),
            ingredients=clean_list(self.ingredients),
            image=clean_text(self.image),
            brand_name=clean_text(self.brand_name),
            category=clean_text(self.category),
            concerns=clean_list(self.concerns),
        )

    def to_pipe_row(self) -> str:
        normalized = self.normalized()
        ingredients_field = (
            json.dumps(normalized.ingredients, ensure_ascii=False)
            if normalized.ingredients
            else ""
        )
        concerns_field = (
            json.dumps(normalized.concerns, ensure_ascii=False)
            if normalized.concerns
            else ""
        )
        fields = [
            normalized.barcode,
            normalized.product_name,
            normalized.description,
            ingredients_field,
            normalized.image,
            normalized.brand_name,
            normalized.category,
            concerns_field,
        ]
        return "|".join(fields)
