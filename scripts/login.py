"""
login.py

初回ログイン専用

使い方
-------
python scripts/login.py
"""

from pathlib import Path
import sys

# --------------------------------------------------
# Project Root
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# --------------------------------------------------

from src.browser import BrowserManager

STATE_FILE = ROOT / "data" / "storage_state.json"


def main():

    print("=" * 60)
    print("SUPER CURVE TERMINAL")
    print("X Login")
    print("=" * 60)

    browser = BrowserManager(
        headless=False
    )

    try:

        page = browser.start()

        page = browser.open(
            "https://x.com/login"
        )

        print()
        print("ブラウザでXへログインしてください。")
        print("ログインが完了したら Enter を押してください。")
        print()

        input("Press Enter > ")

        browser.save_storage_state()

        print()
        print("=" * 60)
        print("保存完了")
        print(STATE_FILE)
        print("=" * 60)

    finally:

        browser.close()


if __name__ == "__main__":
    main()