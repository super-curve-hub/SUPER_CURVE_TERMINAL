"""
scripts/check_storage_state.py

Check Playwright storage_state.json for X / Twitter login cookies.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
STORAGE_STATE_FILE = ROOT_DIR / "data" / "storage_state.json"


def format_expiry(expires):
    if not expires:
        return "session"

    try:
        dt = datetime.fromtimestamp(float(expires), tz=timezone.utc)
    except Exception:
        return "invalid"

    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def main():
    print("=" * 60)
    print("SUPER CURVE TERMINAL")
    print("storage_state.json Check")
    print("=" * 60)
    print(f"Path: {STORAGE_STATE_FILE}")
    print()

    if not STORAGE_STATE_FILE.exists():
        print("storage_state.json not found")
        print()
        print("Create it locally after X login restriction is lifted,")
        print("then upload it to:")
        print()
        print("  data/storage_state.json")
        print()
        sys.exit(1)

    try:
        data = json.loads(STORAGE_STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print("Invalid JSON")
        print(exc)
        sys.exit(1)

    cookies = data.get("cookies", [])
    origins = data.get("origins", [])

    if not isinstance(cookies, list):
        print("Invalid format: cookies is not a list")
        sys.exit(1)

    x_cookies = []
    for cookie in cookies:
        domain = str(cookie.get("domain", ""))
        if "x.com" in domain or "twitter.com" in domain:
            x_cookies.append(cookie)

    print(f"Total cookies : {len(cookies)}")
    print(f"X cookies     : {len(x_cookies)}")
    print(f"Origins       : {len(origins)}")
    print()

    if not x_cookies:
        print("No x.com / twitter.com cookies found")
        print("storage_state.json exists, but it does not look logged in.")
        sys.exit(1)

    print("Cookie summary:")
    for cookie in x_cookies:
        name = cookie.get("name", "")
        domain = cookie.get("domain", "")
        expires = cookie.get("expires")
        print(f"- name={name} domain={domain} expires={format_expiry(expires)}")

    print()
    print("=" * 60)
    print("storage_state.json looks usable")
    print("=" * 60)


if __name__ == "__main__":
    main()