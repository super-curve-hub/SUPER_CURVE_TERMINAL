"""
Initialize months table from search_urls.csv

Usage
-----
python scripts/init_months.py
"""

from pathlib import Path
import sqlite3

import pandas as pd


DB_PATH = Path("data") / "super_curve_terminal.db"
CSV_PATH = Path("search_urls.csv")


def main():

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"{CSV_PATH} が見つかりません。"
        )

    df = pd.read_csv(CSV_PATH)

    required = [
        "month",
        "since",
        "until",
        "url",
        "user",
    ]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"{col} 列がありません。")

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    count = 0

    for _, row in df.iterrows():

        cur.execute(
            """
            INSERT OR REPLACE INTO months
            (
                month,
                since,
                until,
                search_url,
                account,
                status,
                updated_at
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, datetime('now')
            )
            """,
            (
                row["month"],
                row["since"],
                row["until"],
                row["url"],
                row["user"],
                "pending",
            ),
        )

        count += 1

    conn.commit()
    conn.close()

    print("=" * 60)
    print("Months initialized")
    print("=" * 60)
    print(f"{count} records inserted.")


if __name__ == "__main__":
    main()