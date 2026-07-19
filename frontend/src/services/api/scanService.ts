// In Vite, environment variables are exposed on import.meta.env
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ScoreBreakdownItem {
  label: string;
  points: number;
  category: 'penalty' | 'bonus';
}

export interface BaseScanResult {
  scan_id: string;
  created_at: string;
  source: string;
  product_name: string | null;
  overall_confidence: string;
  ai_summary: string;
}

export interface FoodScanResult extends BaseScanResult {
  category: 'Food' | 'Beverage' | 'Fresh Produce';
  brand: string | null;
  barcode: string | null;
  manufacturing_date: string | null;
  expiry_date: string | null;
  batch_number: string | null;
  expiry_status: string;
  ingredients: Array<{
    name: string;
    risk_level: string;
    explanation: string;
    flags: string[];
    is_gras: boolean;
    safety_concern: string | null;
  }>;
  allergens: string[];
  nutrition: {
    sugar_per_100g: number | null;
    sodium_mg_per_100g: number | null;
    saturated_fat_per_100g: number | null;
    fiber_per_100g: number | null;
    protein_per_100g: number | null;
    caffeine_mg_per_serving: number | null;
  };
  nova_class: number | null;
  packaging_analysis: {
    text_clarity: string;
    barcode_present: boolean;
    barcode_format_valid: boolean | null;
    notable_inconsistencies: string[];
  };
  warnings: string[];
  ai_suggested_improvement: string | null;
  confidence_reasoning: string;
  health_score: number;
  health_score_breakdown: ScoreBreakdownItem[];
  ingredient_safety_score: number;
  alternatives: Array<{
    source: string;
    product_name: string | null;
    brand: string | null;
    reason: string;
  }>;
}

export interface MedicineScanResult extends BaseScanResult {
  category: 'Medicine';
  medicine_type: string | null;
  active_ingredients: string[];
  intended_use: string | null;
  warnings: string[];
  storage_instructions: string | null;
  is_prescription: boolean | null;
  safety_notes: string | null;
}

export interface CosmeticScanResult extends BaseScanResult {
  category: 'Cosmetic';
  product_type: string | null;
  key_ingredients: Array<{
    name: string;
    is_safe: boolean;
    explanation: string;
  }>;
  allergens: string[];
  has_artificial_fragrance: boolean;
  preservatives: string[];
  skin_suitability: string | null;
  usage_precautions: string[];
}

export interface FertilizerScanResult extends BaseScanResult {
  category: 'Fertilizer';
  product_type: string | null;
  chemical_safety_score: number;
  npk_composition: string | null;
  chemical_components: string[];
  intended_agricultural_use: string | null;
  hazard_warnings: string[];
  ppe_recommendations: string[];
  storage_instructions: string | null;
  environmental_precautions: string[];
}

export interface PesticideScanResult extends BaseScanResult {
  category: 'Pesticide';
  chemical_safety_score: number;
  active_ingredients: string[];
  hazard_classification: string | null;
  toxicity_level: string | null;
  ppe_recommendations: string[];
  safe_handling: string[];
  storage_instructions: string | null;
  disposal_guidance: string | null;
  environmental_risk: string | null;
}

export interface HouseholdChemicalScanResult extends BaseScanResult {
  category: 'Household Chemical';
  product_type: string | null;
  chemical_safety_score: number;
  hazard_warnings: string[];
  storage_instructions: string | null;
  child_safety_advice: string | null;
  ppe_recommendations: string[];
  first_aid_information: string | null;
}

export interface OtherScanResult extends BaseScanResult {
  category: 'Other';
  detected_type: string | null;
  extracted_text: string;
}

export type ScanResult = 
  | FoodScanResult 
  | MedicineScanResult 
  | CosmeticScanResult 
  | FertilizerScanResult 
  | PesticideScanResult 
  | HouseholdChemicalScanResult 
  | OtherScanResult;

export const scanService = {
  async submitScan(frontImage: File, backImage: File): Promise<ScanResult> {
    const formData = new FormData();
    formData.append('front_image', frontImage);
    formData.append('back_image', backImage);

    const response = await fetch(`${API_BASE_URL}/scan`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to analyze product');
    }

    return response.json();
  },

  async getScan(id: string): Promise<ScanResult> {
    const response = await fetch(`${API_BASE_URL}/scans/${id}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch scan results');
    }

    return response.json();
  }
};
