"""
services/health_score_service.py
---------------------------------
Deterministic Health Score (0-100) algorithm.

Scores nutritional quality — NOT ingredient safety.

Penalties:
  High sugar (>20g/100g)        -25 pts
  High sugar (>10g/100g)        -15 pts
  High sodium (>600mg/100g)     -20 pts
  High sodium (>300mg/100g)     -10 pts
  High saturated fat (>5g/100g) -15 pts
  Artificial colors present     -10 pts
  Artificial sweeteners present  -8 pts
  Preservatives present          -5 pts
  High caffeine (>150mg/serving) -15 pts
  NOVA class 4 (ultra-processed) -20 pts
  NOVA class 3 (processed)       -10 pts
  ingredient risk_level=high     -5 pts each (max -15)

Bonuses:
  High fiber (>5g/100g)         +10 pts
  Good protein (>10g/100g)       +8 pts
  NOVA class 1 (unprocessed)    +10 pts
  NOVA class 2                   +5 pts
  No flagged ingredients          +5 pts

Base score: 70. Final clamped to [0, 100].
"""

from app.schemas.scan_result import AIScanResult, ScoreBreakdownItem, NovaClass
from app.utils.logging import get_logger

logger = get_logger(__name__)

BASE_SCORE = 70


def compute_health_score(ai: AIScanResult) -> tuple[int, list[ScoreBreakdownItem]]:
    """
    Returns (health_score, breakdown_items).
    health_score is clamped to [0, 100].
    """
    score = BASE_SCORE
    breakdown: list[ScoreBreakdownItem] = []

    def add(label: str, points: int, category: str = None):
        nonlocal score
        score += points
        cat = category or ("bonus" if points > 0 else "penalty")
        breakdown.append(ScoreBreakdownItem(label=label, points=points, category=cat))

    n = ai.nutrition
    all_flags = [f for ing in ai.ingredients for f in ing.flags]

    # ── Sugar ─────────────────────────────────────────────────────────
    sugar_penalized = False
    if n.sugar_per_100g is not None:
        if n.sugar_per_100g > 20:
            add(f"Very high sugar ({n.sugar_per_100g:.1f}g/100g)", -25)
            sugar_penalized = True
        elif n.sugar_per_100g > 10:
            add(f"High sugar ({n.sugar_per_100g:.1f}g/100g)", -15)
            sugar_penalized = True
            
    if not sugar_penalized and "high_sugar" in all_flags:
        add("High sugar (flagged)", -15)

    # ── Sodium ────────────────────────────────────────────────────────
    sodium_penalized = False
    if n.sodium_mg_per_100g is not None:
        if n.sodium_mg_per_100g > 600:
            add(f"Very high sodium ({n.sodium_mg_per_100g:.0f}mg/100g)", -20)
            sodium_penalized = True
        elif n.sodium_mg_per_100g > 300:
            add(f"High sodium ({n.sodium_mg_per_100g:.0f}mg/100g)", -10)
            sodium_penalized = True

    if not sodium_penalized and "high_sodium" in all_flags:
        add("High sodium (flagged)", -10)

    # ── Saturated fat ─────────────────────────────────────────────────
    sat_fat_penalized = False
    if n.saturated_fat_per_100g is not None:
        if n.saturated_fat_per_100g > 5:
            add(f"High saturated fat ({n.saturated_fat_per_100g:.1f}g/100g)", -15)
            sat_fat_penalized = True

    if not sat_fat_penalized and "high_saturated_fat" in all_flags:
        add("High saturated fat (flagged)", -15)

    # ── Caffeine ──────────────────────────────────────────────────────
    caffeine_penalized = False
    if n.caffeine_mg_per_serving is not None and n.caffeine_mg_per_serving > 150:
        add(f"High caffeine ({n.caffeine_mg_per_serving:.0f}mg/serving)", -15)
        caffeine_penalized = True

    if not caffeine_penalized and "high_caffeine" in all_flags:
        add("High caffeine (flagged)", -15)

    # ── Ingredient flags ──────────────────────────────────────────────
    if "artificial_color" in all_flags:
        add("Artificial colors present", -10)
    if "artificial_sweetener" in all_flags:
        add("Artificial sweeteners present", -8)
    if "preservative" in all_flags:
        add("Preservatives present", -5)

    # Penalize high-risk ingredients (up to 3)
    high_risk = [i for i in ai.ingredients if i.risk_level.value == "high"]
    if high_risk:
        penalty = min(len(high_risk), 3) * -5
        names = ", ".join(i.name for i in high_risk[:3])
        add(f"High-risk ingredients: {names}", penalty)

    # ── NOVA classification ───────────────────────────────────────────
    if ai.nova_class == NovaClass.four:
        add("Ultra-processed food (NOVA class 4)", -20)
    elif ai.nova_class == NovaClass.three:
        add("Processed food (NOVA class 3)", -10)
    elif ai.nova_class == NovaClass.two:
        add("Minimally processed (NOVA class 2)", +5)
    elif ai.nova_class == NovaClass.one:
        add("Whole / unprocessed food (NOVA class 1)", +10)

    # ── Fiber ─────────────────────────────────────────────────────────
    if n.fiber_per_100g is not None and n.fiber_per_100g >= 5:
        add(f"Good fiber content ({n.fiber_per_100g:.1f}g/100g)", +10)

    # ── Protein ───────────────────────────────────────────────────────
    if n.protein_per_100g is not None and n.protein_per_100g >= 10:
        add(f"Good protein content ({n.protein_per_100g:.1f}g/100g)", +8)

    # ── Clean ingredient bonus ────────────────────────────────────────
    bad_flags = {"artificial_color", "artificial_sweetener", "preservative", "high_sugar", "high_sodium"}
    has_bad_flag = any(f in bad_flags for f in all_flags)
    if not has_bad_flag and len(ai.ingredients) > 0:
        add("No major ingredient concerns", +5)

    final = max(0, min(100, score))

    logger.debug(
        "health_score_computed",
        base=BASE_SCORE,
        adjustments=len(breakdown),
        final=final,
        nova=ai.nova_class,
    )

    return final, breakdown
