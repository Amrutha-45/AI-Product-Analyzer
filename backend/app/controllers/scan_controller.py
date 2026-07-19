"""
controllers/scan_controller.py
--------------------------------
Orchestration layer for the full scan pipeline.

This is the one function that knows the ORDER of operations:
  1. Validate images
  2. Compute content hash
  3. Check cache (return early on hit)
  4. Run AI extraction (with retry)
  5. Enrich with Open Food Facts (if barcode present)
  6. Compute trust score (deterministic)
  7. Assemble final ScanResult
  8. Persist to database (fire-and-forget)
  9. Return result

Routes and services never talk to each other directly — this controller
is the seam between them.
"""

from __future__ import annotations
import asyncio
import uuid
from datetime import datetime, timezone

from app.schemas.scan_result import (
    AIScanResult, ScanResult, ScanSource, AlternativeSuggestion
)
from app.services.vision_extractor import run_extraction, detect_category
from app.services.openfoodfacts_service import (
    lookup_by_barcode, search_alternatives, merge_off_data
)
from app.services.health_score_service import compute_health_score
from app.services.ingredient_safety_service import compute_ingredient_safety_score
from app.services.cache_service import get_cached_scan, save_scan
from app.models.scan import build_scan_row, scan_row_to_result
from app.utils.hashing import compute_content_hash
from app.utils.image_validation import validate_image, ImageValidationError
from app.prompts.extraction_prompt import PROMPT_VERSION, DEVELOPER_PROMPT
from app.utils.logging import get_logger

from app.schemas.category_schemas import (
    ProductCategory,
    MedicineScanResult, CosmeticScanResult, FertilizerScanResult,
    PesticideScanResult, HouseholdChemicalScanResult, OtherScanResult
)
from app.prompts.category_prompts import (
    MEDICINE_PROMPT, COSMETIC_PROMPT, FERTILIZER_PROMPT,
    PESTICIDE_PROMPT, HOUSEHOLD_CHEMICAL_PROMPT, OTHER_PROMPT
)

logger = get_logger(__name__)


class ScanController:

    async def run_scan(
        self,
        front_image: bytes,
        back_image: bytes,
        front_filename: str,
        back_filename: str,
        front_content_type: str,
        back_content_type: str,
        device_id: str | None,
    ) -> Any:
        """
        Execute the full scan pipeline and return a complete ScanResult.

        Raises ImageValidationError for bad uploads (caller maps to 400).
        Raises VisionProviderError if AI extraction fails after retry (caller maps to 502).
        """

        # ── 1. Validate both images ───────────────────────────────────
        validate_image(front_filename, front_content_type, front_image)
        validate_image(back_filename, back_content_type, back_image)

        # ── 2. Compute content hash ───────────────────────────────────
        content_hash = compute_content_hash(front_image, back_image)
        logger.info("scan_started", content_hash=content_hash[:16], device_id=device_id)

        # ── 3. Cache check ────────────────────────────────────────────
        cached = await get_cached_scan(content_hash)
        if cached:
            logger.info("cache_hit_returning", scan_id=cached.get("id"))
            row_dict = scan_row_to_result(cached)
            return ScanResult.model_validate(row_dict)

        # ── 4. AI Category Detection ──────────────────────────────────
        category = await detect_category(
            front_image, back_image, front_content_type, back_content_type
        )
        logger.info("category_detected", category=category)

        scan_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        source = ScanSource.ai_extracted

        FOOD_CATEGORIES = (ProductCategory.food, ProductCategory.beverage, ProductCategory.fresh_produce)

        # ── 5a. FOOD / BEVERAGE / FRESH PRODUCE pipeline ─────────────
        if category in FOOD_CATEGORIES:
            ai_result: AIScanResult = await run_extraction(
                front_image, back_image,
                front_content_type, back_content_type,
                schema_cls=AIScanResult,
                developer_prompt=DEVELOPER_PROMPT,
            )
            # Force the category literal to match the detected value
            ai_result.category = category.value

            # Open Food Facts enrichment
            off_product = None
            off_overrides: dict = {}
            alternatives: list[AlternativeSuggestion] = []

            if ai_result.barcode:
                off_product = await lookup_by_barcode(ai_result.barcode)

            if off_product:
                off_overrides, source = merge_off_data(ai_result, off_product)
                cat_str = off_overrides.get("category") or ai_result.category
                alternatives = await search_alternatives(cat_str, limit=3)
            elif ai_result.ai_suggested_improvement:
                alternatives = [
                    AlternativeSuggestion(
                        source="ai_suggestion",
                        product_name=None,
                        reason=ai_result.ai_suggested_improvement,
                    )
                ]

            # Compute scores deterministically
            health_score, health_score_breakdown = compute_health_score(ai_result)
            ingredient_safety_score = compute_ingredient_safety_score(ai_result)

            # Assemble final ScanResult
            ai_dict = ai_result.model_dump()
            ai_dict.update(off_overrides)

            result = ScanResult(
                **ai_dict,
                scan_id=scan_id,
                created_at=created_at,
                source=source,
                health_score=health_score,
                health_score_breakdown=health_score_breakdown,
                ingredient_safety_score=ingredient_safety_score,
                alternatives=alternatives,
            )

        # ── 5b. NON-FOOD categories pipeline ─────────────────────────
        else:
            schema_map = {
                ProductCategory.medicine: (MedicineScanResult, MEDICINE_PROMPT),
                ProductCategory.cosmetic: (CosmeticScanResult, COSMETIC_PROMPT),
                ProductCategory.fertilizer: (FertilizerScanResult, FERTILIZER_PROMPT),
                ProductCategory.pesticide: (PesticideScanResult, PESTICIDE_PROMPT),
                ProductCategory.household_chemical: (HouseholdChemicalScanResult, HOUSEHOLD_CHEMICAL_PROMPT),
                ProductCategory.other: (OtherScanResult, OTHER_PROMPT),
            }
            schema_cls, dev_prompt = schema_map[category]

            # Make a relaxed version of the schema that doesn't require scan_id/created_at
            # so the AI doesn't need to fill those in
            from pydantic import BaseModel
            class AIExtractOnly(schema_cls):  # type: ignore[valid-type,misc]
                scan_id: str | None = None
                created_at: str | None = None

            ai_result_raw = await run_extraction(
                front_image, back_image,
                front_content_type, back_content_type,
                schema_cls=AIExtractOnly,
                developer_prompt=dev_prompt,
            )

            result_dict = ai_result_raw.model_dump()
            result_dict["scan_id"] = scan_id
            result_dict["created_at"] = created_at
            result_dict["source"] = source.value
            
            # Ensure proper category literal for safety
            result_dict["category"] = schema_cls.model_fields['category'].default
            
            # validate to ensure all fields are correct
            result = schema_cls.model_validate(result_dict)

        # ── 6. Persist (fire-and-forget) ──────────────────────────────
        from app.services.vision_extractor import get_vision_provider
        provider_name = get_vision_provider().name

        scan_row = build_scan_row(
            result=result,
            content_hash=content_hash,
            device_id=device_id,
            front_image_url=None,
            back_image_url=None,
            ai_provider=provider_name,
            prompt_version=PROMPT_VERSION,
        )
        asyncio.create_task(save_scan(scan_row))

        h_score = getattr(result, "health_score", None)
        logger.info(
            "scan_complete",
            scan_id=scan_id,
            source=source,
            category=category.value,
            health_score=h_score,
        )

        return result

