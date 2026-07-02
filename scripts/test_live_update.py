"""
scripts/test_live_update.py

Live differential update test runner.
"""

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from src.config import STORAGE_STATE_FILE
from src.update_engine import UpdateEngine


def parse_args():
    parser = argparse.ArgumentParser(
        description="Test Playwright live differential update.",
    )

    parser.add_argument(
        "--max-scrolls",
        type=int,
        default=2,
        help="Number of scrolls on the X profile page.",
    )

    parser.add_argument(
        "--headful",
        action="store_true",
        help="Run browser with UI. Usually not available in Codespaces.",
    )

    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild embeddings if new tweets are imported.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    storage_path = Path(STORAGE_STATE_FILE)

    print("=" * 60)
    print("SUPER CURVE TERMINAL")
    print("Live Differential Update Test")
    print("=" * 60)
    print(f"storage_state: {storage_path}")
    print()

    if not storage_path.exists():
        print("storage_state.json not found")
        print()
        print("Upload a valid login state file to:")
        print(f"  {storage_path}")
        print()
        print("Then run:")
        print("  python scripts/check_storage_state.py")
        print("  python scripts/test_live_update.py")
        print()
        sys.exit(1)

    engine = UpdateEngine(
        rebuild=args.rebuild,
        max_scrolls=args.max_scrolls,
        headless=not args.headful,
    )

    result = engine.run()

    print()
    print("=" * 60)
    print("Result")
    print("=" * 60)
    print(result)

    if result.status != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()