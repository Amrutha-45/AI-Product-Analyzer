"""
services/vision_providers/openrouter_provider.py
------------------------------------------------
Concrete VisionProvider using the OpenRouter API.
Leverages the openai python SDK to send multimodal requests.
"""

import json
import base64
from typing import Any
from openai import AsyncOpenAI
from pydantic import ValidationError

from app.core.config import get_settings
from app.prompts.extraction_prompt import SYSTEM_PROMPT, DEVELOPER_PROMPT
from app.schemas.scan_result import AIScanResult
from app.services.vision_providers.base import VisionProvider, VisionProviderError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class OpenRouterProvider(VisionProvider):
    """OpenRouter Provider (OpenAI SDK compatible)."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openrouter_api_key:
            raise VisionProviderError(
                "OPENROUTER_API_KEY is not set. Check your .env file.",
                retryable=False,
            )
        self._client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        self._model_name = settings.ai_model
        self._temperature = settings.ai_temperature
        self._timeout = settings.ai_timeout_seconds

    @property
    def name(self) -> str:
        return f"openrouter-{self._model_name}"

    def _encode_image(self, image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode('utf-8')

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
    ) -> Any:
        """
        Send both product images to OpenRouter and return a validated result.
        """
        final_prompt = retry_prompt or developer_prompt or DEVELOPER_PROMPT
        
        # Prepare base64 images
        front_base64 = self._encode_image(front_image)
        back_base64 = self._encode_image(back_image)
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": final_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{front_mime};base64,{front_base64}",
                        },
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{back_mime};base64,{back_base64}",
                        },
                    },
                ],
            }
        ]

        try:
            logger.info("openrouter_call_start", model=self._model_name, is_retry=retry_prompt is not None)
            
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=self._temperature,
                max_tokens=4000,
                response_format={"type": "json_object"},
                timeout=self._timeout
            )
            
            raw_text = response.choices[0].message.content
            
        except Exception as exc:
            logger.error("openrouter_api_error", error=str(exc))
            raise VisionProviderError(
                f"OpenRouter API call failed: {exc}",
                retryable=True,
            ) from exc

        # ── Parse JSON ────────────────────────────────────────────────
        if not raw_text or not raw_text.strip():
            raise VisionProviderError(
                "OpenRouter returned an empty response.",
                retryable=True,
            )

        try:
            parsed_json = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            logger.warning("invalid_json_returned", text=raw_text[:200])
            raise VisionProviderError(
                f"Failed to parse AI response as JSON. ({exc})",
                retryable=True,
            ) from exc

        # ── Validate Schema ───────────────────────────────────────────
        try:
            return schema_cls.model_validate(parsed_json)
        except ValidationError as exc:
            logger.warning("schema_validation_failed", errors=exc.errors())
            
            error_details = []
            for err in exc.errors():
                loc = " -> ".join(str(l) for l in err["loc"])
                error_details.append(f"Field '{loc}': {err['msg']}")
                
            retry_msg = (
                "Your previous response failed JSON Schema validation. "
                "Please fix the following errors and try again:\n"
                + "\n".join(error_details)
            )
            raise VisionProviderError(retry_msg, retryable=True) from exc
