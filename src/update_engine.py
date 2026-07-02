"""
src/update_engine.py

SUPER CURVE TERMINAL
Differential Update Engine

Archive Import 後の差分更新専用エンジン。

Flow
----
1. SQLite から最新 created_at を取得
2. DEFAULT_ACCOUNT のXページを Playwright で開く
3. 最新投稿を取得
4. 既存 tweet_id を除外
5. 新規分だけ tweets に upsert
6. FTS 更新
7. 必要なら embeddings 再構築
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import DEFAULT_ACCOUNT, STORAGE_STATE_FILE
from src.database import (
    get_latest_created_at,
    optimize_database,
    tweet_count,
    tweet_exists,
    update_fts,
)
from src.logger import get_logger
from src.tweet_importer import import_tweets


logger = get_logger(__name__)


STATUS_URL_RE = re.compile(r"/status/(\d+)")


@dataclass
class UpdateResult:
    """差分更新結果。"""

    account: str
    latest_before: str | None
    fetched: int
    new_rows: int
    imported: int
    before_count: int
    after_count: int
    status: str
    error_message: str | None = None


class UpdateEngine:
    """
    差分更新専用エンジン。

    Parameters
    ----------
    account:
        対象Xアカウント。未指定なら DEFAULT_ACCOUNT。
    max_scrolls:
        Xページで下方向にスクロールする回数。
    headless:
        Playwrightをheadlessで動かすか。
    rebuild:
        新規投稿があった場合にembedding再構築まで行うか。
    """

    def __init__(
        self,
        account: str | None = None,
        max_scrolls: int = 8,
        headless: bool = True,
        rebuild: bool = True,
        # 旧 update.py 互換用。現在は使わない。
        month: str | None = None,
        failed: bool = False,
        resume: bool = False,
    ) -> None:
        self.account = (account or DEFAULT_ACCOUNT).lstrip("@")
        self.max_scrolls = max_scrolls
        self.headless = headless
        self.rebuild = rebuild

        self.month = month
        self.failed = failed
        self.resume = resume

    # ==================================================
    # Date helpers
    # ==================================================

    @staticmethod
    def _now_utc() -> str:
        return datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )

    @staticmethod
    def _normalize_datetime(value: str | None) -> str | None:
        """
        datetime文字列を YYYY-MM-DDTHH:MM:SS.000Z へ寄せる。
        """

        if not value:
            return None

        text = value.strip()

        try:
            dt = datetime.fromisoformat(
                text.replace("Z", "+00:00")
            )
        except ValueError:
            return text

        dt = dt.astimezone(timezone.utc)

        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    @staticmethod
    def _month_from_created_at(created_at: str | None) -> str | None:
        if not created_at:
            return None

        return created_at[:7]

    @staticmethod
    def _is_newer(
        created_at: str | None,
        latest_created_at: str | None,
    ) -> bool:
        if not created_at:
            return False

        if not latest_created_at:
            return True

        return created_at > latest_created_at

    # ==================================================
    # Playwright helpers
    # ==================================================

    def _browser_context_kwargs(self) -> dict[str, Any]:
        """
        Playwright context 引数を作る。

        storage_state.json が存在する場合はログイン状態を使う。
        """

        kwargs: dict[str, Any] = {
            "viewport": {
                "width": 1280,
                "height": 1600,
            },
            "locale": "ja-JP",
            "timezone_id": "Asia/Tokyo",
        }

        storage_path = Path(STORAGE_STATE_FILE)

        if storage_path.exists():
            kwargs["storage_state"] = str(storage_path)

        return kwargs

    @staticmethod
    def _extract_tweet_id_from_href(
        href: str | None,
    ) -> str | None:
        if not href:
            return None

        match = STATUS_URL_RE.search(href)

        if not match:
            return None

        return match.group(1)

    def _extract_article(
        self,
        article: Any,
        inserted_at: str,
    ) -> dict[str, Any] | None:
        """
        Xの article[data-testid='tweet'] から1投稿を抽出する。

        注意
        ----
        XのDOMは頻繁に変わるため、ここでは最低限の安定項目に限定する。

        - tweet_id
        - created_at
        - text
        - url

        likes / reposts / replies / quotes はDOM依存が強いため0で入れる。
        """

        # status URL
        tweet_id: str | None = None
        href: str | None = None

        try:
            links = article.locator('a[href*="/status/"]')
            link_count = links.count()

            for i in range(link_count):
                candidate_href = links.nth(i).get_attribute("href")
                candidate_id = self._extract_tweet_id_from_href(
                    candidate_href
                )

                if candidate_id:
                    tweet_id = candidate_id
                    href = candidate_href
                    break
        except Exception:
            return None

        if not tweet_id:
            return None

        # created_at
        created_at: str | None = None

        try:
            time_locator = article.locator("time").first
            created_at = time_locator.get_attribute("datetime")
            created_at = self._normalize_datetime(created_at)
        except Exception:
            created_at = None

        # text
        text = ""

        try:
            text_nodes = article.locator(
                'div[data-testid="tweetText"]'
            )

            parts: list[str] = []

            for i in range(text_nodes.count()):
                item_text = text_nodes.nth(i).inner_text().strip()

                if item_text:
                    parts.append(item_text)

            text = "\n".join(parts).strip()
        except Exception:
            text = ""

        if not text:
            return None

        if href and href.startswith("/"):
            url = f"https://x.com{href}"
        elif href:
            url = href
        else:
            url = f"https://x.com/{self.account}/status/{tweet_id}"

        return {
            "tweet_id": tweet_id,
            "created_at": created_at,
            "account": self.account,
            "month": self._month_from_created_at(created_at),
            "text": text,
            "url": url,
            "likes": 0,
            "reposts": 0,
            "replies": 0,
            "quotes": 0,
            "source": "playwright",
            "inserted_at": inserted_at,
        }

    def _fetch_latest_tweets(self) -> pd.DataFrame:
        """
        Playwrightで対象アカウントの最新投稿を取得する。
        """

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "playwright is not installed. "
                "Run: pip install playwright && playwright install chromium"
            ) from exc

        inserted_at = self._now_utc()
        url = f"https://x.com/{self.account}"

        rows: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        logger.info("Opening X page: %s", url)

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
            )

            context = browser.new_context(
                **self._browser_context_kwargs()
            )

            page = context.new_page()

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(5_000)

            for scroll_index in range(self.max_scrolls):
                articles = page.locator(
                    'article[data-testid="tweet"]'
                )

                article_count = articles.count()

                logger.info(
                    "Scroll %s/%s: articles=%s",
                    scroll_index + 1,
                    self.max_scrolls,
                    article_count,
                )

                for i in range(article_count):
                    item = self._extract_article(
                        article=articles.nth(i),
                        inserted_at=inserted_at,
                    )

                    if item is None:
                        continue

                    tweet_id = item["tweet_id"]

                    if tweet_id in seen_ids:
                        continue

                    seen_ids.add(tweet_id)
                    rows.append(item)

                page.mouse.wheel(
                    0,
                    1800,
                )

                page.wait_for_timeout(2_000)

            context.close()
            browser.close()

        columns = [
            "tweet_id",
            "created_at",
            "account",
            "month",
            "text",
            "url",
            "likes",
            "reposts",
            "replies",
            "quotes",
            "source",
            "inserted_at",
        ]

        df = pd.DataFrame(
            rows,
            columns=columns,
        )

        if df.empty:
            return df

        df = (
            df.drop_duplicates(
                subset=["tweet_id"],
                keep="last",
            )
            .sort_values("created_at")
            .reset_index(drop=True)
        )

        return df

    # ==================================================
    # Differential filtering
    # ==================================================

    def _filter_new_rows(
        self,
        df: pd.DataFrame,
        latest_created_at: str | None,
    ) -> pd.DataFrame:
        """
        最新created_atより新しく、かつtweet_id未登録の投稿だけ残す。
        """

        if df.empty:
            return df

        mask = df["created_at"].apply(
            lambda x: self._is_newer(
                x,
                latest_created_at,
            )
        )

        filtered = df.loc[mask].copy()

        if filtered.empty:
            return filtered

        keep_rows: list[dict[str, Any]] = []

        for row in filtered.to_dict(orient="records"):
            tweet_id = str(row["tweet_id"])

            if tweet_exists(tweet_id):
                continue

            keep_rows.append(row)

        return pd.DataFrame(
            keep_rows,
            columns=list(df.columns),
        )

    # ==================================================
    # Index rebuild
    # ==================================================

    def _rebuild_indexes(
        self,
        imported: int,
    ) -> None:
        """
        新規投稿があった場合のみFTS/DB/Embeddingを更新する。
        """

        if imported <= 0:
            print("No new rows. Skip FTS / embeddings.")
            return

        update_fts()
        optimize_database()

        if not self.rebuild:
            print("Embedding rebuild skipped.")
            return

        try:
            from src.build_embeddings import rebuild_embeddings
        except Exception as exc:
            logger.exception("Failed to import rebuild_embeddings")
            print(f"Embedding rebuild skipped: {exc}")
            return

        rebuild_embeddings()

    # ==================================================
    # Public API
    # ==================================================

    def run(self) -> UpdateResult:
        """
        差分更新を実行する。
        """

        before = tweet_count()
        latest_before = get_latest_created_at()

        print("=" * 60)
        print("SUPER CURVE TERMINAL")
        print("Differential Update")
        print("=" * 60)
        print(f"Account       : {self.account}")
        print(f"Before count  : {before}")
        print(f"Latest before : {latest_before}")
        print(f"Max scrolls   : {self.max_scrolls}")
        print(f"Headless      : {self.headless}")
        print()

        try:
            fetched_df = self._fetch_latest_tweets()

            new_df = self._filter_new_rows(
                df=fetched_df,
                latest_created_at=latest_before,
            )

            imported = 0

            if not new_df.empty:
                imported = int(import_tweets(new_df))

            after = tweet_count()

            print()
            print("=" * 60)
            print("Differential Update Result")
            print("=" * 60)
            print(f"Fetched   : {len(fetched_df)}")
            print(f"New rows  : {len(new_df)}")
            print(f"Imported  : {imported}")
            print(f"Before    : {before}")
            print(f"After     : {after}")
            print()

            self._rebuild_indexes(imported)

            return UpdateResult(
                account=self.account,
                latest_before=latest_before,
                fetched=len(fetched_df),
                new_rows=len(new_df),
                imported=imported,
                before_count=before,
                after_count=after,
                status="success",
            )

        except Exception as exc:
            logger.exception("Differential update failed")

            print()
            print("=" * 60)
            print("Differential Update Failed")
            print("=" * 60)
            print(str(exc))

            return UpdateResult(
                account=self.account,
                latest_before=latest_before,
                fetched=0,
                new_rows=0,
                imported=0,
                before_count=before,
                after_count=tweet_count(),
                status="failed",
                error_message=str(exc),
            )