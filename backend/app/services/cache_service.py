"""
services/cache_service.py
--------------------------
Content-hash based scan cache backed by Supabase (PostgreSQL).

The cache check happens BEFORE any AI call so identical images are
never re-billed. A hash miss proceeds to the AI pipeline; a hit
returns the persisted ScanResult instantly.

This also avoids the performance hit of a second DB write on a cache
hit — we just return the existing row.
"""

from typing import Any
from app.db.supabase_client import get_supabase
from app.utils.logging import get_logger

logger = get_logger(__name__)

TABLE = "scans"


async def get_cached_scan(content_hash: str) -> dict[str, Any] | None:
    """
    Look up a previously completed scan by content hash.
    Returns the raw Supabase row dict on a cache hit, or None on a miss.
    """
    try:
        client = get_supabase()
        result = (
            client.table(TABLE)
            .select("*")
            .eq("content_hash", content_hash)
            .limit(1)
            .execute()
        )
        if result.data:
            logger.info("cache_hit", content_hash=content_hash[:16])
            return result.data[0]
        logger.debug("cache_miss", content_hash=content_hash[:16])
        return None
    except Exception as exc:
        # Cache failures are non-fatal — log and proceed to AI call
        logger.warning("cache_lookup_error", error=str(exc))
        return None


async def save_scan(scan_row: dict[str, Any]) -> None:
    """
    Persist a completed scan to the database.
    Called fire-and-forget — failures are logged but do not block
    the response being returned to the client.
    """
    try:
        client = get_supabase()
        client.table(TABLE).insert(scan_row).execute()
        logger.info("scan_persisted", scan_id=scan_row.get("id"))
    except Exception as exc:
        logger.error("scan_persist_error", error=str(exc), scan_id=scan_row.get("id"))
