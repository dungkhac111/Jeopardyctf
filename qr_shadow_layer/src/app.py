import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def page():
    return """<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>QR Shadow Layer</title>
    <link rel="stylesheet" href="/static/style.css">
  </head>
  <body>
    <main class="shell">
      <section class="panel">
        <div class="copy">
          <p class="eyebrow">Internal token handoff</p>
          <h1>QR Shadow Layer</h1>
          <p class="muted">Scan the QR for the handoff token. The original web render is kept for audit.</p>
          <a class="button" href="/static/qr_shadow.svg" download>Download QR asset</a>
        </div>
        <div class="qr-box">
          <img src="/static/qr_shadow.svg" alt="handoff QR code">
        </div>
      </section>
    </main>
  </body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "QRShadow/1.1"

    def do_GET(self):
        if self.path == "/":
            return self.send_bytes(page().encode(), "text/html; charset=utf-8")
        if self.path == "/healthz":
            return self.send_bytes(b'{"ok": true}\n', "application/json")
        if self.path == "/static/style.css":
            return self.send_file(STATIC_DIR / "style.css", "text/css; charset=utf-8")
        if self.path == "/static/qr_shadow.svg":
            return self.send_file(STATIC_DIR / "qr_shadow.svg", "image/svg+xml; charset=utf-8")
        if self.path == "/static/qr_visible.png":
            return self.send_file(STATIC_DIR / "qr_visible.png", "image/png")
        self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)

    def send_file(self, path, content_type):
        if not path.is_file():
            return self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
        self.send_bytes(path.read_bytes(), content_type)

    def send_bytes(self, data, content_type, status=HTTPStatus.OK):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} - {fmt % args}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8081"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"QR Shadow Layer listening on 0.0.0.0:{port}")
    server.serve_forever()
