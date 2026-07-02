"""
scripts/init_db.py

SUPER CURVE TERMINAL
SQLite Database Initializer

Usage
-----
python scripts/init_db.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_FILE = DATA_DIR / "super_curve_terminal.db"


def create_months_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS months (
            month TEXT PRIMARY KEY,
            since TEXT NOT NULL,
            until TEXT NOT NULL,
            search_url TEXT NOT NULL,
            account TEXT,
            status TEXT DEFAULT 'pending',
            tweet_count INTEGER DEFAULT 0,
            error_message TEXT,
            updated_at TEXT
        )
        """
    )


def create_tweets_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tweets (
            tweet_id TEXT PRIMARY KEY,
            created_at TEXT,
            account TEXT,
            month TEXT,
            text TEXT,
            url TEXT,
            likes INTEGER DEFAULT 0,
            reposts INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            quotes INTEGER DEFAULT 0,
            source TEXT DEFAULT 'archive',
            inserted_at TEXT
        )
        """
    )


def create_fts_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS tweets_fts
        USING fts5(
            tweet_id,
            account,
            month,
            text,
            url
        )
        """
    )


def create_indexes(conn: sqlite3.Connection) -> None:
    indexes = [
        """
        CREATE INDEX IF NOT EXISTS idx_tweets_created_at
        ON tweets(created_at)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_tweets_month
        ON tweets(month)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_tweets_account
        ON tweets(account)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_months_status
        ON months(status)
        """,
    ]

    for sql in indexes:
        conn.execute(sql)


def init_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)

    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA foreign_keys = ON")

        create_months_table(conn)
        create_tweets_table(conn)
        create_fts_table(conn)
        create_indexes(conn)

        conn.commit()

    finally:
        conn.close()


def main() -> None:
    init_database()

    print("=" * 60)
    print("SUPER CURVE TERMINAL")
    print("Database Initialized")
    print("=" * 60)
    print(f"Database : {DB_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()