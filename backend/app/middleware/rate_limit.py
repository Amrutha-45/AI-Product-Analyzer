"""
middleware/rate_limit.py
-------------------------
Per-IP rate limiting on the /scan endpoint using slowapi.

Protects the Gemini API budget as much as the server — a single
buggy or malicious client can burn your entire hackathon API quota
in minutes without this.

Rate: configurable via RATE_LIMIT_SCANS_PER_HOUR env var (default 10/hour).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import get_settings

settings = get_settings()

# Single limiter instance — imported by routes that need it
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_scans_per_hour}/hour"],
)
