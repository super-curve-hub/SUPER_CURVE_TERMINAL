"""
update.py

SUPER CURVE TERMINAL

Update Pipeline

Usage
-----
python update.py
python update.py --month 2026-06
python update.py --failed
python update.py --resume
"""

from __future__ import annotations

import argparse
from datetime import datetime

from src.update_engine import UpdateEngine


# ==================================================
# Banner
# ==================================================

def banner() -> None:
    print("=" * 60)
    print("SUPER CURVE TERMINAL")
    print("Update Pipeline")
    print("=" * 60)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()


# ==================================================
# Arguments
# ==================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SUPER CURVE TERMINAL Update Pipeline",
    )

    parser.add_argument(
        "--month",
        type=str,
        help="更新する月（例: 2026-06）",
    )

    parser.add_argument(
        "--failed",
        action="store_true",
        help="failed の月のみ更新",
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="pending / running / failed を再開",
    )

    parser.add_argument(
        "--no-rebuild",
        action="store_true",
        help="FTS / Embedding の再構築を行わない",
    )

    return parser.parse_args()


# ==================================================
# Main
# ==================================================

def main() -> None:
    banner()

    args = parse_args()

    engine = UpdateEngine(
        month=args.month,
        failed=args.failed,
        resume=args.resume,
        rebuild=not args.no_rebuild,
    )

    engine.run()


# ==================================================
# Entry Point
# ==================================================

if __name__ == "__main__":
    main()