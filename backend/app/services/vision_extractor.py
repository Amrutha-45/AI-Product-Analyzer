"""
services/vision_extractor.py
-----------------------------
Provider factory and retry orchestration.

get_vision_provider() returns the configured VisionProvider implementation.
run_extraction()      handles the single-retry-on-failure logic:
  - Call the provider.
  - If the call raises VisionProviderError (retryable), retry once with
    the specific Pydantic validation error appended to the developer prompt.
  - If the retry also fails, re-raise so the controller can surface a 502.

Per the spec: "an unbounded retry loop risks masking a genuinely broken
prompt/image pair and burning API budget" — exactly one retry, no more.
"""

from app.core.config import get_settings
from app.prompts.extraction_prompt import build_retry_prompt
from app.schemas.scan_result import AIScanResult
from app.schemas.category_schemas import ProductCategory
from app.services.vision_providers.base import VisionProvider, VisionProviderError
from app.utils.logging import get_logger

logger = get_logger(__name__)


def get_vision_provider() -> VisionProvider:
    """
    Factory: returns the VisionProvider implementation selected in config.
    Defaults to GeminiProvider. Add new providers here as they're built.
    """
    settings = get_settings()
    provider_name = settings.ai_provider.lower()

    if provider_name == "gemini":
        from app.services.vision_providers.gemini_provider import GeminiProvider
        return GeminiProvider()
        
    if provider_name == "groq":
        from app.services.vision_providers.groq_provider import GroqProvider
        return GroqProvider()

    # Stub for future providers (e.g. OpenAI GPT-4 Vision)
    raise ValueError(f"Unsupported AI provider: '{provider_name}'. Check AI_PROVIDER in .env")


async def run_extraction(
    front_image: bytes,
    back_image: bytes,
    front_mime: str,
    back_mime: str,
    schema_cls: type = AIScanResult,
    developer_prompt: str | None = None,
) -> any:
    """
    Run the AI extraction pipeline with exactly one retry on failure.

    Returns a validated AIScanResult on success.
    Raises VisionProviderError if both the initial call and the single
    retry fail — caller should convert this to a 502 response.
    """
    provider = get_vision_provider()

    # ── First attempt ─────────────────────────────────────────────────
    try:
        logger.info("extraction_attempt", attempt=1, provider=provider.name)
        return await provider.extract(
            front_image, back_image, front_mime, back_mime,
            schema_cls=schema_cls, developer_prompt=developer_prompt
        )
    except VisionProviderError as exc:
        if not exc.retryable:
            raise

        logger.warning(
            "extraction_attempt_failed",
            attempt=1,
            error=str(exc),
            retrying=True,
        )
        first_error = str(exc)

    # ── Single retry with corrective prompt ───────────────────────────
    try:
        logger.info("extraction_attempt", attempt=2, provider=provider.name)
        corrective_prompt = build_retry_prompt(first_error)
        return await provider.extract(
            front_image,
            back_image,
            front_mime,
            back_mime,
            retry_prompt=corrective_prompt,
            schema_cls=schema_cls,
            developer_prompt=developer_prompt,
        )
    except VisionProviderError as exc:
        logger.error(
            "extraction_failed_after_retry",
            error=str(exc),
        )
        raise

async def detect_category(
    front_image: bytes,
    back_image: bytes,
    front_mime: str,
    back_mime: str,
) -> ProductCategory:
    """Run lightweight category detection before full extraction."""
    provider = get_vision_provider()
    # If the provider implements detect_category, call it. Otherwise default to food.
    if hasattr(provider, 'detect_category'):
        return await provider.detect_category(front_image, back_image, front_mime, back_mime)
    return ProductCategory.food
