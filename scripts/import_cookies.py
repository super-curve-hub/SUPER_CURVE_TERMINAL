"""
import_cookies.py

Cookie-Editor
    ↓
Playwright Cookie Format

Usage
-----
python scripts/import_cookies.py
"""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "cookies.json"
OUTPUT_FILE = ROOT / "data" / "cookies_playwright.json"


def convert_same_site(value):

    if value is None:
        return "Lax"

    value = value.lower()

    if value == "no_restriction":
        return "None"

    if value == "unspecified":
        return "Lax"

    if value == "lax":
        return "Lax"

    if value == "strict":
        return "Strict"

    return "Lax"


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        cookies = json.load(f)

    result = []

    for c in cookies:

        cookie = {
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c.get("path", "/"),
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", True),
            "sameSite": convert_same_site(
                c.get("sameSite")
            ),
        }

        #
        # expirationDate
        #

        if not c.get("session", False):

            if "expirationDate" in c:

                cookie["expires"] = int(
                    c["expirationDate"]
                )

        result.append(cookie)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("=" * 60)
    print("Cookie Conversion Complete")
    print("=" * 60)
    print(f"Input  : {INPUT_FILE}")
    print(f"Output : {OUTPUT_FILE}")
    print(f"Cookies: {len(result)}")


if __name__ == "__main__":
    main()