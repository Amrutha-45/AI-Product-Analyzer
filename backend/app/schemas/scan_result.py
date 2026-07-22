"""
schemas/scan_result.py
-----------------------
Pydantic models for the AI Product Analyzer scan result.

Scoring architecture (v2):
  health_score         — 0-100, computed deterministically by health_score_service.py
  ingredient_safety_score — 0-100, computed deterministically by ingredient_safety_service.py
  (trust_score removed in v2)
"""

from __future__ import annotations
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    safe = "safe"
    moderate = "moderate"
    high = "high"

class ExpiryStatus(str, Enum):
    valid = "valid"
    expired = "expired"
    unclear = "unclear"

class TextClarity(str, Enum):
    clear = "clear"
    blurry = "blurry"
    inconsistent = "inconsistent"

class OverallConfidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class ScanSource(str, Enum):
    ai_extracted = "ai_extracted"
    openfoodfacts_merged = "openfoodfacts_merged"

class NovaClass(int, Enum):
    one = 1    # Unprocessed / minimally processed
    two = 2    # Processed culinary ingredients
    three = 3  # Processed foods
    four = 4   # Ultra-processed foods


# ── Sub-models produced by the AI ─────────────────────────────────────────────

class Ingredient(BaseModel):
    name: str
    risk_level: RiskLevel
    explanation: str
    flags: list[str] = Field(default_factory=list)
    # Safety fields added in v2
    is_gras: bool = Field(
        default=True,
        description="Is this ingredient Generally Recognized As Safe (GRAS/FSSAI/EFSA/FDA approved)?"
    )
    safety_concern: str | None = Field(
        default=None,
        description="Brief safety note if not GRAS or has specific concern. Null if fully safe."
    )


class NutritionData(BaseModel):
    """Structured nutrition values per 100g, extracted by the AI from the label."""
    sugar_per_100g: float | None = None
    sodium_mg_per_100g: float | None = None
    saturated_fat_per_100g: float | None = None
    fiber_per_100g: float | None = None
    protein_per_100g: float | None = None
    caffeine_mg_per_serving: float | None = None


class ScoreBreakdownItem(BaseModel):
    """A single line in the health score breakdown."""
    label: str = Field(description="Human-readable label e.g. 'High sugar content'")
    points: int = Field(description="Points added (positive) or deducted (negative)")
    category: str = Field(description="'penalty' or 'bonus'")


class PackagingAnalysis(BaseModel):
    text_clarity: TextClarity
    barcode_present: bool
    barcode_format_valid: bool
    notable_inconsistencies: list[str] = Field(default_factory=list)


# ── AI-produced result ─────────────────────────────────────────────────────────

class AIScanResult(BaseModel):
    """
    The exact JSON shape the AI model must return.
    Validated by Pydantic before any downstream processing.
    """
    product_name: str | None = None
    brand: str | None = None
    category: str = "Food"
    barcode: str | None = None
    manufacturing_date: str | None = None
    expiry_date: str | None = None
    batch_number: str | None = None
    expiry_status: ExpiryStatus

    ingredients: list[Ingredient] = Field(default_factory=list)
    allergens: list[str] = Field(default_factory=list)

    # Structured nutrition data for algorithmic scoring
    nutrition: NutritionData = Field(default_factory=NutritionData)
    nova_class: NovaClass | None = Field(
        default=None,
        description="NOVA food processing classification: 1=unprocessed, 4=ultra-processed"
    )

    packaging_analysis: PackagingAnalysis
    warnings: list[str] = Field(default_factory=list)
    ai_suggested_improvement: str | None = None
    ai_summary: str
    overall_confidence: OverallConfidence
    confidence_reasoning: str


# ── Alternative suggestion ─────────────────────────────────────────────────────

class AlternativeSuggestion(BaseModel):
    source: str
    product_name: str | None = None
    brand: str | None = None
    reason: str
    off_id: str | None = None


# ── Final API response ─────────────────────────────────────────────────────────

class ScanResult(AIScanResult):
    """
    Complete scan result returned to the frontend.
    Scores are computed deterministically by backend services, not by the AI.
    """
    scan_id: str
    created_at: str
    source: ScanSource = ScanSource.ai_extracted

    # v2 scores — computed by backend services
    health_score: int = Field(
        ge=0, le=100,
        description="0-100 nutritional quality score computed by health_score_service"
    )
    health_score_breakdown: list[ScoreBreakdownItem] = Field(
        default_factory=list,
        description="Transparent breakdown of health score additions and deductions"
    )
    ingredient_safety_score: int = Field(
        ge=0, le=100,
        description="0-100 ingredient safety score based on GRAS/FSSAI/EFSA/FDA approval status"
    )

    alternatives: list[AlternativeSuggestion] = Field(default_factory=list)


class ScanSummary(BaseModel):
    scan_id: str
    product_name: str | None
    brand: str | None
    health_score: int
    ingredient_safety_score: int
    source: ScanSource
    created_at: str
