"""
routes/scan.py
---------------
POST /scan   — submit front + back product images for analysis
GET  /scans/{scan_id} — retrieve a previously completed scan

HTTP layer only: parse the request, delegate to the controller,
return the response.  No business logic lives here.
"""

from fastapi import APIRouter, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from app.controllers.scan_controller import ScanController
from app.core.config import get_settings
from app.db.supabase_client import get_supabase
from app.middleware.rate_limit import limiter
from app.models.scan import scan_row_to_result
from app.utils.image_validation import ImageValidationError
from app.services.vision_providers.base import VisionProviderError
from app.utils.logging import get_logger

router = APIRouter(tags=["Scan"])
logger = get_logger(__name__)
controller = ScanController()


@router.post(
    "/scan",
    summary="Analyze a product from front + back label images",
    responses={
        400: {"description": "Missing or invalid image files"},
        413: {"description": "File exceeds size limit"},
        429: {"description": "Rate limit exceeded"},
        502: {"description": "AI provider failure"},
        504: {"description": "AI provider timeout"},
    },
)
@limiter.limit("10/hour")
async def submit_scan(
    request: Request,                       # required by slowapi
    front_image: UploadFile = File(..., description="Front label of the product (JPEG/PNG/WEBP, max 8MB)"),
    back_image: UploadFile = File(..., description="Back label of the product (JPEG/PNG/WEBP, max 8MB)"),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
):
    """
    Submit front and back product images for AI-powered analysis.

    Returns a complete ScanResult including:
    - Ingredient breakdown with risk levels
    - Health score (0–10) with reasoning
    - Packaging trust score (0–100, deterministic)
    - Expiry status
    - Healthier alternatives (data-backed when available)
    - AI summary in plain language
    """

    # Read file bytes
    try:
        front_bytes = await front_image.read()
        back_bytes = await back_image.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Failed to read uploaded files.")

    # Delegate to controller
    try:
        result = await controller.run_scan(
            front_image=front_bytes,
            back_image=back_bytes,
            front_filename=front_image.filename or "front.jpg",
            back_filename=back_image.filename or "back.jpg",
            front_content_type=front_image.content_type or "image/jpeg",
            back_content_type=back_image.content_type or "image/jpeg",
            device_id=x_device_id,
        )
        return result

    except ImageValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except VisionProviderError as exc:
        settings = get_settings()
        status = 504 if "timeout" in str(exc).lower() else 502
        # In development: always expose the real error so we can debug
        # In production: show a safe generic message
        if settings.is_production:
            message = (
                "Analysis is taking longer than expected. Please try again."
                if status == 504
                else "We couldn't analyze this product image. Please try a clearer photo."
            )
        else:
            message = f"[DEV] VisionProviderError ({status}): {str(exc)}"
        raise HTTPException(status_code=status, detail=message)
    except Exception as exc:
        logger.error("scan_route_error", error=str(exc), exc_info=True)
        settings = get_settings()
        detail = f"[DEV] Unexpected error: {str(exc)}" if not settings.is_production else "An unexpected error occurred."
        raise HTTPException(status_code=500, detail=detail)


@router.get(
    "/scans/{scan_id}",
    summary="Retrieve a previously completed scan",
    responses={404: {"description": "Scan not found"}},
)
async def get_scan(scan_id: str):
    """
    Retrieve a previously completed scan by its ID.
    Used for polling after a long scan or for sharing results.
    """
    try:
        client = get_supabase()
        result = (
            client.table("scans")
            .select("*")
            .eq("id", scan_id)
            .limit(1)
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Scan not found.")

        row_dict = scan_row_to_result(result.data[0])
        return row_dict

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_scan_error", error=str(exc), scan_id=scan_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve scan.")
