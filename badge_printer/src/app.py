import base64
import json
import os
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
BADGE_DIR = BASE_DIR / "badges"

BADGES = {
    "1": {
        "owner": "Guest Demo",
        "role": "guest",
        "department": "Visitor",
        "qr": "guest_1.svg",
    },
    "2": {
        "owner": "Contractor Demo",
        "role": "guest",
        "department": "Visitor",
        "qr": "guest_2.svg",
    },
    "17": {
        "owner": "Admin Night Shift",
        "role": "admin",
        "department": "Security Operations",
        "qr": "admin_17.svg",
    },
}


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(text):
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def make_guest_token():
    header = {"alg": "none", "typ": "JWT"}
    payload = {"user": "guest", "role": "guest", "badge_id": "1"}
    return f"{b64url(json.dumps(header, separators=(',', ':')).encode())}.{b64url(json.dumps(payload, separators=(',', ':')).encode())}."


def parse_token(headers):
    cookie = SimpleCookie(headers.get("Cookie", ""))
    token = cookie.get("session")
    if token is None:
        return None
    value = token.value.strip().strip('"')
    parts = value.split(".")
    if len(parts) == 2:
        parts.append("")
    if len(parts) != 3:
        return None
    try:
        header = json.loads(b64url_decode(parts[0]))
        payload = json.loads(b64url_decode(parts[1]))
    except Exception:
        return None
    # Vulnerable on purpose: accepts alg=none and never verifies a signature.
    if header.get("alg") != "none":
        return None
    return payload


def page(title, body):
    return f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="/static/style.css">
  </head>
  <body>{body}</body>
</html>
"""


def index(payload=None):
    if payload:
        cta = '<a class="nav-button" href="/badges">Open badges</a>'
    else:
        cta = '<a class="nav-button" href="/login">Login</a>'
    body = f"""<main class="shell">
      <nav class="site-nav">
        <span class="brand">Badge Printer</span>
        {cta}
      </nav>
      <section class="hero centered">
        <div class="hero-copy">
          <h1>Badge Printer</h1>
          <p class="muted">Print queue and QR badge review for temporary access cards.</p>
        </div>
        <div class="badge-preview" aria-hidden="true">
          <div class="lanyard"></div>
          <div class="badge-card">
            <div class="photo"></div>
            <div class="lines">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div class="mini-qr">
              <i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
            </div>
          </div>
        </div>
      </section>
    </main>"""
    return page("Badge Printer", body)


def login_page(error=""):
    error_html = f'<p class="error">{error}</p>' if error else ""
    body = f"""<main class="shell">
      <nav class="site-nav">
        <span class="brand">Badge Printer</span>
        <a class="nav-button" href="/">Home</a>
      </nav>
      <section class="login-wrap">
        <form class="login-card" method="post" action="/login">
          <p class="eyebrow">Guest access</p>
          <h1>Sign in</h1>
          <label>
            <span>Username</span>
            <input name="username" autocomplete="username" placeholder="guest" required>
          </label>
          <label>
            <span>Password</span>
            <input name="password" type="password" autocomplete="current-password" placeholder="guest" required>
          </label>
          {error_html}
          <button type="submit">Sign in as guest</button>
        </form>
      </section>
    </main>"""
    return page("Login - Badge Printer", body)


def badges_page(payload):
    if not payload:
        return page("Login required", '<main class="shell"><h1>Login required</h1><a href="/login">Login</a></main>')
    if payload.get("role") != "staff":
        return page(
            "Forbidden",
            '<main class="shell"><h1>Staff only</h1><p class="muted">Guest accounts may only view their assigned badge.</p></main>',
        )
    cards = []
    for badge_id in ("1", "2"):
        badge = BADGES[badge_id]
        cards.append(
            f"""<a class="card" href="/badge?id={badge_id}">
          <strong>{badge['owner']}</strong>
          <span>{badge['department']}</span>
          <code>badge #{badge_id}</code>
        </a>"""
        )
    body = f"""<main class="shell">
      <section class="topbar">
        <div>
          <p class="eyebrow">Staff console</p>
          <h1>Badge Queue</h1>
        </div>
        <span class="badge">visible queue: guest badges</span>
      </section>
      <section class="grid">{''.join(cards)}</section>
    </main>"""
    return page("Badge Queue", body)


def badge_page(payload, badge_id):
    if not payload:
        return page("Login required", '<main class="shell"><h1>Login required</h1><a href="/login">Login</a></main>')
    if payload.get("role") != "staff" and payload.get("badge_id") != badge_id:
        return page("Forbidden", '<main class="shell"><h1>Forbidden</h1></main>')
    badge = BADGES.get(badge_id)
    if not badge:
        return page("Not found", '<main class="shell"><h1>Badge not found</h1></main>')
    # IDOR on purpose: staff role can request any badge id, including unlisted admin badge.
    body = f"""<main class="shell">
      <nav><a href="/badges">Back</a></nav>
      <article class="detail">
        <img src="/badge/qr?id={badge_id}" alt="badge QR">
        <div>
          <p class="eyebrow">badge record</p>
          <h1>{badge['owner']}</h1>
          <p class="muted">{badge['department']}</p>
          <code>badge #{badge_id}</code>
          <a class="button" href="/badge/qr?id={badge_id}" download>Download QR SVG</a>
        </div>
      </article>
    </main>"""
    return page("Badge Detail", body)


class Handler(BaseHTTPRequestHandler):
    server_version = "BadgePrinter/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        payload = parse_token(self.headers)

        if path == "/":
            return self.send_bytes(index(payload).encode(), "text/html; charset=utf-8")
        if path == "/login":
            return self.send_bytes(login_page().encode(), "text/html; charset=utf-8")
        if path == "/badges":
            return self.send_bytes(badges_page(payload).encode(), "text/html; charset=utf-8")
        if path == "/badge":
            badge_id = parse_qs(parsed.query).get("id", ["1001"])[0]
            return self.send_bytes(badge_page(payload, badge_id).encode(), "text/html; charset=utf-8")
        if path == "/badge/qr":
            badge_id = parse_qs(parsed.query).get("id", ["1001"])[0]
            badge = BADGES.get(badge_id)
            if not badge:
                return self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
            return self.send_bytes((BADGE_DIR / badge["qr"]).read_bytes(), "image/svg+xml; charset=utf-8")
        if path == "/static/style.css":
            return self.send_bytes((STATIC_DIR / "style.css").read_bytes(), "text/css; charset=utf-8")
        if path == "/healthz":
            return self.send_bytes(b'{"ok": true}\n', "application/json")
        return self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/login":
            return self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        data = parse_qs(body)
        username = data.get("username", [""])[0]
        password = data.get("password", [""])[0]
        if username != "guest" or password != "guest":
            return self.send_bytes(login_page("Invalid guest credentials.").encode(), "text/html; charset=utf-8", HTTPStatus.UNAUTHORIZED)
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Set-Cookie", f"session={make_guest_token()}; Path=/; SameSite=Lax")
        self.send_header("Location", "/")
        self.end_headers()

    def send_bytes(self, data, content_type, status=HTTPStatus.OK):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} - {fmt % args}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8085"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Badge Printer listening on 0.0.0.0:{port}")
    server.serve_forever()
