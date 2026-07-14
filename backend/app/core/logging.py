import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """Configures structured application-wide logging formats."""
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
