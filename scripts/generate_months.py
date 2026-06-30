"""
Generate months table

Usage
-----
python scripts/generate_months.py
"""

from datetime import datetime
import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path("data") / "super_curve_terminal.db"

# ----------------------------
# 設定
# ----------------------------

ACCOUNT = "mageya_curve"

START = "2022-06"
END = datetime.today().strftime("%Y-%m")


def month_range(start, end):

    months = pd.period_range(
        start=start,
        end=end,
        freq="M",
    )

    return [str(m) for m in months]


def build_search_url(account, month):

    since = f"{month}-01"

    until = (
        pd.Period(month)
        .end_time
        .strftime("%Y-%m-%d")
    )

    url = (
        "https://x.com/search?"
        f"q=from:{account}%20"
        f"since:{since}%20"
        f"until:{until}"
        "&src=typed_query&f=live"
    )

    return since, until, url


def main():

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    count = 0

    for month in reversed(month_range(START, END)):

        since, until, url = build_search_url(
            ACCOUNT,
            month,
        )

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
                month,
                since,
                until,
                url,
                ACCOUNT,
                "pending",
            ),
        )

        count += 1

    conn.commit()
    conn.close()

    print("=" * 60)
    print("Months Generated")
    print("=" * 60)
    print(f"Account : {ACCOUNT}")
    print(f"Months  : {count}")


if __name__ == "__main__":
    main()