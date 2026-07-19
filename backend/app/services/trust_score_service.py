"""
services/trust_score_service.py
---------------------------------
Computes a deterministic trust score (0–100) from the packaging signals
returned by the AI.  This is arithmetic, not an AI call — the number
is explainable and reproducible.

Formula (max 100 points):
  ┌─────────────────────────────────────────────┬────────┐
  │ Signal                                      │ Points │
  ├─────────────────────────────────────────────┼────────┤
  │ text_clarity = "clear"                      │  40    │
  │ text_clarity = "inconsistent"               │  20    │
  │ text_clarity = "blurry"                     │   0    │
  ├─────────────────────────────────────────────┼────────┤
  │ barcode_present = true                      │  30    │
  │ barcode_format_valid = true (requires above)│  20    │
  ├─────────────────────────────────────────────┼────────┤
  │ notable_inconsistencies deduction           │  -10   │
  │   per observed inconsistency (max -20)      │  each  │
  └─────────────────────────────────────────────┴────────┘

Total is clamped to [0, 100].

Rationale for each weight:
  - text_clarity carries the most weight (40 pts) because illegible text
    is the single biggest signal that a label might be reprinted/tampered.
  - barcode_present (30 pts) + format_valid (20 pts) together reward
    products that have a standard, well-formed barcode — missing or
    malformed barcodes are a meaningful anomaly signal.
  - inconsistencies are penalised additively, capped at -20 so a product
    with multiple minor observations doesn't drop to zero on what might
    still be a legitimate but low-quality print run.
"""

from app.schemas.scan_result import PackagingAnalysis, TextClarity
from app.utils.logging import get_logger

logger = get_logger(__name__)

# ── Scoring weights ────────────────────────────────────────────────────────────
_CLARITY_SCORES = {
    TextClarity.clear: 40,
    TextClarity.inconsistent: 20,
    TextClarity.blurry: 0,
}
_BARCODE_PRESENT_SCORE = 30
_BARCODE_FORMAT_SCORE = 20
_INCONSISTENCY_PENALTY = 10
_MAX_INCONSISTENCY_PENALTY = 20


def compute_trust_score(packaging: PackagingAnalysis) -> float:
    """
    Return a trust score in [0.0, 100.0] computed from packaging_analysis signals.

    Parameters
    ----------
    packaging  The PackagingAnalysis object produced by the AI.

    Returns
    -------
    float  The computed trust score, clamped to [0.0, 100.0].
    """
    score = 0.0

    # ── text_clarity ──────────────────────────────────────────────────
    score += _CLARITY_SCORES.get(packaging.text_clarity, 0)

    # ── barcode signals ───────────────────────────────────────────────
    if packaging.barcode_present:
        score += _BARCODE_PRESENT_SCORE
        if packaging.barcode_format_valid:
            score += _BARCODE_FORMAT_SCORE

    # ── inconsistency deductions ──────────────────────────────────────
    num_inconsistencies = len(packaging.notable_inconsistencies)
    penalty = min(num_inconsistencies * _INCONSISTENCY_PENALTY, _MAX_INCONSISTENCY_PENALTY)
    score -= penalty

    final_score = max(0.0, min(100.0, score))

    logger.debug(
        "trust_score_computed",
        clarity=packaging.text_clarity,
        barcode_present=packaging.barcode_present,
        barcode_valid=packaging.barcode_format_valid,
        inconsistencies=num_inconsistencies,
        final_score=final_score,
    )

    return round(final_score, 2)
