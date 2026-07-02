from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
DEBUG_DIR = ROOT_DIR / "debug"
SCRIPTS_DIR = ROOT_DIR / "scripts"

for directory in (DATA_DIR, LOG_DIR, DEBUG_DIR):
    directory.mkdir(parents=True, exist_ok=True)


DB_FILE = DATA_DIR / "super_curve_terminal.db"

EMBEDDINGS_FILE = DATA_DIR / "embeddings.npy"
ID_MAP_FILE = DATA_DIR / "id_map.npy"

COOKIE_FILE = DATA_DIR / "cookies_playwright.json"
STORAGE_STATE_FILE = DATA_DIR / "storage_state.json"

MODEL_NAME = "intfloat/multilingual-e5-base"

DEFAULT_ACCOUNT = "kotsudokan"

START_YEAR = 2015
START_MONTH = 1

LOG_FILE = LOG_DIR / "update.log"
LOG_LEVEL = "INFO"

DEFAULT_TOP_K = 10
SIMILARITY_THRESHOLD = 0.0

APP_NAME = "SUPER CURVE TERMINAL"
VERSION = "1.0.0-alpha1"