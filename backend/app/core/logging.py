import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload)


def setup_logging() -> None:
    root = logging.getLogger()
    root.setLevel(settings.log_level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(JsonLogFormatter())

    root.handlers.clear()
    root.addHandler(stream_handler)
