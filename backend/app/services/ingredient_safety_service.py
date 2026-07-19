"""
services/ingredient_safety_service.py
--------------------------------------
Deterministic Ingredient Safety Score (0-100).

Measures whether ingredients are generally recognized as safe (GRAS/FSSAI/EFSA/FDA)
when consumed within recommended limits.

Does NOT measure nutritional quality (that is the Health Score's job).

Algorithm:
  Start at 100.
  For each ingredient where is_gras=False: -15 pts (max 3 applied)
  For each ingredient with risk_level=high: -8 pts (max 3 applied)
  For each ingredient with risk_level=moderate: -3 pts (max 5 applied)
  Clamp to [0, 100].
"""

from app.schemas.scan_result import AIScanResult
from app.utils.logging import get_logger

logger = get_logger(__name__)


def compute_ingredient_safety_score(ai: AIScanResult) -> int:
    """
    Returns ingredient_safety_score in [0, 100].
    """
    score = 100

    not_gras = [i for i in ai.ingredients if not i.is_gras]
    applied = min(len(not_gras), 3)
    score -= applied * 15

    high_risk = [i for i in ai.ingredients if i.risk_level.value == "high"]
    applied = min(len(high_risk), 3)
    score -= applied * 8

    moderate_risk = [i for i in ai.ingredients if i.risk_level.value == "moderate"]
    applied = min(len(moderate_risk), 5)
    score -= applied * 3

    final = max(0, min(100, score))

    logger.debug("ingredient_safety_score_computed", final=final)
    return final
