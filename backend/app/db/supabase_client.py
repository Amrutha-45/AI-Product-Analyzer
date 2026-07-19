"""
db/supabase_client.py
----------------------
Single Supabase client instance.  All database access goes through
get_supabase() — never instantiate the client elsewhere.

The service key (not the public anon key) is used here so the backend
has full read/write access independent of Row Level Security policies.
RLS still enforces access control for reads scoped to device_id, but
writes always go through this privileged client.
"""

from functools import lru_cache
from supabase import create_client, Client
from app.core.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


@lru_cache
def get_supabase() -> Client:
    """Return a cached Supabase client instance."""
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_service_key:
        logger.warning(
            "supabase_not_configured",
            message="SUPABASE_URL or SUPABASE_SERVICE_KEY not set. "
                    "Database features (caching, history) will be unavailable.",
        )
        # Still return a client — it will fail at call time with a clear error
        # rather than crashing the whole app on startup.

    client = create_client(settings.supabase_url, settings.supabase_service_key)
    logger.info("supabase_client_initialized", url=settings.supabase_url)
    return client
