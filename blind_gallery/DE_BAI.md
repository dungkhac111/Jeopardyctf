# Đề bài Jeopardy CTF: Blind Gallery

## Thông tin chung

**Tên bài:** Blind Gallery  
**Chủ đề:** SQL Injection, Web Steganography, steghide  
**Hình thức:** Jeopardy  
**Độ khó đề xuất:** Trung bình  
**Flag format:** `blockChainPTIT{}`

## Mô tả

Một gallery ảnh nội bộ chỉ hiển thị ảnh public. Backend dùng SQLite và endpoint xem ảnh có lỗi SQL Injection.

Trong bảng `images` có nhiều ảnh, bao gồm một ảnh archive không public. Nhiệm vụ của người chơi là khai thác SQL Injection để tìm filename và passphrase, tải ảnh archive, sau đó dùng kỹ thuật steganography phù hợp để khôi phục flag theo định dạng `blockChainPTIT{...}`.

## File phát cho người chơi

Các file public nằm trong thư mục `public/`:

```text
HINT.txt
README.md
```

Challenge chính chạy dưới dạng web service:

```text
http://challenge-host:8084
```

Có thể phát cho người chơi file zip public nếu hệ thống yêu cầu attachment:
## Ghi chú cho ban tổ chức

Không đưa thư mục `solution/` cho người chơi. Thư mục này chỉ dùng cho người ra đề/chấm bài, gồm writeup chi tiết và script solve.

Đây là web challenge, cần deploy `src/` bằng `Dockerfile` hoặc `docker-compose.yml`. Trên nền tảng CTF chỉ hiển thị URL challenge và file trong `public/` nếu cần.
