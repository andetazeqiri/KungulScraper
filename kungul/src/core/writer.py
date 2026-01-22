from pathlib import Path
from typing import Iterable
from .models import Product


HEADER = "barcode|product_name|description|ingredients|image|brand_name|category|concerns"


def write_products(path: Path, products: Iterable[Product]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write(f"{HEADER}\n")
        for product in products:
            file.write(f"{product.to_pipe_row()}\n")
