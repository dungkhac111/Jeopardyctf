#!/usr/bin/env python3
import re
import sys
from urllib.parse import urljoin
from urllib.request import Request, urlopen


KNOWN_SCANNED_QR = "blockChainPTIT{qr_"


def fetch(url):
    request = Request(url, headers={"User-Agent": "qr-shadow-solver"})
    with urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8")


def bits_to_text(bits):
    out = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8]
        if len(chunk) == 8:
            out.append(int(chunk, 2))
    return out.decode("utf-8", errors="replace")


def main():
    base_url = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "http://127.0.0.1:8081/"
    svg = fetch(urljoin(base_url, "static/qr_shadow.svg"))

    rects = re.findall(
        r'<rect class="shadow-cell" x="([0-9.]+)" y="([0-9.]+)"[^>]+fill="#0([12])0[12]0[12]"',
        svg,
    )
    if not rects:
        raise SystemExit("shadow layer not found")

    ordered = sorted((float(x), float(y), value) for x, y, value in rects)
    bits = "".join("1" if value == "1" else "0" for _, _, value in ordered)
    part2 = bits_to_text(bits).rstrip("\x00")
    print(KNOWN_SCANNED_QR + part2)


if __name__ == "__main__":
    main()
