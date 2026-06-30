"""
logger.py

SUPER CURVE TERMINAL
Logging Utility
"""

from __future__ import annotations

import logging
from pathlib import Path

from src.config import (
    LOG_DIR,
    LOG_FILE,
    LOG_LEVEL,
)

# ログディレクトリ作成
Path(LOG_DIR).mkdir(
    parents=True,
    exist_ok=True,
)

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"

_configured = False


def configure_logging() -> None:
    """
    ログ設定（初回のみ）
    """

    global _configured

    if _configured:
        return

    level = getattr(
        logging,
        LOG_LEVEL.upper(),
        logging.INFO,
    )

    formatter = logging.Formatter(
        fmt=_FORMAT,
        datefmt=_DATEFMT,
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

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Logger取得
    """

    configure_logging()

    return logging.getLogger(name)