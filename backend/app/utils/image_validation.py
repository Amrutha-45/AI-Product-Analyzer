"""
utils/image_validation.py
--------------------------
Validates uploaded image files before they ever reach the AI pipeline.
Failing early here is cheaper (no API cost, lower latency) than letting
the model try to extract from an unreadable image.

Checks:
  1. MIME type (must be jpeg/png/webp)
  2. File size (must be ≤ MAX_IMAGE_SIZE_MB)
  3. Minimum dimension (must be ≥ MIN_IMAGE_DIMENSION on both axes)
"""

from io import BytesIO
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class ImageValidationError(ValueError):
    """Raised when an uploaded file fails any validation check."""


def validate_image(filename: str, content_type: str, data: bytes) -> None:
    """
    Run all validation checks on a single uploaded image.
    Raises ImageValidationError with a user-facing message on failure.
    """
    settings = get_settings()

    # ── 1. MIME type check ────────────────────────────────────────────
    if content_type not in ALLOWED_MIME_TYPES:
        raise ImageValidationError(
            f"Unsupported file type '{content_type}'. "
            "Please upload a JPG, PNG, or WEBP image."
        )

    # ── 2. File size check ────────────────────────────────────────────
    size_bytes = len(data)
    if size_bytes > settings.max_image_size_bytes:
        raise ImageValidationError(
            f"Image '{filename}' exceeds the {settings.max_image_size_mb}MB limit. "
            "Try a smaller or compressed photo."
        )

    # ── 3. Minimum dimension check ────────────────────────────────────
    try:
        with Image.open(BytesIO(data)) as img:
            width, height = img.size
    except UnidentifiedImageError:
        raise ImageValidationError(
            f"'{filename}' could not be read as an image. "
            "Please upload a valid JPG, PNG, or WEBP file."
        )

    min_dim = settings.min_image_dimension
    if width < min_dim or height < min_dim:
        raise ImageValidationError(
            f"Image '{filename}' is too small ({width}×{height}px). "
            f"Please upload an image of at least {min_dim}×{min_dim}px "
            "so the AI can read the label clearly."
        )

    logger.debug(
        "image_validated",
        filename=filename,
        size_bytes=size_bytes,
        dimensions=f"{width}x{height}",
    )
