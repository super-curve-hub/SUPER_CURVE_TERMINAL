"""
scripts/save_x_login.py

X / Twitter login state saver for Playwright.

This script opens X in a browser, lets you log in manually,
and saves the browser storage state to data/storage_state.json.

Usage
-----
python scripts/save_x_login.py
"""

from __future__ import annotations

import sys
from pathlib import Path


# ==================================================
# Path Setup
# ==================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from src.config import STORAGE_STATE_FILE


def main() -> None:
    from playwright.sync_api import sync_playwright

    storage_path = Path(STORAGE_STATE_FILE)
    storage_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 60)
    print("X Login State Saver")
    print("=" * 60)
    print()
    print("1. Browser will open.")
    print("2. Log in to X manually.")
    print("3. After the timeline/profile is visible, return here.")
    print("4. Press Enter.")
    print()
    print(f"Storage will be saved to: {storage_path}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=100,
        )

        context = browser.new_context(
            viewport={
                "width": 1280,
                "height": 1600,
            },
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
        )

        page = context.new_page()

        page.goto(
            "https://x.com/login",
            wait_until="domcontentloaded",
            timeout=60_000,
        )

        input("Log in to X, then press Enter here... ")

        context.storage_state(
            path=str(storage_path),
        )

        print()
        print("=" * 60)
        print("Storage State Saved")
        print("=" * 60)
        print(storage_path)

        context.close()
        browser.close()


if __name__ == "__main__":
    main()