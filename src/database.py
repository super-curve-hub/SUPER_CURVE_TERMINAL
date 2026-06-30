from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd

DB_PATH = Path("data/super_curve_terminal.db")


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(str(db_path))


def get_tweet(tweet_id: str, db_path: Path | str = DB_PATH) -> pd.DataFrame:
    with get_connection(db_path) as conn:
        return pd.read_sql(
            """
            SELECT *
            FROM tweets
            WHERE tweet_id = ?
            """,
            conn,
            params=[tweet_id],
        )


def get_tweets_by_ids(tweet_ids: list[str], db_path: Path | str = DB_PATH) -> pd.DataFrame:
    if not tweet_ids:
        return pd.DataFrame()

    placeholders = ",".join(["?"] * len(tweet_ids))

    with get_connection(db_path) as conn:
        return pd.read_sql(
            f"""
            SELECT *
            FROM tweets
            WHERE tweet_id IN ({placeholders})
            """,
            conn,
            params=tweet_ids,
        )


def search_fts(
    query: str,
    month: Optional[str] = None,
    account: Optional[str] = None,
    limit: int = 50,
    db_path: Path | str = DB_PATH,
) -> pd.DataFrame:
    sql = """
    SELECT
        t.*
    FROM tweets_fts f
    JOIN tweets t
        ON f.tweet_id = t.tweet_id
    WHERE tweets_fts MATCH ?
    """

    params: list[object] = [query]

    if month:
        sql += " AND t.month = ?"
        params.append(month)

    if account:
        sql += " AND t.account = ?"
        params.append(account)

    sql += " ORDER BY t.created_at DESC LIMIT ?"
    params.append(limit)

    with get_connection(db_path) as conn:
        return pd.read_sql(sql, conn, params=params)


def list_months(db_path: Path | str = DB_PATH) -> list[str]:
    with get_connection(db_path) as conn:
        df = pd.read_sql(
            """
            SELECT month
            FROM months
            ORDER BY month DESC
            """,
            conn,
        )
    return df["month"].dropna().tolist()


def list_accounts(db_path: Path | str = DB_PATH) -> list[str]:
    with get_connection(db_path) as conn:
        df = pd.read_sql(
            """
            SELECT DISTINCT account
            FROM tweets
            WHERE account IS NOT NULL
            ORDER BY account
            """,
            conn,
        )
    return df["account"].dropna().tolist()
