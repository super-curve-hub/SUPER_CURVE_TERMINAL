"""
playwright_fetcher.py

Playwright Fetcher
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.browser import BrowserManager
from src.database import get_search_url
from src.parser import parse_page
from src.scroll import scroll_to_bottom


DEBUG_DIR = Path("debug")
DEBUG_DIR.mkdir(exist_ok=True)


class PlaywrightFetcher:

    def __init__(
        self,
        headless: bool = True,
        debug: bool = True,
    ):

        self.headless = headless
        self.debug = debug

    def fetch_month(
        self,
        month: str,
    ) -> pd.DataFrame:

        url = get_search_url(month)

        if url is None:
            raise ValueError(
                f"Search URL not found : {month}"
            )

        print("=" * 60)
        print(f"Month : {month}")
        print(url)
        print("=" * 60)

        browser = BrowserManager(
            headless=self.headless
        )

        try:

            page = browser.start()

            page = browser.open(url)

            #
            # Debug (Open)
            #

            if self.debug:

                browser.screenshot(
                    DEBUG_DIR / "01_open.png"
                )

                with open(
                    DEBUG_DIR / "01_open.html",
                    "w",
                    encoding="utf-8",
                ) as f:

                    f.write(browser.html())

            #
            # Scroll
            #

            scroll_to_bottom(page)

            #
            # Debug (Scroll)
            #

            if self.debug:

                browser.screenshot(
                    DEBUG_DIR / "02_scroll.png"
                )

                with open(
                    DEBUG_DIR / "02_scroll.html",
                    "w",
                    encoding="utf-8",
                ) as f:

                    f.write(browser.html())

            #
            # Parse
            #

            df = parse_page(
                page,
                default_account="mageya_curve",
                default_month=month,
            )

            print(f"Tweets : {len(df)}")

            #
            # Debug CSV
            #

            if self.debug:

                df.to_csv(
                    DEBUG_DIR / "tweets.csv",
                    index=False,
                    encoding="utf-8-sig",
                )

            return df

        finally:

            browser.close()


def fetch_month(
    month: str,
    headless: bool = True,
    debug: bool = True,
):

    fetcher = PlaywrightFetcher(
        headless=headless,
        debug=debug,
    )

    return fetcher.fetch_month(month)