"""
scroll.py

Auto Scroll Utility
"""

from __future__ import annotations

import time


def scroll_to_bottom(
    page,
    max_scrolls: int = 100,
    pause: float = 2.0,
    stable_rounds: int = 3,
):
    """
    ページを最下部までスクロールし、
    HTMLを返す。

    Parameters
    ----------
    page : Playwright Page

    max_scrolls : int
        最大スクロール回数

    pause : float
        スクロール後の待機時間(秒)

    stable_rounds : int
        高さが変化しない状態が
        何回続けば終了するか
    """

    last_height = 0
    stable = 0

    for i in range(max_scrolls):

        page.evaluate(
            """
            window.scrollTo(
                0,
                document.body.scrollHeight
            );
            """
        )

        time.sleep(pause)

        height = page.evaluate(
            "document.body.scrollHeight"
        )

        print(
            f"Scroll {i+1:03d}  Height={height}"
        )

        if height == last_height:

            stable += 1

        else:

            stable = 0

        if stable >= stable_rounds:

            print("Reached Bottom.")
            break

        last_height = height

    return page.content()