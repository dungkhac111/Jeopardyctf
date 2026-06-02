# Đề bài Jeopardy CTF: Metadata Gallery

## Thông tin chung

**Tên bài:** Metadata Gallery  
**Chủ đề:** Web Steganography, PNG metadata  
**Hình thức:** Jeopardy  
**Độ khó đề xuất:** Dễ  
**Flag format:** `blockChainPTIT{}`

## Mô tả

SOC nhận được một web gallery nội bộ dùng để lưu ảnh hiện trường. Giao diện chỉ hiển thị thumbnail đã được làm sạch, nhưng hệ thống cache/CDN vẫn để lại dấu vết về bản gốc.

Nhiệm vụ của người chơi là khai thác các manh mối từ web response, tìm file ảnh gốc và phân tích metadata PNG để khôi phục flag theo định dạng `blockChainPTIT{...}`.

## File phát cho người chơi

Các file public nằm trong thư mục `public/`:

```text
HINT.txt
README.md
```

Challenge chính chạy dưới dạng web service:

```text
http://challenge-host:8080
```

Có thể phát cho người chơi file zip public nếu hệ thống yêu cầu attachment:

## Ghi chú cho ban tổ chức

Không đưa thư mục `solution/` cho người chơi. Thư mục này chỉ dùng cho người ra đề/chấm bài, gồm writeup chi tiết và script solve.

Đây là web challenge, cần deploy `src/` bằng `Dockerfile` hoặc `docker-compose.yml`. Trên nền tảng CTF chỉ hiển thị URL challenge và file trong `public/` nếu cần.
