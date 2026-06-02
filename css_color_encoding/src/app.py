import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
THEME_DIR = BASE_DIR / "themes"


def page():
    return """<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Palette Preview</title>
    <link rel="stylesheet" href="/theme?file=default.css">
  </head>
  <body>
    <main class="shell">
      <section class="topbar">
        <div>
          <p class="eyebrow">Brand system</p>
          <h1>Palette Preview</h1>
        </div>
        <span class="badge">theme: default</span>
      </section>
      <section class="palette">
        <div class="card accent-a"><span></span><strong>Signal Red</strong><small>public token color</small></div>
        <div class="card accent-b"><span></span><strong>Queue Blue</strong><small>operator UI color</small></div>
        <div class="card accent-c"><span></span><strong>Audit Green</strong><small>log review color</small></div>
        <div class="card accent-d"><span></span><strong>Archive Gold</strong><small>retention color</small></div>
      </section>
    </main>
  </body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "PalettePreview/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            return self.send_bytes(page().encode(), "text/html; charset=utf-8")
        if path == "/healthz":
            return self.send_bytes(b'{"ok": true}\n', "application/json")
        if path == "/robots.txt":
            return self.send_bytes(b"User-agent: *\nDisallow: /debug/\n", "text/plain; charset=utf-8")
        if path == "/debug/theme":
            name = parse_qs(parsed.query).get("name", ["default"])[0]
            data = {
                "name": name,
                "loader": "/theme?file=default.css",
                "note": "legacy loader accepts relative theme filenames for migration tests",
            }
            if name == "internal":
                data["archived_palette"] = "../private/internal-palette.css"
            return self.send_bytes(json.dumps(data, indent=2).encode(), "application/json")
        if path == "/theme":
            filename = parse_qs(parsed.query).get("file", ["default.css"])[0]
            # Vulnerable on purpose: legacy loader joins paths without resolving or constraining them.
            target = THEME_DIR / filename
            if not target.is_file():
                return self.send_bytes(b"theme not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
            return self.send_bytes(target.read_bytes(), "text/css; charset=utf-8")

        self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)

    def send_bytes(self, data, content_type, status=HTTPStatus.OK):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} - {fmt % args}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8082"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Palette Preview listening on 0.0.0.0:{port}")
    server.serve_forever()
