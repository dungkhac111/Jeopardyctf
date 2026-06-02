# Đề bài Jeopardy CTF: Badge Printer

## Thông tin chung

**Tên bài:** Badge Printer  
**Chủ đề:** JWT misconfiguration, IDOR, QR steganography  
**Hình thức:** Jeopardy  
**Độ khó đề xuất:** Trung bình  
**Flag format:** `blockChainPTIT{}`

## Mô tả

Hệ thống in badge nội bộ cho phép guest đăng nhập để xem badge demo. JWT của hệ thống dùng cấu hình yếu, và trang badge có lỗi IDOR.

Queue staff chỉ hiển thị vài badge bình thường, nhưng badge admin nằm ở một ID khác. Nhiệm vụ của người chơi là nâng quyền vào khu staff, brute force ID badge admin, sau đó quét QR để khôi phục flag theo định dạng `blockChainPTIT{...}`.

## File phát cho người chơi

Các file public nằm trong thư mục `public/`:

```text
HINT.txt
README.md
```

Challenge chính chạy dưới dạng web service:

```text
http://challenge-host:8085
```

Có thể phát cho người chơi file zip public nếu hệ thống yêu cầu attachment:
## Ghi chú cho ban tổ chức

Không đưa thư mục `solution/` cho người chơi. Thư mục này chỉ dùng cho người ra đề/chấm bài, gồm writeup chi tiết và script solve.

Đây là web challenge, cần deploy `src/` bằng `Dockerfile` hoặc `docker-compose.yml`. Trên nền tảng CTF chỉ hiển thị URL challenge và file trong `public/` nếu cần.
