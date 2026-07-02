from __future__ import annotations

import logging
from pathlib import Path

from src.config import LOG_DIR, LOG_FILE, LOG_LEVEL


_CONFIGURED = False


def configure_logging() -> None:
    global _CONFIGURED

    if _CONFIGURED:
        return

    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    level = getattr(
        logging,
        LOG_LEVEL.upper(),
        logging.INFO,
    )

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)