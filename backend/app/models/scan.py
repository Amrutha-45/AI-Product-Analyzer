"""
models/scan.py
--------------
DB row model mirroring the `scans` table in Supabase.

This is intentionally separate from schemas/scan_result.py:
  - schemas  = what goes over the wire (API contract)
  - models   = what gets persisted (DB row shape)

They often look similar but conflating them is a classic mistake — the
day you want to store a field you don't want to expose in the API (e.g.
an internal confidence score), the split saves you.
"""

from __future__ import annotations
from typing import Any
from datetime import datetime, timezone
import uuid

from app.schemas.scan_result import ScanResult, ScanSource


def build_scan_row(
    result: Any,
    content_hash: str,
    device_id: str | None,
    front_image_url: str | None,
    back_image_url: str | None,
    ai_provider: str,
    prompt_version: str,
) -> dict[str, Any]:
    """
    Convert a fully assembled ScanResult into the flat dict that maps
    directly to a `scans` table row in Supabase.
    """
    category = getattr(result, "category", "Food")
    is_food = category in ("Food", "Beverage", "Fresh Produce")

    row = {
        "id": result.scan_id,
        "device_id": device_id,
        "content_hash": content_hash,
        "front_image_url": front_image_url,
        "back_image_url": back_image_url,
        "product_name": getattr(result, "product_name", None),
        "brand": getattr(result, "brand", None),
        "category": category,
        "barcode": getattr(result, "barcode", None),
        "source": getattr(result, "source", "ai_extracted"),
        "ai_provider": ai_provider,
        "prompt_version": prompt_version,
        "created_at": result.created_at,
    }

    if is_food:
        row.update({
            "expiry_status": result.expiry_status.value if getattr(result, "expiry_status", None) else None,
            "manufacturing_date": getattr(result, "manufacturing_date", None),
            "expiry_date": getattr(result, "expiry_date", None),
            "health_score": getattr(result, "health_score", 0),
            "ingredient_safety_score": getattr(result, "ingredient_safety_score", 0),
            "health_score_breakdown": [b.model_dump() for b in getattr(result, "health_score_breakdown", [])],
            "nutrition": result.nutrition.model_dump() if getattr(result, "nutrition", None) else {},
            "nova_class": result.nova_class.value if getattr(result, "nova_class", None) else None,
            "ingredients": [i.model_dump() for i in getattr(result, "ingredients", [])],
            "packaging_signals": result.packaging_analysis.model_dump() if getattr(result, "packaging_analysis", None) else {},
            "allergens": getattr(result, "allergens", []),
            "warnings": getattr(result, "warnings", []),
            "alternatives": [a.model_dump() for a in getattr(result, "alternatives", [])],
        })
    else:
        # Serialize non-food specific fields into category_data
        base_keys = set(row.keys()) | {"scan_id"}
        category_data = {k: v for k, v in result.model_dump().items() if k not in base_keys}
        row["category_data"] = category_data

    return row


def scan_row_to_result(row: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a raw Supabase `scans` row back into a dict that matches
    the ScanResult schema for returning via the API.
    """
    from app.schemas.scan_result import (
        PackagingAnalysis, Ingredient, AlternativeSuggestion,
        TextClarity, RiskLevel, ExpiryStatus, OverallConfidence,
    )

    category = row.get("category", "Food")
    is_food = category in ("Food", "Beverage", "Fresh Produce")

    if is_food:
        # Reconstruct nested objects from JSONB
        packaging_raw = row.get("packaging_signals") or {}
        ingredients_raw = row.get("ingredients") or []
        alternatives_raw = row.get("alternatives") or []
        breakdown_raw = row.get("health_score_breakdown") or []
        nutrition_raw = row.get("nutrition") or {}
    
        return {
            "scan_id": str(row["id"]),
            "created_at": str(row.get("created_at", "")),
            "source": row.get("source", ScanSource.ai_extracted.value),
            "product_name": row.get("product_name"),
            "brand": row.get("brand"),
            "category": category,
            "barcode": row.get("barcode"),
            "manufacturing_date": row.get("manufacturing_date"),
            "expiry_date": row.get("expiry_date"),
            "batch_number": row.get("batch_number"),
            "expiry_status": row.get("expiry_status", "unclear"),
            "ingredients": ingredients_raw,
            "allergens": row.get("allergens") or [],
            "health_score": row.get("health_score", 0),
            "ingredient_safety_score": row.get("ingredient_safety_score", 0),
            "health_score_breakdown": breakdown_raw,
            "nutrition": nutrition_raw,
            "nova_class": row.get("nova_class"),
            "packaging_analysis": packaging_raw,
            "warnings": row.get("warnings") or [],
            "ai_suggested_improvement": row.get("ai_suggested_improvement"),
            "ai_summary": row.get("ai_summary", ""),
            "overall_confidence": row.get("overall_confidence", "medium"),
            "confidence_reasoning": row.get("confidence_reasoning", ""),
            "alternatives": alternatives_raw,
        }
    else:
        category_data = row.get("category_data") or {}
        return {
            "scan_id": str(row["id"]),
            "created_at": str(row.get("created_at", "")),
            "source": row.get("source", "ai_extracted"),
            "product_name": row.get("product_name"),
            "brand": row.get("brand"),
            "category": category,
            **category_data
        }
