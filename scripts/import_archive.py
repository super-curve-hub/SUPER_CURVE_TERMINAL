"""
scripts/import_archive.py

SUPER CURVE TERMINAL
Archive Import Script

Usage
-----
python scripts/import_archive.py data/archive/twitter-archive.zip
python scripts/import_archive.py data/archive/twitter-archive.zip --no-fts
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# ==================================================
# Path Setup
# ==================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from src.archive_importer import ArchiveImporter
from src.database import tweet_count, update_fts
from src.tweet_importer import import_tweets


# ==================================================
# Arguments
# ==================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import X/Twitter archive ZIP into SQLite.",
    )

    parser.add_argument(
        "zip_path",
        type=str,
        help="X / Twitter archive ZIP path",
    )

    parser.add_argument(
        "--no-fts",
        action="store_true",
        help="FTS更新をスキップする",
    )

    return parser.parse_args()


# ==================================================
# Main
# ==================================================

def main() -> None:
    args = parse_args()

    zip_path = Path(args.zip_path)

    if not zip_path.exists():
        raise FileNotFoundError(
            f"ZIP file not found: {zip_path}"
        )

    print("=" * 60)
    print("SUPER CURVE TERMINAL")
    print("Archive Import")
    print("=" * 60)
    print(f"Archive : {zip_path}")
    print()

    before = tweet_count()

    df = ArchiveImporter(
        zip_path=zip_path,
    ).load()

    print("=" * 60)
    print("Archive Loaded")
    print("=" * 60)
    print(f"Rows : {len(df)}")
    print()

    imported = import_tweets(df)

    after = tweet_count()

    print()
    print("=" * 60)
    print("SQLite Import Complete")
    print("=" * 60)
    print(f"Before   : {before}")
    print(f"Imported : {imported}")
    print(f"After    : {after}")
    print()

    if not args.no_fts:
        update_fts()

    print()
    print("=" * 60)
    print("Archive Import Finished")
    print("=" * 60)


# ==================================================
# Entry Point
# ==================================================

if __name__ == "__main__":
    main()