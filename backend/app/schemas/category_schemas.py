"""
schemas/category_schemas.py
-----------------------------
Pydantic models for category-aware product analysis.
Non-food categories are defined here.
Food/Beverage results still use ScanResult from scan_result.py.
"""
import enum
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class ProductCategory(str, enum.Enum):
    food = "Food"
    beverage = "Beverage"
    fresh_produce = "Fresh Produce"
    medicine = "Medicine"
    cosmetic = "Cosmetic"
    fertilizer = "Fertilizer"
    pesticide = "Pesticide"
    household_chemical = "Household Chemical"
    other = "Other"


class CategoryDetectionResult(BaseModel):
    category: ProductCategory


class MedicineScanResult(BaseModel):
    category: str = "Medicine"
    scan_id: str
    created_at: str
    source: str = "ai_extracted"
    product_name: Optional[str] = None
    medicine_type: Optional[str] = None
    active_ingredients: List[str] = Field(default_factory=list)
    intended_use: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    storage_instructions: Optional[str] = None
    is_prescription: Optional[bool] = None
    safety_notes: Optional[str] = None
    ai_summary: str = ""
    overall_confidence: str = "medium"


class CosmeticIngredient(BaseModel):
    name: str
    is_safe: bool
    explanation: str


class CosmeticScanResult(BaseModel):
    category: str = "Cosmetic"
    scan_id: str
    created_at: str
    source: str = "ai_extracted"
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    key_ingredients: List[CosmeticIngredient] = Field(default_factory=list)
    allergens: List[str] = Field(default_factory=list)
    has_artificial_fragrance: bool = False
    preservatives: List[str] = Field(default_factory=list)
    skin_suitability: Optional[str] = None
    usage_precautions: List[str] = Field(default_factory=list)
    ai_summary: str = ""
    overall_confidence: str = "medium"


class FertilizerScanResult(BaseModel):
    category: str = "Fertilizer"
    scan_id: str
    created_at: str
    source: str = "ai_extracted"
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    chemical_safety_score: int = Field(default=50, ge=0, le=100)
    npk_composition: Optional[str] = None
    chemical_components: List[str] = Field(default_factory=list)
    intended_agricultural_use: Optional[str] = None
    hazard_warnings: List[str] = Field(default_factory=list)
    ppe_recommendations: List[str] = Field(default_factory=list)
    storage_instructions: Optional[str] = None
    environmental_precautions: List[str] = Field(default_factory=list)
    ai_summary: str = ""
    overall_confidence: str = "medium"


class PesticideScanResult(BaseModel):
    category: str = "Pesticide"
    scan_id: str
    created_at: str
    source: str = "ai_extracted"
    product_name: Optional[str] = None
    chemical_safety_score: int = Field(default=30, ge=0, le=100)
    active_ingredients: List[str] = Field(default_factory=list)
    hazard_classification: Optional[str] = None
    toxicity_level: Optional[str] = None
    ppe_recommendations: List[str] = Field(default_factory=list)
    safe_handling: List[str] = Field(default_factory=list)
    storage_instructions: Optional[str] = None
    disposal_guidance: Optional[str] = None
    environmental_risk: Optional[str] = None
    ai_summary: str = ""
    overall_confidence: str = "medium"


class HouseholdChemicalScanResult(BaseModel):
    category: str = "Household Chemical"
    scan_id: str
    created_at: str
    source: str = "ai_extracted"
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    chemical_safety_score: int = Field(default=50, ge=0, le=100)
    hazard_warnings: List[str] = Field(default_factory=list)
    storage_instructions: Optional[str] = None
    child_safety_advice: Optional[str] = None
    ppe_recommendations: List[str] = Field(default_factory=list)
    first_aid_information: Optional[str] = None
    ai_summary: str = ""
    overall_confidence: str = "medium"


class OtherScanResult(BaseModel):
    category: str = "Other"
    scan_id: str
    created_at: str
    source: str = "ai_extracted"
    product_name: Optional[str] = None
    detected_type: Optional[str] = None
    ai_summary: str = ""
    extracted_text: str = ""
    overall_confidence: str = "medium"
