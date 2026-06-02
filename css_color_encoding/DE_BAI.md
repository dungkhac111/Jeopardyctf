# Đề bài Jeopardy CTF: CSS Color Encoding

## Thông tin chung

**Tên bài:** CSS Color Encoding  
**Chủ đề:** Web Steganography, CSS color encoding  
**Hình thức:** Jeopardy  
**Độ khó đề xuất:** Dễ  
**Flag format:** `blockChainPTIT{}`

## Mô tả

Một web preview theme nội bộ dùng CSS palette để render màu thương hiệu. Trang chính trông bình thường, nhưng legacy theme loader vẫn còn một lỗi đọc file tương đối.

Nhiệm vụ của người chơi là tìm palette nội bộ, khai thác lỗi web để đọc CSS ẩn, sau đó decode dữ liệu được giấu trong mã màu CSS để khôi phục flag theo định dạng `blockChainPTIT{...}`.

## File phát cho người chơi

Các file public nằm trong thư mục `public/`:

```text
HINT.txt
README.md
```

Challenge chính chạy dưới dạng web service:

```text
http://challenge-host:8082
```

Có thể phát cho người chơi file zip public nếu hệ thống yêu cầu attachment:

## Ghi chú cho ban tổ chức

Không đưa thư mục `solution/` cho người chơi. Thư mục này chỉ dùng cho người ra đề/chấm bài, gồm writeup chi tiết và script solve.

Đây là web challenge, cần deploy `src/` bằng `Dockerfile` hoặc `docker-compose.yml`. Trên nền tảng CTF chỉ hiển thị URL challenge và file trong `public/` nếu cần.
