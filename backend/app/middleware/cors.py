"""
middleware/cors.py
------------------
CORS configuration. Locked to the deployed frontend origin — not "*".
An open CORS policy on an endpoint that calls a paid AI API is a real
cost risk (any page can trigger scans against your quota).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings


def setup_cors(app: FastAPI) -> None:
    settings = get_settings()
    origins = [settings.frontend_origin]

    # Allow localhost variants in development
    if not settings.is_production:
        origins += [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
