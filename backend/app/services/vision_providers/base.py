"""
services/vision_providers/base.py
----------------------------------
Abstract interface that every AI vision provider must implement.

This indirection means the rest of the codebase (vision_extractor,
scan_controller, tests) never imports from a specific provider —
they only ever talk to VisionProvider. Swapping from Gemini to
OpenAI (or running both in an A/B test) is a one-file change.
"""

from abc import ABC, abstractmethod
from app.schemas.scan_result import AIScanResult


class VisionProviderError(Exception):
    """
    Raised by any VisionProvider implementation on failure.
    Normalises all provider-specific errors (network errors, empty
    responses, malformed JSON, schema mismatches) into a single
    exception type so the route layer has exactly one failure case
    to handle.
    """

    def __init__(self, message: str, retryable: bool = True):
        super().__init__(message)
        self.retryable = retryable


class VisionProvider(ABC):
    """
    Abstract base class for AI vision providers.

    Implementations must override `extract()` and optionally `name`.
    """

    @property
    def name(self) -> str:
        """Human-readable provider name (used for logging + DB recording)."""
        return self.__class__.__name__

    @abstractmethod
    async def extract(
        self,
        front_image: bytes,
        back_image: bytes,
        front_mime: str,
        back_mime: str,
        *,
        retry_prompt: str | None = None,
    ) -> AIScanResult:
        """
        Send the two product images to the AI model and return a
        validated AIScanResult.

        Parameters
        ----------
        front_image   Raw bytes of the product's front label image.
        back_image    Raw bytes of the product's back label image.
        front_mime    MIME type of the front image (e.g. "image/jpeg").
        back_mime     MIME type of the back image.
        retry_prompt  If this is a retry attempt, the modified developer
                      prompt that includes the validation error detail.
                      None on the first attempt.

        Raises
        ------
        VisionProviderError  On any failure (network, parse, validation).
        """
        ...
