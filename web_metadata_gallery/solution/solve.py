#!/usr/bin/env python3
import base64
import sys
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def png_chunks(data):
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG file")
    off = 8
    while off + 12 <= len(data):
        size = int.from_bytes(data[off:off + 4], "big")
        kind = data[off + 4:off + 8]
        payload = data[off + 8:off + 8 + size]
        yield kind, payload
        off += 12 + size


def decode_note(value):
    raw = base64.b64decode(value)
    for key in range(256):
        text = bytes(byte ^ key for byte in raw)
        if text.startswith(b"blockChainPTIT{"):
            return text.decode()
    raise ValueError("flag not found in note")


def main():
    base_url = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "http://127.0.0.1:8080/"

    fetch_text(urljoin(base_url, "robots.txt"))

    _, preview_headers = fetch_bytes(urljoin(base_url, "static-view/silent-lake"))
    origin_path = preview_headers["X-Origin-Path"]

    original, _ = fetch_bytes(urljoin(base_url, origin_path.lstrip("/")))

    for kind, payload in png_chunks(original):
        if kind == b"tEXt":
            keyword, _, value = payload.partition(b"\x00")
            if keyword == b"archive.note":
                print(decode_note(value.decode()))
                return
    raise SystemExit("archive.note metadata not found")


def fetch_bytes(url):
    request = Request(url, headers={"User-Agent": "metadata-gallery-solver"})
    with urlopen(request, timeout=10) as response:
        return response.read(), response.headers


def fetch_text(url):
    data, _ = fetch_bytes(url)
    return data.decode("utf-8", errors="replace")


if __name__ == "__main__":
    main()
