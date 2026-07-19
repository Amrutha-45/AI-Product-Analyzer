"""
app/main.py
-----------
FastAPI application entry point.
Instantiates the app, configures middleware, mounts all routers.
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import limiter
from app.middleware.error_handler import setup_error_handlers
from app.routes import health, scan, history
from app.utils.logging import setup_logging

# ── Initialise logging first ──────────────────────────────────────────────────
setup_logging()

settings = get_settings()

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Product Analyzer API",
    description=(
        "Analyze packaged consumer products from label photos using AI vision. "
        "Returns ingredient breakdowns, health scores, packaging trust signals, "
        "and healthier alternatives."
    ),
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# ── Middleware ────────────────────────────────────────────────────────────────
setup_cors(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
setup_error_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(scan.router)
app.include_router(history.router)
