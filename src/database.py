"""
database.py

SQLite Utility
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


DB_FILE = Path("data") / "super_curve_terminal.db"


# --------------------------------------------------
# Connection
# --------------------------------------------------


def get_connection():

    return sqlite3.connect(DB_FILE)


# --------------------------------------------------
# Search URL
# --------------------------------------------------


def get_search_url(
    month: str,
):

    conn = get_connection()

    try:

        row = conn.execute(
            """
            SELECT search_url
            FROM months
            WHERE month=?
            """,
            (month,),
        ).fetchone()

        if row is None:
            return None

        return row[0]

    finally:

        conn.close()


# --------------------------------------------------
# Pending Months
# --------------------------------------------------


def get_pending_months():

    conn = get_connection()

    try:

        return pd.read_sql(
            """
            SELECT *
            FROM months
            WHERE status='pending'
            ORDER BY month DESC
            """,
            conn,
        )

    finally:

        conn.close()


# --------------------------------------------------
# Month List
# --------------------------------------------------


def list_months():

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


# --------------------------------------------------
# Month Status
# --------------------------------------------------


def update_month_status(
    month: str,
    status: str,
):

    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE months
            SET
                status=?,
                updated_at=datetime('now','localtime')
            WHERE month=?
            """,
            (
                status,
                month,
            ),
        )

        conn.commit()

    finally:

        conn.close()


# --------------------------------------------------
# FTS Update
# --------------------------------------------------

def update_fts():
    """
    tweets テーブル → tweets_fts を完全同期する
    """

    conn = get_connection()

    try:

        cur = conn.cursor()

        #
        # FTSを空にする
        #
        cur.execute(
            """
            DELETE FROM tweets_fts
            """
        )

        #
        # tweets → FTS
        #
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

        count = conn.execute(
            """
            SELECT COUNT(*)
            FROM tweets_fts
            """
        ).fetchone()[0]

        print("=" * 60)
        print("FTS Update Complete")
        print("=" * 60)
        print(f"Rows : {count}")

    finally:

        conn.close()


# --------------------------------------------------
# Tweet List
# --------------------------------------------------


def list_tweets():

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


# --------------------------------------------------
# Tweet Count
# --------------------------------------------------


def tweet_count():

    conn = get_connection()

    try:

        row = conn.execute(
            """
            SELECT COUNT(*)
            FROM tweets
            """
        ).fetchone()

        return row[0]

    finally:

        conn.close()