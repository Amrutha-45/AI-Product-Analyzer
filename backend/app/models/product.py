"""
models/product.py
------------------
DB row model mirroring the `products` table in Supabase.
Products are deduplicated by barcode and cache raw Open Food Facts data.
"""

from typing import Any


def build_product_row(
    barcode: str,
    product_name: str | None,
    brand: str | None,
    category: str | None,
    off_raw: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a dict that maps directly to a `products` table row."""
    return {
        "barcode": barcode,
        "product_name": product_name,
        "brand": brand,
        "category": category,
        "off_data": off_raw,
    }
