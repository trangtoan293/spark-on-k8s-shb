import logging
import os
from typing import Optional

_DEFAULT_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s [%(levelname)s] %(name)s - %(message)s")

_configured = False

def _configure_root(level: str = _DEFAULT_LEVEL) -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format=_FORMAT)
    _configured = True


def get_logger(name: Optional[str] = None, level: Optional[str] = None) -> logging.Logger:
    _configure_root(level or _DEFAULT_LEVEL)
    logger = logging.getLogger(name if name else __name__)
    if level:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
