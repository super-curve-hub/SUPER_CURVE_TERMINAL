"""
archive_importer.py

SUPER CURVE TERMINAL

X / Twitter Archive Importer

Purpose
-------
Twitter Archive ZIP から data/tweets.js を読み込み、
tweet_importer.py にそのまま渡せる DataFrame を生成する。

Usage
-----
from src.archive_importer import ArchiveImporter

df = ArchiveImporter("twitter-archive.zip").load()
"""

from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_FILES = [
    "data/manifest.js",
    "data/account.js",
    "data/tweets.js",
]


TWITTER_DATE_FORMAT = "%a %b %d %H:%M:%S %z %Y"


@dataclass
class ArchiveAccount:
    """Xアーカイブ内のアカウント情報。"""

    username: str
    account_id: str | None = None
    display_name: str | None = None


class ArchiveImporter:
    """
    X / Twitter Archive ZIP を読み込み、tweets DataFrame を生成する。

    返却DataFrameは src.tweet_importer.import_tweets(df) に合わせる。

    Columns
    -------
    tweet_id
    created_at
    account
    month
    text
    url
    likes
    reposts
    replies
    quotes
    source
    inserted_at
    """

    def __init__(
        self,
        zip_path: str | Path,
        default_account: str | None = None,
    ) -> None:
        self.zip_path = Path(zip_path)
        self.default_account = default_account

        if not self.zip_path.exists():
            raise FileNotFoundError(f"Archive ZIP not found: {self.zip_path}")

        if not self.zip_path.is_file():
            raise ValueError(f"Archive path is not a file: {self.zip_path}")

    # ==================================================
    # ZIP / File
    # ==================================================

    def _open_zip(self) -> zipfile.ZipFile:
        """ZIPファイルを開く。"""

        try:
            return zipfile.ZipFile(self.zip_path)
        except zipfile.BadZipFile as exc:
            raise ValueError(f"Invalid ZIP archive: {self.zip_path}") from exc

    @staticmethod
    def _normalize_name(name: str) -> str:
        """
        ZIP内パスを正規化する。

        一部のアーカイブはトップディレクトリ付きで格納されるため、
        data/tweets.js を末尾一致で検出できるようにする。
        """

        return name.replace("\\", "/").lstrip("./")

    def _find_data_file(
        self,
        zf: zipfile.ZipFile,
        target: str,
    ) -> str:
        """
        ZIP内から target ファイルを探す。

        例
        ---
        target='data/tweets.js'
        """

        target = self._normalize_name(target)

        names = [
            self._normalize_name(name)
            for name in zf.namelist()
        ]

        if target in names:
            idx = names.index(target)
            return zf.namelist()[idx]

        suffix = "/" + target

        for raw_name, normalized in zip(zf.namelist(), names):
            if normalized.endswith(suffix):
                return raw_name

        raise FileNotFoundError(
            f"Required archive file not found: {target}"
        )

    def _read_text_file(
        self,
        zf: zipfile.ZipFile,
        target: str,
    ) -> str:
        """ZIP内のテキストファイルをUTF-8で読む。"""

        archive_name = self._find_data_file(
            zf=zf,
            target=target,
        )

        raw = zf.read(archive_name)

        return raw.decode("utf-8")

    def validate_archive(self) -> None:
        """必須ファイルの存在確認。"""

        with self._open_zip() as zf:
            for file_name in REQUIRED_FILES:
                self._find_data_file(
                    zf=zf,
                    target=file_name,
                )

    # ==================================================
    # JS Parser
    # ==================================================

    @staticmethod
    def _strip_js_assignment(text: str) -> str:
        """
        XアーカイブのJS代入形式をJSON文字列へ変換する。

        例
        ---
        window.YTD.tweets.part0 = [ ... ]
        """

        marker = "="

        if marker not in text:
            raise ValueError("Invalid archive JS format: '=' not found")

        json_text = text.split(marker, 1)[1].strip()

        if json_text.endswith(";"):
            json_text = json_text[:-1].strip()

        return json_text

    def _parse_js_json(self, text: str) -> Any:
        """JS代入形式のテキストをJSONとして読む。"""

        json_text = self._strip_js_assignment(text)

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as exc:
            raise ValueError("Failed to parse archive JS as JSON") from exc

    def _load_manifest(
        self,
        zf: zipfile.ZipFile,
    ) -> dict[str, Any]:
        """manifest.js を読む。"""

        text = self._read_text_file(
            zf=zf,
            target="data/manifest.js",
        )

        data = self._parse_js_json(text)

        if not isinstance(data, dict):
            raise ValueError("manifest.js did not contain an object")

        return data

    def _load_account(
        self,
        zf: zipfile.ZipFile,
    ) -> ArchiveAccount:
        """account.js からアカウント情報を読む。"""

        text = self._read_text_file(
            zf=zf,
            target="data/account.js",
        )

        data = self._parse_js_json(text)

        if not isinstance(data, list) or not data:
            if self.default_account:
                return ArchiveAccount(
                    username=self.default_account,
                )

            raise ValueError("account.js did not contain account data")

        account = data[0].get("account", {})

        username = (
            account.get("username")
            or self.default_account
        )

        if not username:
            raise ValueError("Account username not found")

        return ArchiveAccount(
            username=str(username),
            account_id=(
                str(account["accountId"])
                if account.get("accountId") is not None
                else None
            ),
            display_name=account.get("accountDisplayName"),
        )

    def _load_tweets_raw(
        self,
        zf: zipfile.ZipFile,
    ) -> list[dict[str, Any]]:
        """tweets.js を読み、生データリストを返す。"""

        text = self._read_text_file(
            zf=zf,
            target="data/tweets.js",
        )

        data = self._parse_js_json(text)

        if not isinstance(data, list):
            raise ValueError("tweets.js did not contain a list")

        return data

    # ==================================================
    # Tweet Normalization
    # ==================================================

    @staticmethod
    def _parse_date(value: str | None) -> str | None:
        """
        Xアーカイブの日付をISO形式へ変換する。

        入力例
        ------
        Tue Jun 30 13:07:35 +0000 2026

        出力例
        ------
        2026-06-30T13:07:35.000Z
        """

        if not value:
            return None

        try:
            dt = datetime.strptime(
                value,
                TWITTER_DATE_FORMAT,
            )
        except ValueError:
            try:
                # ISO風の日付が来た場合の保険
                dt = datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )
            except ValueError:
                return value

        dt = dt.astimezone(timezone.utc)

        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    @staticmethod
    def _month_from_created_at(created_at: str | None) -> str | None:
        """created_at から YYYY-MM を取り出す。"""

        if not created_at:
            return None

        return created_at[:7]

    @staticmethod
    def _safe_int(value: Any) -> int:
        """整数変換。Noneや空文字は0。"""

        if value is None:
            return 0

        if value == "":
            return 0

        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _clean_text(value: Any) -> str:
        """本文を文字列化する。"""

        if value is None:
            return ""

        text = str(value)

        # Xアーカイブ本文は改行を含むので、改行は保持する。
        return text.strip()

    @staticmethod
    def _build_url(
        account: str,
        tweet_id: str,
    ) -> str:
        """X投稿URLを生成する。"""

        return f"https://x.com/{account}/status/{tweet_id}"

    @staticmethod
    def _extract_tweet_object(
        row: dict[str, Any],
    ) -> dict[str, Any]:
        """
        tweets.js の1要素から tweet オブジェクトを取り出す。

        通常形式
        --------
        {"tweet": {...}}
        """

        tweet = row.get("tweet")

        if isinstance(tweet, dict):
            return tweet

        # 将来の形式差異への保険
        return row

    def _normalize_tweet(
        self,
        raw_row: dict[str, Any],
        account: ArchiveAccount,
        inserted_at: str,
    ) -> dict[str, Any] | None:
        """1件のtweetをtweet_importer形式へ変換する。"""

        tweet = self._extract_tweet_object(raw_row)

        tweet_id = (
            tweet.get("id_str")
            or tweet.get("id")
        )

        if tweet_id is None:
            return None

        tweet_id = str(tweet_id)

        created_at = self._parse_date(
            tweet.get("created_at")
        )

        month = self._month_from_created_at(
            created_at
        )

        text = self._clean_text(
            tweet.get("full_text")
            or tweet.get("text")
        )

        return {
            "tweet_id": tweet_id,
            "created_at": created_at,
            "account": account.username,
            "month": month,
            "text": text,
            "url": self._build_url(
                account=account.username,
                tweet_id=tweet_id,
            ),
            "likes": self._safe_int(
                tweet.get("favorite_count")
            ),
            "reposts": self._safe_int(
                tweet.get("retweet_count")
            ),
            "replies": self._safe_int(
                tweet.get("reply_count")
            ),
            "quotes": self._safe_int(
                tweet.get("quote_count")
            ),
            "source": "archive",
            "inserted_at": inserted_at,
        }

    def _build_dataframe(
        self,
        rows: list[dict[str, Any]],
        account: ArchiveAccount,
    ) -> pd.DataFrame:
        """生tweetリストからDataFrameを作る。"""

        inserted_at = datetime.now(
            timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        normalized: list[dict[str, Any]] = []

        for row in rows:
            item = self._normalize_tweet(
                raw_row=row,
                account=account,
                inserted_at=inserted_at,
            )

            if item is not None:
                normalized.append(item)

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
            normalized,
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
    # Public API
    # ==================================================

    def load(self) -> pd.DataFrame:
        """
        アーカイブZIPを読み、tweet_importer互換DataFrameを返す。
        """

        with self._open_zip() as zf:
            self.validate_archive()

            # manifestは現時点では検証目的。
            self._load_manifest(zf)

            account = self._load_account(zf)

            rows = self._load_tweets_raw(zf)

        return self._build_dataframe(
            rows=rows,
            account=account,
        )


def load_archive(
    zip_path: str | Path,
    default_account: str | None = None,
) -> pd.DataFrame:
    """
    関数型インターフェース。

    Examples
    --------
    df = load_archive("twitter.zip")
    """

    return ArchiveImporter(
        zip_path=zip_path,
        default_account=default_account,
    ).load()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Load X/Twitter archive ZIP and preview tweets.",
    )

    parser.add_argument(
        "zip_path",
        type=str,
        help="X / Twitter archive ZIP path",
    )

    parser.add_argument(
        "--head",
        type=int,
        default=5,
        help="Preview rows",
    )

    args = parser.parse_args()

    frame = load_archive(args.zip_path)

    print("=" * 60)
    print("Archive Loaded")
    print("=" * 60)
    print(f"Rows : {len(frame)}")
    print(frame.head(args.head))