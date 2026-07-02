"""
scripts/check_compile.py

SUPER CURVE TERMINAL
Compile Check Script

主要Pythonファイルを一括で py_compile する。

Usage
-----
python scripts/check_compile.py
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


TARGETS = [
    # Root scripts
    "app.py",
    "update.py",

    # Core modules
    "src/archive_importer.py",
    "src/update_engine.py",
    "src/config.py",
    "src/database.py",
    "src/logger.py",
    "src/progress.py",
    "src/search.py",
    "src/build_embeddings.py",
    "src/tweet_importer.py",

    # Utility scripts
    "scripts/init_db.py",
    "scripts/import_archive.py",
    "scripts/save_x_login.py",
    "scripts/check_storage_state.py",
    "scripts/test_live_update.py",
    "scripts/check_compile.py",
]


def compile_file(path: Path) -> bool:
    relative = path.relative_to(ROOT_DIR)

    if not path.exists():
        print(f"❌ MISSING  {relative}")
        return False

    try:
        py_compile.compile(
            file=str(path),
            doraise=True,
        )
    except py_compile.PyCompileError as exc:
        print(f"❌ FAILED   {relative}")
        print(exc)
        return False

    print(f"✅ OK       {relative}")
    return True


def main() -> None:
    print("=" * 60)
    print("SUPER CURVE TERMINAL")
    print("Python Compile Check")
    print("=" * 60)

    ok = True

    for target in TARGETS:
        path = ROOT_DIR / target
        result = compile_file(path)
        ok = ok and result

    print()
    print("=" * 60)

    if ok:
        print("Compile Check Complete: ALL OK")
        print("=" * 60)
        return

    print("Compile Check Failed")
    print("=" * 60)
    sys.exit(1)


if __name__ == "__main__":
    main()