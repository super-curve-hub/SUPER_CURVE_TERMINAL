"""
browser.py

Playwright Browser Manager
"""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


COOKIE_FILE = Path("data") / "cookies_playwright.json"


class BrowserManager:

    def __init__(self, headless: bool = True):

        self.headless = headless

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    # --------------------------------------------------
    # Browser Start
    # --------------------------------------------------

    def start(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        self.context = self.browser.new_context(
            viewport={
                "width": 1600,
                "height": 900,
            },
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
        )

        self.page = self.context.new_page()

        self.page.set_default_timeout(60000)

        #
        # Cookie読込
        #

        if COOKIE_FILE.exists():

            print(f"Loading cookies : {COOKIE_FILE}")

            with open(
                COOKIE_FILE,
                "r",
                encoding="utf-8",
            ) as f:

                cookies = json.load(f)

            #
            # x.comへアクセス
            #

            self.page.goto(
                "https://x.com",
                wait_until="domcontentloaded",
            )

            #
            # Cookie投入
            #

            self.context.add_cookies(cookies)

            #
            # Reload
            #

            self.page.reload(
                wait_until="domcontentloaded"
            )

            #
            # SPA描画待ち
            #

            self.page.wait_for_timeout(3000)

            print(f"Loaded {len(cookies)} cookies")

        else:

            print("Cookie file not found.")

        return self.page

    # --------------------------------------------------
    # Open URL
    # --------------------------------------------------

    def open(
        self,
        url: str,
    ):

        self.page.goto(
            url,
            wait_until="domcontentloaded",
        )

        #
        # XはSPAなので描画待ち
        #

        self.page.wait_for_timeout(5000)

        return self.page

    # --------------------------------------------------
    # HTML
    # --------------------------------------------------

    def html(self):

        return self.page.content()

    # --------------------------------------------------
    # Screenshot
    # --------------------------------------------------

    def screenshot(
        self,
        path,
    ):

        self.page.screenshot(
            path=str(path),
            full_page=True,
        )

    # --------------------------------------------------
    # Close
    # --------------------------------------------------

    def close(self):

        try:

            if self.context:
                self.context.close()

            if self.browser:
                self.browser.close()

        finally:

            if self.playwright:
                self.playwright.stop()