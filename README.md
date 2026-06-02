# Web Steganography Jeopardy CTF Labs

Thư mục này chứa các lab Web Steganography ở dạng Jeopardy CTF.

Mỗi challenge được đóng gói theo format:

```text
<challenge>/
  challenge.yml      Metadata để đưa nên nền tảng CTF
  Dockerfile         Build web service
  docker-compose.yml Chạy challenge local/deploy
  public/            File/hint phat cho người chơi nếu cần
  src/               Source web challenge và asset
  solution/          Writeup và script solve cho giảng viên
```

## Danh sách challenge

| STT | Tên | Kỹ thuật | Flag | Độ khó CTF |
|---|---|---|---|---|
| 01 | Metadata Gallery | Web cache/header leak + PNG metadata `tEXt` + XOR/base64 | `blockChainPTIT{web_cache_metadata_leak}` | Dễ |
| 02 | QR Shadow Layer | QR scan lấy part 1 + SVG shadow layer encode bit bằng màu `#010101/#020202` | `blockChainPTIT{qr_shadow_layer}` | Dễ |
| 03 | CSS Color Encoding | Web LFI/path traversal đọc CSS nội bộ + decode màu `#xx0000` thành ASCII | `blockChainPTIT{css_palette_lfi}` | Dễ |
| 04 | Tri-Modal Stego Web | Web API enum + LFI lấy evidence + EXIF + PNG LSB + audio spectrogram | `blockChainPTIT{tri_modal_stego_web}` | Trung bình |
| 05 | Blind Gallery | SQL Injection đọc bảng `images` + leak filename/passphrase + `steghide` trong JPEG | `blockChainPTIT{sqli_steghide_gallery}` | Trung bình |
| 06 | Badge Printer | JWT `alg=none` + IDOR brute force badge admin + QR chứa flag | `blockChainPTIT{jwt_idor_qr_badge}` | Dễ |

## Gợi ý triển khai

Khi đưa lên hệ thống CTF:

- Deploy web service bằng `Dockerfile` hoặc `docker-compose.yml`.
- Trên nền tẳng CTF, chỉ hiển thị URL challenge và các file trong `public/` nếu cần.
- Không upload hoặc công khai các thư mục `solution/` cho người chơi.
- Không công khai `challenge.yml` nếu nền tảng tự quản lý flag.
- Thư mục `src/` là source deploy service,không nên phát trực tiếp cho người chơi trừ khi bài yêu cầu source review.

## Chay local

Vi du chay mot challenge:

```bash
cd tri_modal_stego_web
docker compose up --build
```

Sau đó mở URL tương ứng trong `challenge.yml`, ví dụ:

```text
http://127.0.0.1:8083
```
