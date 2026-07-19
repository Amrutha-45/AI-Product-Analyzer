"""
schemas/scan_request.py
-----------------------
Pydantic model for the incoming scan request.
The actual files arrive via multipart/form-data and are handled
by FastAPI's UploadFile — this schema covers any additional
query / body parameters the request may carry.
"""

from pydantic import BaseModel, Field


class ScanRequestMeta(BaseModel):
    """Optional metadata that can accompany a scan submission."""

    device_id: str | None = Field(
        default=None,
        description="Anonymous client-generated UUID for history grouping.",
    )
