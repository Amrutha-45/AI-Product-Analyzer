"""
services/vision_providers/groq_provider.py
---------------------------------------------
Concrete VisionProvider using EasyOCR + Groq.
Extracts text locally from images, then feeds the cleaned text to Groq.
"""

import json
import base64
import numpy as np
from typing import Any
from groq import AsyncGroq
from pydantic import ValidationError

from app.core.config import get_settings
from app.prompts.extraction_prompt import SYSTEM_PROMPT, DEVELOPER_PROMPT
from app.prompts.category_prompts import DETECT_CATEGORY_PROMPT
from app.schemas.category_schemas import CategoryDetectionResult, ProductCategory
from app.services.vision_providers.base import VisionProvider, VisionProviderError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class GroqProvider(VisionProvider):
    """Groq Provider using EasyOCR for text extraction."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.groq_api_key:
            raise VisionProviderError(
                "GROQ_API_KEY is not set. Check your .env file.",
                retryable=False,
            )
        self._client = AsyncGroq(api_key=settings.groq_api_key)
        self._model_name = settings.ai_model
        self._temperature = settings.ai_temperature
        self._timeout = settings.ai_timeout_seconds

        # Lazy load EasyOCR and OpenCV
        self._reader = None
        self._cv2 = None

    def _init_ocr(self):
        if self._reader is None:
            logger.info("initializing_easyocr")
            import easyocr
            import cv2
            self._cv2 = cv2
            self._reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            logger.info("easyocr_initialized")

    @property
    def name(self) -> str:
        return f"groq-easyocr-{self._model_name}"

    def _preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        self._init_ocr()
        # Decode image
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = self._cv2.imdecode(np_arr, self._cv2.IMREAD_COLOR)
        
        # Resize if too small (width < 800)
        h, w = img.shape[:2]
        if w < 800:
            scale = 800 / w
            img = self._cv2.resize(img, None, fx=scale, fy=scale, interpolation=self._cv2.INTER_CUBIC)

        # Grayscale
        gray = self._cv2.cvtColor(img, self._cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = self._cv2.fastNlMeansDenoising(gray, h=30)
        
        # Contrast (CLAHE)
        clahe = self._cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(denoised)
        
        return contrast

    def _extract_text(self, image_bytes: bytes, min_confidence: float = 0.3) -> str:
        if not image_bytes:
            return ""
            
        preprocessed_img = self._preprocess_image(image_bytes)
        
        logger.info("ocr_extraction_started")
        results = self._reader.readtext(preprocessed_img)
        
        filtered_lines = []
        for bbox, text, conf in results:
            if conf >= min_confidence:
                filtered_lines.append(text.strip())
                
        # Clean and merge
        seen = set()
        cleaned_lines = []
        for line in filtered_lines:
            if line and line not in seen:
                seen.add(line)
                cleaned_lines.append(line)
                
        final_text = " ".join(cleaned_lines)
        logger.info("ocr_extraction_finished", cleaned_text_length=len(final_text))
        return final_text

    async def extract(
        self,
        front_image: bytes,
        back_image: bytes,
        front_mime: str,
        back_mime: str,
        retry_prompt: str | None = None,
        schema_cls: type = None,
        developer_prompt: str | None = None,
    ) -> Any:
        
        dev_prompt = developer_prompt or DEVELOPER_PROMPT
        content_prompt = retry_prompt if retry_prompt else dev_prompt

        # Extract text from both images
        front_text = self._extract_text(front_image)
        back_text = self._extract_text(back_image)
        combined_text = f"FRONT LABEL TEXT:\n{front_text}\n\nBACK LABEL TEXT:\n{back_text}"
        
        logger.info("cleaned_ocr_text", combined_text=combined_text)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"{content_prompt}\n\nHere is the text extracted from the product packaging via OCR:\n{combined_text}"
            }
        ]

        try:
            logger.info("groq_request_started", model=self._model_name)
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=self._temperature,
                timeout=self._timeout,
                response_format={"type": "json_object"},
            )
            raw_text = response.choices[0].message.content
            logger.info("groq_response_received", response_text=raw_text)
        except Exception as exc:
            raise VisionProviderError(
                f"Groq API call failed: {exc}",
                retryable=True,
            ) from exc

        try:
            parsed_json = json.loads(raw_text)
            result = schema_cls.model_validate(parsed_json)
            logger.info("json_validation_success")
        except json.JSONDecodeError as exc:
            raise VisionProviderError(
                f"Groq response was not valid JSON: {exc}",
                retryable=True,
            ) from exc
        except ValidationError as exc:
            raise VisionProviderError(
                f"Groq response did not match the expected schema: {exc}",
                retryable=True,
            ) from exc

        logger.info(
            "groq_call_success",
            product_name=getattr(result, "product_name", "Unknown"),
        )
        return result

    async def detect_category(
        self,
        front_image: bytes,
        back_image: bytes,
        front_mime: str,
        back_mime: str,
    ) -> ProductCategory:
        
        front_text = self._extract_text(front_image)
        back_text = self._extract_text(back_image)
        combined_text = f"FRONT LABEL TEXT:\n{front_text}\n\nBACK LABEL TEXT:\n{back_text}"

        messages = [
            {
                "role": "user",
                "content": f"{DETECT_CATEGORY_PROMPT}\n\nHere is the text extracted from the product packaging via OCR:\n{combined_text}"
            }
        ]

        try:
            logger.info("groq_category_detection_started", model=self._model_name)
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=0.0,
                timeout=self._timeout,
                response_format={"type": "json_object"},
            )
            raw_text = response.choices[0].message.content
            logger.info("raw_category_detection_response", text=raw_text)
            parsed_json = json.loads(raw_text)
            result = CategoryDetectionResult.model_validate(parsed_json)
            return result.category
        except Exception as exc:
            logger.error("category_detection_failed", error=str(exc))
            return ProductCategory.food
