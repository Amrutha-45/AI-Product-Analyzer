"""
routes/health.py
-----------------
GET /health — uptime check endpoint.
Used by deployment platforms to confirm the server is alive.
Useful during a live demo to prove the deployment is running.
"""

from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check")
async def health_check():
    """Returns server status and version. Use to verify the deployment is live."""
    settings = get_settings()
    return {"status": "ok", "version": settings.app_version}
