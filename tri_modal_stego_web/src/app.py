import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public_assets"


def page():
    return """<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Case Media Portal</title>
    <link rel="stylesheet" href="/static/style.css">
  </head>
  <body>
    <main class="shell">
      <section class="topbar">
        <div>
          <p class="eyebrow">Forensics media portal</p>
          <h1>Case Media Portal</h1>
        </div>
        <span class="badge">case: public-demo</span>
      </section>
      <section class="grid">
        <article class="card">
          <img src="/asset?name=cover.png" alt="public preview">
          <div>
            <h2>Public Preview</h2>
            <p>Only sanitized media is listed here. Migration API keeps older case manifests for audit.</p>
            <a href="/asset?name=cover.png" download>Download preview</a>
          </div>
        </article>
      </section>
    </main>
  </body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "CasePortal/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            return self.send_bytes(page().encode(), "text/html; charset=utf-8")
        if path == "/static/style.css":
            return self.send_file(BASE_DIR / "static" / "style.css", "text/css; charset=utf-8")
        if path == "/healthz":
            return self.send_bytes(b'{"ok": true}\n', "application/json")
        if path == "/robots.txt":
            return self.send_bytes(b"User-agent: *\nDisallow: /api/\n", "text/plain; charset=utf-8")
        if path == "/api/" or path == "/api":
            data = {
                "service": "case media api",
                "version": "legacy-migration",
                "routes": [
                    "/api/status",
                    "/api/manifest?case=public-demo",
                ],
                "migration_note": "old incident case 713 was archived after media review",
            }
            return self.send_bytes(json.dumps(data, indent=2).encode(), "application/json")
        if path == "/api/status":
            data = {
                "ok": True,
                "public_case": "public-demo",
                "archived_cases": ["713"],
            }
            return self.send_bytes(json.dumps(data, indent=2).encode(), "application/json")
        if path == "/api/manifest":
            case_id = parse_qs(parsed.query).get("case", ["public-demo"])[0]
            data = {
                "case": case_id,
                "public_asset": "/asset?name=cover.png",
                "legacy_fetch": "/asset?name=<relative-file>",
                "archived_case_dir": "../private/case-713/",
                "evidence": ["photo.jpg", "mask.png", "signal.wav"],
                "note": "relative paths are accepted for compatibility with the old evidence sync job",
            }
            return self.send_bytes(json.dumps(data, indent=2).encode(), "application/json")
        if path == "/asset":
            filename = parse_qs(parsed.query).get("name", ["cover.png"])[0]
            # Vulnerable on purpose: no path normalization or base-dir containment check.
            target = PUBLIC_DIR / filename
            if not target.is_file():
                return self.send_bytes(b"asset not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
            return self.send_file(target, guess_type(target))

        self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)

    def send_file(self, path, content_type):
        self.send_bytes(path.read_bytes(), content_type)

    def send_bytes(self, data, content_type, status=HTTPStatus.OK):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} - {fmt % args}")


def guess_type(path):
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix in (".jpg", ".jpeg"):
        return "image/jpeg"
    if suffix == ".wav":
        return "audio/wav"
    if suffix == ".css":
        return "text/css; charset=utf-8"
    return "application/octet-stream"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8083"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Case Media Portal listening on 0.0.0.0:{port}")
    server.serve_forever()
