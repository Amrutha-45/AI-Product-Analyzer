"""
schemas/error.py
----------------
Standardised error response shapes so every error the API returns
has the same JSON structure — the frontend can always rely on
{ "detail": "..." } being present.
"""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str

    model_config = {"json_schema_extra": {"example": {"detail": "Something went wrong."}}}
