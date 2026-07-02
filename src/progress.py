from __future__ import annotations

import os
import time


class Progress:
    """
    SUPER CURVE TERMINAL Progress Bar
    """

    def __init__(
        self,
        total: int,
    ):
        self.total = max(int(total), 1)
        self.start_time = time.time()

    # --------------------------------------------------

    def update(
        self,
        current: int,
        month: str,
        tweets: int,
        status: str,
    ):

        percent = current / self.total

        width = 40

        done = int(width * percent)

        bar = (
            "█" * done +
            "░" * (width - done)
        )

        elapsed = int(
            time.time() - self.start_time
        )

        remaining = self.total - current

        self._clear()

        print("=" * 70)
        print("SUPER CURVE TERMINAL")
        print("Update Progress")
        print("=" * 70)
        print()

        print(f"Progress  : {current}/{self.total}")
        print(bar)
        print(f"{percent * 100:5.1f}%")
        print()

        print(f"Month     : {month}")
        print(f"Tweets    : {tweets}")
        print(f"Status    : {status}")
        print(f"Remaining : {remaining}")

        print()

        print(
            f"Elapsed   : {self._format_time(elapsed)}"
        )

        print()

        print("=" * 70)

    # --------------------------------------------------

    def finish(self):

        elapsed = int(
            time.time() - self.start_time
        )

        print()

        print("=" * 70)
        print("UPDATE COMPLETE")
        print("=" * 70)

        print(
            f"Elapsed : {self._format_time(elapsed)}"
        )

        print("=" * 70)

    # --------------------------------------------------

    @staticmethod
    def _format_time(
        seconds: int,
    ) -> str:

        h = seconds // 3600

        m = (seconds % 3600) // 60

        s = seconds % 60

        return f"{h:02}:{m:02}:{s:02}"

    # --------------------------------------------------

    @staticmethod
    def _clear():

        os.system(
            "cls"
            if os.name == "nt"
            else "clear"
        )