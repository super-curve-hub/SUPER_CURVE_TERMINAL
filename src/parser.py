"""
parser.py

X Tweet Parser
"""

from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd


STATUS_RE = re.compile(r"/status/(\d+)")


def extract_status_url(article):
    links = article.locator("a").evaluate_all(
        """
        els => els
            .map(e => e.href)
            .filter(h => h.includes('/status/'))
        """
    )

    if not links:
        return "", ""

    url = links[0]
    m = STATUS_RE.search(url)
    tweet_id = m.group(1) if m else ""

    return tweet_id, url


def extract_created_at(article):
    try:
        value = article.locator("time").first.get_attribute("datetime")
        return value or ""
    except Exception:
        return ""


def extract_account_from_url(url):
    try:
        path = urlparse(url).path
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[1] == "status":
            return parts[0]
    except Exception:
        pass

    return ""


def extract_text(article):
    try:
        blocks = article.locator('[data-testid="tweetText"]').all()

        texts = []
        for b in blocks:
            t = b.inner_text().strip()
            if t:
                texts.append(t)

        return "\n".join(texts)

    except Exception:
        return ""


def extract_metrics(article):
    """
    XのDOMは頻繁に変わるため、まずは安全に0埋め。
    v0.3でaria-labelから数値抽出を強化する。
    """

    return {
        "likes": 0,
        "reposts": 0,
        "replies": 0,
        "quotes": 0,
    }


def parse_page(
    page,
    default_account: str | None = None,
    default_month: str | None = None,
) -> pd.DataFrame:

    rows = []

    articles = page.locator("article").all()

    for article in articles:

        try:
            tweet_id, url = extract_status_url(article)

            if not tweet_id:
                continue

            created_at = extract_created_at(article)

            account = (
                extract_account_from_url(url)
                or default_account
                or ""
            )

            text = extract_text(article)

            if not text:
                continue

            metrics = extract_metrics(article)

            month = default_month

            if not month and created_at:
                try:
                    month = pd.to_datetime(created_at).strftime("%Y-%m")
                except Exception:
                    month = ""

            rows.append(
                {
                    "tweet_id": tweet_id,
                    "created_at": created_at,
                    "account": account,
                    "month": month or "",
                    "text": text,
                    "url": url,
                    "likes": metrics["likes"],
                    "reposts": metrics["reposts"],
                    "replies": metrics["replies"],
                    "quotes": metrics["quotes"],
                    "source": "x_playwright",
                    "inserted_at": datetime.utcnow().isoformat(),
                }
            )

        except Exception:
            continue

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    return (
        df.drop_duplicates("tweet_id")
        .sort_values("created_at", ascending=False)
        .reset_index(drop=True)
    )