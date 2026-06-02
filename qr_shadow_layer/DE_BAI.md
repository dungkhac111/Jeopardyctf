# Đề bài Jeopardy CTF: QR Shadow Layer

## Thông tin chung

**Tên bài:** QR Shadow Layer  
**Chủ đề:** Web Steganography, QR/SVG hidden layer  
**Hình thức:** Jeopardy  
**Độ khó đề xuất:** Dễ  
**Flag format:** `blockChainPTIT{}`

## Mô tả

Website hiển thị một QR code dùng cho việc bàn giao token nội bộ. Khi quét QR, người chơi chỉ nhận được một phần dữ liệu.

Tuy nhiên QR này được render bởi web và có một lớp dữ liệu mờ nằm chồng lên mã gốc. Nhiệm vụ của người chơi là quét QR, phân tích asset SVG và khôi phục flag theo định dạng `blockChainPTIT{...}`.

## File phát cho người chơi

Các file public nằm trong thư mục `public/`:

```text
HINT.txt
README.md
```

Challenge chính chạy dưới dạng web service:

```text
http://challenge-host:8081
```

Có thể phát cho người chơi file zip public nếu hệ thống yêu cầu attachment:

```text
qr_shadow_layer_public.zip
```

## Ghi chú cho ban tổ chức

Không đưa thư mục `solution/` cho người chơi. Thư mục này chỉ dùng cho người ra đề/chấm bài, gồm writeup chi tiết và script solve.

Đây là web challenge, cần deploy `src/` bằng `Dockerfile` hoặc `docker-compose.yml`. Trên nền tảng CTF chỉ hiển thị URL challenge và file trong `public/` nếu cần.
