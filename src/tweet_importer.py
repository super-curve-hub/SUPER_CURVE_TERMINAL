"""
tweet_importer.py

DataFrame
    ↓
SQLite
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


DB_FILE = Path("data") / "super_curve_terminal.db"


class TweetImporter:

    def __init__(self):

        self.conn = sqlite3.connect(DB_FILE)

    def import_dataframe(
        self,
        df: pd.DataFrame,
    ) -> int:

        if df.empty:
            print("No tweets.")
            return 0

        cur = self.conn.cursor()

        count = 0

        for _, row in df.iterrows():

            cur.execute(
                """
                INSERT INTO tweets(
                    tweet_id,
                    created_at,
                    account,
                    month,
                    text,
                    url,
                    likes,
                    reposts,
                    replies,
                    quotes,
                    source,
                    inserted_at
                )
                VALUES(
                    ?,?,?,?,?,?,?,?,?,?,?,?
                )
                ON CONFLICT(tweet_id)
                DO UPDATE SET

                    created_at=excluded.created_at,
                    account=excluded.account,
                    month=excluded.month,
                    text=excluded.text,
                    url=excluded.url,
                    likes=excluded.likes,
                    reposts=excluded.reposts,
                    replies=excluded.replies,
                    quotes=excluded.quotes,
                    source=excluded.source
                """,
                (
                    row["tweet_id"],
                    row["created_at"],
                    row["account"],
                    row["month"],
                    row["text"],
                    row["url"],
                    int(row["likes"]),
                    int(row["reposts"]),
                    int(row["replies"]),
                    int(row["quotes"]),
                    row["source"],
                    row["inserted_at"],
                ),
            )

            count += 1

        self.conn.commit()

        print(f"Imported : {count}")

        return count

    def close(self):

        self.conn.close()


def import_tweets(
    df: pd.DataFrame,
):

    importer = TweetImporter()

    try:

        return importer.import_dataframe(df)

    finally:

        importer.close()