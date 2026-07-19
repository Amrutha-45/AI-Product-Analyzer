"""
services/openfoodfacts_service.py
-----------------------------------
Open Food Facts integration for two purposes:
  1. Barcode lookup: ground product_name / brand / ingredients in real data.
  2. Alternatives search: find better-scoring products in the same category.

Real OFF data always overrides AI-guessed data where available — this is
the grounding-over-generation principle from AI_PROMPT_SPEC.md Section 1.

OFF API docs: https://wiki.openfoodfacts.org/API
"""

import httpx
from typing import Any

from app.schemas.scan_result import AIScanResult, AlternativeSuggestion, ScanSource
from app.utils.logging import get_logger

logger = get_logger(__name__)

OFF_BASE_URL = "https://world.openfoodfacts.org"
OFF_SEARCH_URL = f"{OFF_BASE_URL}/cgi/search.pl"
OFF_PRODUCT_URL = f"{OFF_BASE_URL}/api/v2/product"
USER_AGENT = "AIProductAnalyzer/1.0 (contact@aiproductanalyzer.com)"

# Timeout for OFF API calls — OFF can be slow, but we don't want to
# block the response indefinitely.
OFF_TIMEOUT = 8.0


async def lookup_by_barcode(barcode: str) -> dict[str, Any] | None:
    """
    Look up a product by barcode on Open Food Facts.
    Returns the raw product dict on a match, or None if not found.
    """
    if not barcode or not barcode.strip():
        return None

    url = f"{OFF_PRODUCT_URL}/{barcode.strip()}.json"
    headers = {"User-Agent": USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=OFF_TIMEOUT) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.info("off_barcode_not_found", barcode=barcode, status=response.status_code)
                return None

            data = response.json()
            if data.get("status") != 1:
                logger.info("off_barcode_no_match", barcode=barcode)
                return None

            logger.info("off_barcode_found", barcode=barcode, product=data["product"].get("product_name"))
            return data["product"]

    except httpx.TimeoutException:
        logger.warning("off_barcode_timeout", barcode=barcode)
        return None
    except Exception as exc:
        logger.error("off_barcode_error", barcode=barcode, error=str(exc))
        return None


async def search_alternatives(category: str | None, limit: int = 3) -> list[AlternativeSuggestion]:
    """
    Search Open Food Facts for well-rated products in the same category.
    Returns a list of AlternativeSuggestion objects.
    """
    if not category:
        return []

    params = {
        "search_terms": category,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
        "sort_by": "nutriscore_score",
        "fields": "product_name,brands,nutriscore_grade,categories",
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=OFF_TIMEOUT) as client:
            response = await client.get(OFF_SEARCH_URL, params=params, headers=headers)
            if response.status_code != 200:
                return []

            products = response.json().get("products", [])

    except Exception as exc:
        logger.warning("off_alternatives_error", category=category, error=str(exc))
        return []

    alternatives: list[AlternativeSuggestion] = []
    for product in products[:limit]:
        name = product.get("product_name")
        brand = product.get("brands")
        grade = product.get("nutriscore_grade", "").upper()
        if not name:
            continue
        alternatives.append(
            AlternativeSuggestion(
                source="openfoodfacts",
                product_name=name,
                brand=brand,
                reason=f"Nutri-Score {grade} — a better-rated option in the same category.",
            )
        )

    return alternatives


def merge_off_data(ai_result: AIScanResult, off_product: dict[str, Any]) -> tuple[dict[str, Any], ScanSource]:
    """
    Merge real Open Food Facts product data over the AI-guessed fields.
    Returns a dict of override fields and the resulting ScanSource.

    Real data wins over AI guesses — this is the core grounding principle.
    Fields not available in OFF are left as the AI extracted them.
    """
    overrides: dict[str, Any] = {}

    off_name = off_product.get("product_name")
    if off_name:
        overrides["product_name"] = off_name

    off_brand = off_product.get("brands")
    if off_brand:
        overrides["brand"] = off_brand.split(",")[0].strip()  # OFF sometimes returns comma-separated brands

    off_category = off_product.get("categories_hierarchy")
    if off_category and isinstance(off_category, list):
        # Use the last (most specific) category
        last_category = off_category[-1]
        # Strip the "en:" language prefix if present
        overrides["category"] = last_category.replace("en:", "").replace("-", " ").title()

    logger.info(
        "off_data_merged",
        overridden_fields=list(overrides.keys()),
    )

    return overrides, ScanSource.openfoodfacts_merged
