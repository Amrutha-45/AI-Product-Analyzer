"""
routes/history.py
------------------
GET /scans — anonymous scan history scoped to the requesting device.

Requires X-Device-Id header for grouping. Returns a paginated list of
past scan summaries for that device (no cross-device data leakage).
"""

from fastapi import APIRouter, Header, HTTPException, Query
from app.db.supabase_client import get_supabase
from app.schemas.scan_result import ScanSummary
from app.utils.logging import get_logger

router = APIRouter(tags=["History"])
logger = get_logger(__name__)


@router.get(
    "/scans",
    response_model=dict,
    summary="Get scan history for the current device",
)
async def get_scan_history(
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
):
    """
    Returns paginated scan history for the provided device ID.
    Scoped strictly to the requesting device — no cross-device access.
    """
    if not x_device_id:
        raise HTTPException(
            status_code=400,
            detail="X-Device-Id header is required to retrieve scan history.",
        )

    try:
        client = get_supabase()
        result = (
            client.table("scans")
            .select("id, product_name, brand, health_score, ingredient_safety_score, source, created_at")
            .eq("device_id", x_device_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        # Total count for pagination
        count_result = (
            client.table("scans")
            .select("id", count="exact")
            .eq("device_id", x_device_id)
            .execute()
        )
        total = count_result.count or 0

        # Map DB rows to ScanSummary
        summaries = [
            ScanSummary(
                scan_id=str(row["id"]),
                product_name=row.get("product_name"),
                brand=row.get("brand"),
                health_score=row.get("health_score", 0),
                ingredient_safety_score=row.get("ingredient_safety_score", 0),
                source=row.get("source", "ai_extracted"),
                created_at=str(row.get("created_at", "")),
            )
            for row in result.data
        ]

        return {
            "results": [s.model_dump() for s in summaries],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("history_fetch_error", error=str(exc), device_id=x_device_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve scan history.")
