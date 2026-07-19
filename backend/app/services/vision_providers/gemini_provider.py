"""
services/vision_providers/gemini_provider.py
---------------------------------------------
Concrete VisionProvider using the google-genai REST SDK.
Uses HTTPS (not gRPC) so it's faster and more reliable on restricted networks.
"""

import json
import asyncio
from google import genai
from google.genai import types
from pydantic import ValidationError

from app.core.config import get_settings
from app.prompts.extraction_prompt import SYSTEM_PROMPT, DEVELOPER_PROMPT
from app.prompts.category_prompts import DETECT_CATEGORY_PROMPT
from app.schemas.scan_result import AIScanResult
from app.schemas.category_schemas import CategoryDetectionResult, ProductCategory
from app.services.vision_providers.base import VisionProvider, VisionProviderError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class GeminiProvider(VisionProvider):
    """Google Gemini 2.5 Flash multimodal vision provider (REST/HTTPS)."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise VisionProviderError(
                "GEMINI_API_KEY is not set. Check your .env file.",
                retryable=False,
            )
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model_name = settings.ai_model
        self._temperature = settings.ai_temperature
        self._timeout = settings.ai_timeout_seconds

    @property
    def name(self) -> str:
        return self._model_name

    async def extract(
        self,
        front_image: bytes,
        back_image: bytes,
        front_mime: str,
        back_mime: str,
        *,
        retry_prompt: str | None = None,
        schema_cls: type = AIScanResult,
        developer_prompt: str | None = None,
    ) -> any:
        """
        Send both product images to Gemini via REST and return a validated result.
        """
        final_prompt = retry_prompt or developer_prompt or DEVELOPER_PROMPT

        contents = [
            SYSTEM_PROMPT,
            types.Part.from_bytes(data=front_image, mime_type=front_mime),
            types.Part.from_bytes(data=back_image, mime_type=back_mime),
            final_prompt,
        ]

        config = types.GenerateContentConfig(
            temperature=self._temperature,
            response_mime_type="application/json",
        )

        try:
            logger.info("gemini_call_start", model=self._model_name, is_retry=retry_prompt is not None)

            # Use async REST call — no gRPC, no blocked ports
            response = await self._client.aio.models.generate_content(
                model=self._model_name,
                contents=contents,
                config=config,
            )

            raw_text = response.text

        except Exception as exc:
            logger.error("gemini_api_error", error=str(exc))
            raise VisionProviderError(
                f"Gemini API call failed: {exc}",
                retryable=True,
            ) from exc

        # ── Parse JSON ────────────────────────────────────────────────
        if not raw_text or not raw_text.strip():
            raise VisionProviderError(
                "Gemini returned an empty response.",
                retryable=True,
            )

        try:
            parsed_json = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise VisionProviderError(
                f"Gemini response was not valid JSON: {exc}",
                retryable=True,
            ) from exc

        # ── Validate against schema ────────────────────────────────────
        try:
            result = schema_cls.model_validate(parsed_json)
        except ValidationError as exc:
            raise VisionProviderError(
                f"Gemini response did not match the expected schema: {exc}",
                retryable=True,
            ) from exc

        logger.info(
            "gemini_call_success",
            product_name=getattr(result, "product_name", "Unknown"),
            confidence=getattr(result, "overall_confidence", "unknown"),
        )

        return result

    async def detect_category(
        self,
        front_image: bytes,
        back_image: bytes,
        front_mime: str,
        back_mime: str,
    ) -> ProductCategory:
        """
        Lightweight fast call to detect category.
        """
        contents = [
            SYSTEM_PROMPT,
            types.Part.from_bytes(data=front_image, mime_type=front_mime),
            types.Part.from_bytes(data=back_image, mime_type=back_mime),
            DETECT_CATEGORY_PROMPT,
        ]
        
        config = types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=CategoryDetectionResult,
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model_name,
                contents=contents,
                config=config,
            )
            raw_text = response.text
            logger.info("raw_category_detection", text=raw_text)
            parsed_json = json.loads(raw_text)
            result = CategoryDetectionResult.model_validate(parsed_json)
            return result.category
        except Exception as exc:
            logger.error("category_detection_failed", error=str(exc))
            # Fallback to Food if detection fails
            return ProductCategory.food
