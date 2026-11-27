# logging.config: standard library, applies a configuration dictionary (dictConfig)
import logging.config

# Any: type hint for "any value", the dictionary values hane different types
from typing import Any

# request_id_var: per-request storage; yhe filter reads the id of the current request from it
from app.request_context import request_id_var

LOG_FORMAT = "%(asctime)s %(levelname)s [request_id:%(request_id)s] %(name)s: %(message)s"


class RequestIdFilter(logging.Filter):
    """Add the id of the current request to every log record as 'request_id'."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging(log_level: str) -> None:
    """Configure logging once at application startup."""
    logging_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {"format": LOG_FORMAT},
        },
        "filters": {
            "request_id": {"()": RequestIdFilter},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
                "filters": ["request_id"],
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
        "loggers": {
            "uvicorn": {"handlers": [], "level": log_level, "propagate": True},
            "uvicorn.error": {"handlers": [], "level": log_level, "propagate": True},
            # No handlers and no propagation: Uvicorn sees that nobody listens and skips access log lines
            "uvicorn.access": {"handlers": [], "propagate": False},
            "new_logger": {"handlers": [], "level": log_level, "propagate": True},
        },
    }

    # Apply the configuration; calling it again rebuilds it from scratch, so handlers are not duplicated
    logging.config.dictConfig(logging_config)
