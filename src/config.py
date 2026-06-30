"""
config.py

SUPER CURVE TERMINAL
Global Configuration
"""

from pathlib import Path

# ==================================================
# Project
# ==================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

# ==================================================
# Directories
# ==================================================

DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
DEBUG_DIR = ROOT_DIR / "debug"
SCRIPTS_DIR = ROOT_DIR / "scripts"

# 自動生成
for directory in (
    DATA_DIR,
    LOG_DIR,
    DEBUG_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

# ==================================================
# Database
# ==================================================

DB_FILE = DATA_DIR / "super_curve_terminal.db"

# ==================================================
# Embedding
# ==================================================

MODEL_NAME = "intfloat/multilingual-e5-base"

EMBEDDINGS_FILE = DATA_DIR / "embeddings.npy"

ID_MAP_FILE = DATA_DIR / "id_map.npy"

# ==================================================
# Cookies
# ==================================================

COOKIE_FILE = DATA_DIR / "cookies_playwright.json"

# ==================================================
# Playwright
# ==================================================

HEADLESS = True

DEFAULT_TIMEOUT = 30000

SCROLL_WAIT_MS = 1200

MAX_SCROLL = 30

# ==================================================
# Update
# ==================================================

DEFAULT_ACCOUNT = "mageya_curve"

START_YEAR = 2015

START_MONTH = 1

END_YEAR = None

# ==================================================
# Logging
# ==================================================

LOG_FILE = LOG_DIR / "update.log"

LOG_LEVEL = "INFO"

# ==================================================
# Search
# ==================================================

DEFAULT_TOP_K = 10

SIMILARITY_THRESHOLD = 0.50

# ==================================================
# Application
# ==================================================

APP_NAME = "SUPER CURVE TERMINAL"

VERSION = "1.0.0"