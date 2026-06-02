# Đề bài Jeopardy CTF: Tri-Modal Stego Web

## Thông tin chung

**Tên bài:** Tri-Modal Stego Web  
**Chủ đề:** Web Steganography, EXIF, PNG LSB, audio spectrogram  
**Hình thức:** Jeopardy  
**Độ khó đề xuất:** Trung bình  
**Flag format:** `blockChainPTIT{}`

## Mô tả

Một portal forensics nội bộ lưu các bằng chứng media theo case. Trang chính chỉ cho xem file public, nhưng API migration cũ vẫn để lộ manifest và có lỗi đọc file tương đối.

Nhiệm vụ của người chơi là khai thác web để lấy đủ các bằng chứng nội bộ, sau đó phân tích nhiều kênh giấu tin khác nhau gồm EXIF, LSB ảnh PNG và audio spectrogram để khôi phục flag theo định dạng `blockChainPTIT{...}`.

## File phát cho người chơi

Các file public nằm trong thư mục `public/`:

```text
HINT.txt
README.md
```

Challenge chính chạy dưới dạng web service:

```text
http://challenge-host:8083
```

Có thể phát cho người chơi file zip public nếu hệ thống yêu cầu attachment:

```text
tri_modal_stego_web_public.zip
```

## Ghi chú cho ban tổ chức

Không đưa thư mục `solution/` cho người chơi. Thư mục này chỉ dùng cho người ra đề/chấm bài, gồm writeup chi tiết và script solve.

Đây là web challenge, cần deploy `src/` bằng `Dockerfile` hoặc `docker-compose.yml`. Trên nền tảng CTF chỉ hiển thị URL challenge và file trong `public/` nếu cần.
