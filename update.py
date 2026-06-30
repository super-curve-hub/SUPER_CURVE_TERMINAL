"""
SUPER CURVE TERMINAL
Update Pipeline

python update.py
"""

from datetime import datetime

from src.database import get_pending_months
from src.tweet_importer import import_dataframe
from src.build_embeddings import rebuild_embeddings
from src.playwright_fetcher import fetch_month


def banner():

    print("=" * 60)
    print("SUPER CURVE TERMINAL")
    print("Update Pipeline")
    print("=" * 60)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()


def main():

    banner()

    months = get_pending_months()

    if len(months) == 0:
        print("更新対象はありません。")
        return

    total = 0

    for month in months:

        print("-" * 60)
        print(f"対象月 : {month}")
        print("-" * 60)

        df = fetch_month(month)

        if df is None or len(df) == 0:

            print("投稿なし")
            continue

        print(f"{len(df)}件取得")

        import_dataframe(df)

        total += len(df)

    print()
    print("=" * 60)
    print("Embedding更新")
    print("=" * 60)

    rebuild_embeddings()

    print()
    print("=" * 60)
    print("更新完了")
    print("=" * 60)
    print(f"総取得件数 : {total}")


if __name__ == "__main__":
    main()