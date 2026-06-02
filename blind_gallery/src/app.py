import html
import os
import sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "media"


def connect_db():
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute(
        """
        CREATE TABLE images (
          id INTEGER PRIMARY KEY,
          title TEXT,
          filename TEXT,
          is_public INTEGER,
          description TEXT
        )
        """
    )
    db.executemany(
        "INSERT INTO images(id, title, filename, is_public, description) VALUES(?, ?, ?, ?, ?)",
        [
            (1, "Morning Atrium", "atrium.jpg", 1, "public lobby capture"),
            (2, "Server Corner", "server_corner.jpg", 1, "sanitized infrastructure photo"),
            (3, "Badge Desk", "badge_desk.jpg", 1, "front desk record"),
            (4, "Archive 713", "archive_713.jpg", 0, "passphrase: night-shift-713"),
            (5, "Old Parking Feed", "parking_feed.jpg", 0, "retired camera feed, no attachment"),
            (6, "Broken Turnstile", "turnstile.jpg", 0, "maintenance only"),
        ],
    )
    return db


DB = connect_db()


def page(body, title="Blind Gallery"):
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


def index_page():
    rows = DB.execute("SELECT id, title, filename, description FROM images WHERE is_public = 1").fetchall()
    cards = []
    for image_id, title, filename, description in rows:
        cards.append(
            f"""<a class="card" href="/image?id={image_id}">
          <img src="/download?file={html.escape(filename)}" alt="{html.escape(title)}">
          <div>
            <h2>{html.escape(title)}</h2>
            <p>{html.escape(description)}</p>
          </div>
        </a>"""
        )
    body = f"""<main class="shell">
      <section class="topbar">
        <div>
          <p class="eyebrow">Internal photo review</p>
          <h1>Blind Gallery</h1>
        </div>
        <span class="badge">public images only</span>
      </section>
      <section class="grid">{''.join(cards)}</section>
    </main>"""
    return page(body)


def image_page(image_id):
    # Vulnerable on purpose: id is concatenated into SQL.
    query = (
        "SELECT title, filename, description FROM images "
        f"WHERE id = '{image_id}' AND is_public = 1"
    )
    try:
        rows = DB.execute(query).fetchall()
    except sqlite3.Error as exc:
        rows = [("SQL error", "", str(exc))]

    cards = []
    for title, filename, description in rows:
        safe_title = html.escape(str(title))
        safe_filename = html.escape(str(filename))
        safe_description = html.escape(str(description))
        image = ""
        if safe_filename:
            image = f'<img src="/download?file={safe_filename}" alt="{safe_title}">'
        cards.append(
            f"""<article class="detail">
          {image}
          <div>
            <p class="eyebrow">image record</p>
            <h1>{safe_title}</h1>
            <p>{safe_description}</p>
            <code>{safe_filename}</code>
          </div>
        </article>"""
        )
    if not cards:
        cards.append('<article class="detail"><div><h1>No image</h1><p>No public image matched this id.</p></div></article>')
    return page(f'<main class="shell"><nav><a href="/">Back</a></nav>{"".join(cards)}</main>', "Image Detail")


class Handler(BaseHTTPRequestHandler):
    server_version = "BlindGallery/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            return self.send_bytes(index_page().encode(), "text/html; charset=utf-8")
        if path == "/image":
            image_id = parse_qs(parsed.query).get("id", ["1"])[0]
            return self.send_bytes(image_page(image_id).encode(), "text/html; charset=utf-8")
        if path == "/download":
            filename = parse_qs(parsed.query).get("file", [""])[0]
            # Download intentionally allows any basename present in media.
            target = MEDIA_DIR / Path(filename).name
            if not target.is_file():
                return self.send_bytes(b"file not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
            return self.send_bytes(target.read_bytes(), guess_type(target))
        if path == "/static/style.css":
            return self.send_bytes((BASE_DIR / "static" / "style.css").read_bytes(), "text/css; charset=utf-8")
        if path == "/healthz":
            return self.send_bytes(b'{"ok": true}\n', "application/json")
        return self.send_bytes(b"not found\n", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)

    def send_bytes(self, data, content_type, status=HTTPStatus.OK):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(f"{self.client_address[0]} - {fmt % args}")


def guess_type(path):
    if path.suffix.lower() in (".jpg", ".jpeg"):
        return "image/jpeg"
    if path.suffix.lower() == ".css":
        return "text/css; charset=utf-8"
    if path.suffix.lower() == ".txt":
        return "text/plain; charset=utf-8"
    return "application/octet-stream"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8084"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Blind Gallery listening on 0.0.0.0:{port}")
    server.serve_forever()
