"""
middleware/error_handler.py
-----------------------------
Global exception handlers that convert any unhandled exception into a
clean JSON error response with a consistent { "detail": "..." } shape.

Having one global handler means:
  - Every route returns errors in the same JSON shape
  - The frontend's error-toast logic can depend on this being consistent
  - No route needs its own try/except for unexpected errors
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.services.vision_providers.base import VisionProviderError
from app.utils.logging import get_logger

logger = get_logger(__name__)


def setup_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        logger.warning("rate_limit_exceeded", client_ip=request.client.host if request.client else "unknown")
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many scans. Please wait a moment and try again."},
        )

    @app.exception_handler(VisionProviderError)
    async def vision_provider_error_handler(request: Request, exc: VisionProviderError):
        logger.error("vision_provider_error", error=str(exc))
        return JSONResponse(
            status_code=502,
            content={"detail": "We couldn't analyze this product image. Please try a clearer photo."},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", error=str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again."},
        )
