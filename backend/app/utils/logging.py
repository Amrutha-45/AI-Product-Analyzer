"""
utils/logging.py
----------------
Configures structlog for structured output.
Uses stdlib integration to fix PrintLogger/add_logger_name compatibility issue.
"""

import logging
import structlog
from app.core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()

    log_level = logging.DEBUG if not settings.is_production else logging.INFO

    # Configure stdlib logging first — structlog will delegate to it
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
    )

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_production:
        processors = shared_processors + [structlog.processors.JSONRenderer()]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=False)
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        # Use stdlib logger factory instead of PrintLoggerFactory
        # so that add_logger_name works correctly
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Silence noisy third-party loggers in production
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str = __name__):
    """Return a bound structlog logger for the given module name."""
    return structlog.get_logger(name)
