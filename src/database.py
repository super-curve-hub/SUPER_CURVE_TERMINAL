"""
database.py

SUPER CURVE TERMINAL
SQLite Utility
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.config import DB_FILE


# ==================================================
# Connection
# ==================================================

def get_connection() -> sqlite3.Connection:
    """
    SQLite接続を取得する。

    共通PRAGMAを設定して返す。
    """

    conn = sqlite3.connect(
        DB_FILE,
        timeout=30,
    )

    #
    # Row Factory
    #
    conn.row_factory = sqlite3.Row

    #
    # SQLite PRAGMA
    #
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA cache_size = -64000")      # 約64MB
    conn.execute("PRAGMA mmap_size = 268435456")    # 256MB

    return conn


# ==================================================
# Months
# ==================================================

def get_search_url(month: str) -> str | None:
    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT search_url
            FROM months
            WHERE month = ?
            """,
            (month,),
        ).fetchone()

        if row is None:
            return None

        return row[0]

    finally:
        conn.close()


def list_months() -> pd.DataFrame:
    conn = get_connection()

    try:
        return pd.read_sql(
            """
            SELECT *
            FROM months
            ORDER BY month DESC
            """,
            conn,
        )

    finally:
        conn.close()


def get_pending_months() -> pd.DataFrame:
    conn = get_connection()

    try:
        return pd.read_sql(
            """
            SELECT *
            FROM months
            WHERE status = 'pending'
            ORDER BY month DESC
            """,
            conn,
        )

    finally:
        conn.close()


def get_months_for_update(
    month: str | None = None,
    failed: bool = False,
    resume: bool = False,
) -> pd.DataFrame:
    conn = get_connection()

    try:
        if month is not None:
            return pd.read_sql(
                """
                SELECT *
                FROM months
                WHERE month = ?
                ORDER BY month DESC
                """,
                conn,
                params=(month,),
            )

        if failed:
            return pd.read_sql(
                """
                SELECT *
                FROM months
                WHERE status = 'failed'
                ORDER BY month DESC
                """,
                conn,
            )

        if resume:
            return pd.read_sql(
                """
                SELECT *
                FROM months
                WHERE status IN ('pending', 'running', 'failed')
                ORDER BY month DESC
                """,
                conn,
            )

        return pd.read_sql(
            """
            SELECT *
            FROM months
            WHERE status = 'pending'
            ORDER BY month DESC
            """,
            conn,
        )

    finally:
        conn.close()


def update_month_status(
    month: str,
    status: str,
    tweet_count: int | None = None,
    error_message: str | None = None,
) -> None:
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE months
            SET
                status = ?,
                tweet_count = COALESCE(?, tweet_count),
                error_message = ?,
                updated_at = datetime('now','localtime')
            WHERE month = ?
            """,
            (
                status,
                tweet_count,
                error_message,
                month,
            ),
        )

        conn.commit()

    finally:
        conn.close()
# ==================================================
# Tweets
# ==================================================

def list_tweets() -> pd.DataFrame:
    """
    全ツイート一覧
    """

    conn = get_connection()

    try:

        return pd.read_sql(
            """
            SELECT *
            FROM tweets
            ORDER BY created_at DESC
            """,
            conn,
        )

    finally:

        conn.close()


def tweet_count() -> int:
    """
    tweets件数
    """

    conn = get_connection()

    try:

        row = conn.execute(
            """
            SELECT COUNT(*)
            FROM tweets
            """
        ).fetchone()

        return int(row[0])

    finally:

        conn.close()


def tweet_exists(
    tweet_id: str,
) -> bool:
    """
    tweet存在確認
    """

    conn = get_connection()

    try:

        row = conn.execute(
            """
            SELECT 1
            FROM tweets
            WHERE tweet_id=?
            LIMIT 1
            """,
            (tweet_id,),
        ).fetchone()

        return row is not None

    finally:

        conn.close()


def get_latest_created_at() -> str | None:
    """
    最新Tweet日時
    """

    conn = get_connection()

    try:

        row = conn.execute(
            """
            SELECT MAX(created_at)
            FROM tweets
            """
        ).fetchone()

        return row[0]

    finally:

        conn.close()


def get_tweets_by_ids(
    tweet_ids: list[str],
) -> pd.DataFrame:

    if len(tweet_ids) == 0:
        return pd.DataFrame()

    conn = get_connection()

    try:

        placeholders = ",".join(
            ["?"] * len(tweet_ids)
        )

        df = pd.read_sql(
            f"""
            SELECT *
            FROM tweets
            WHERE tweet_id IN ({placeholders})
            """,
            conn,
            params=tweet_ids,
        )

        order = {
            tid: i
            for i, tid in enumerate(tweet_ids)
        }

        df["rank"] = (
            df["tweet_id"]
            .astype(str)
            .map(order)
        )

        return (
            df.sort_values("rank")
            .drop(columns=["rank"])
            .reset_index(drop=True)
        )

    finally:

        conn.close()


# ==================================================
# FTS
# ==================================================

def update_fts():
    """
    tweets
        ↓
    tweets_fts
    """

    conn = get_connection()

    try:

        cur = conn.cursor()

        cur.execute(
            """
            DELETE FROM tweets_fts
            """
        )

        cur.execute(
            """
            INSERT INTO tweets_fts
            (
                tweet_id,
                account,
                month,
                text,
                url
            )

            SELECT
                tweet_id,
                account,
                month,
                text,
                url

            FROM tweets

            ORDER BY created_at
            """
        )

        conn.commit()

        rows = conn.execute(
            """
            SELECT COUNT(*)
            FROM tweets_fts
            """
        ).fetchone()[0]

        print("=" * 60)
        print("FTS Update Complete")
        print("=" * 60)
        print(f"Rows : {rows}")

    finally:

        conn.close()


# ==================================================
# Utility
# ==================================================

def vacuum() -> None:
    """
    SQLiteデータベースを最適化（VACUUM）
    """

    conn = get_connection()

    try:

        conn.execute("VACUUM")

    finally:

        conn.close()


def analyze() -> None:
    """
    SQLite統計情報を更新
    """

    conn = get_connection()

    try:

        conn.execute("ANALYZE")

    finally:

        conn.close()


def optimize_database() -> None:
    """
    SQLite最適化
    """

    print("=" * 60)
    print("Optimize SQLite")
    print("=" * 60)

    analyze()
    vacuum()

    print("Complete")


# ==================================================
# Export
# ==================================================

__all__ = [
    "get_connection",
    "get_search_url",
    "get_pending_months",
    "list_months",
    "get_months_for_update",
    "update_month_status",
    "update_fts",
    "list_tweets",
    "tweet_count",
    "tweet_exists",
    "get_latest_created_at",
    "get_tweets_by_ids",
    "vacuum",
    "analyze",
    "optimize_database",
]