# QR Shadow Layer - Writeup

## 1. Quét QR

Trang web hiển thị một QR code chuẩn. Quét bằng điện thoại, Burp browser screenshot, hoặc tool đọc QR sẽ nhận được:

```text
flag_part_1=blockChainPTIT{qr_
```

Đây chỉ là phần đầu của flag.

## 2. Tải asset SVG

QR được render từ:

```text
/static/qr_shadow.svg
```

Tải file:

```bash
curl -o qr_shadow.svg http://127.0.0.1:8081/static/qr_shadow.svg
```

## 3. Phân tích shadow layer

Trong SVG có QR visible là ảnh PNG nhúng base64. Ngoài ra còn một layer rất mờ:

```xml
<g id="shadow-layer" opacity="0.035">
```

Các ô `rect.shadow-cell` dùng màu gần như giống nhau:

```text
#010101 -> bit 1
#020202 -> bit 0
```

Sắp xếp các rect theo `x`, sau đó `y`, lấy bit từ màu fill và ghép mỗi 8 bit thành ASCII.

Byte 1 (Từ x=206 đến x=220):
```text
Màu: 02, 01, 01, 01, 02, 02, 01, 01

Nhị phân: 01110011

Ký tự ASCII: s
```
Byte 2 (Từ x=222 đến x=236):
```text
Màu: 02, 01, 01, 02, 01, 02, 02, 02

Nhị phân: 01101000

Ký tự ASCII: h
```
Byte 3 (Từ x=238 đến x=252):
```text
Màu: 02, 01, 01, 02, 02, 02, 02, 01

Nhị phân: 01100001

Ký tự ASCII: a
```
Byte 4 (Từ x=254 đến x=268):
```text
Màu: 02, 01, 01, 02, 02, 01, 02, 02

Nhị phân: 01100100

Ký tự ASCII: d
```
Byte 5 (Từ x=270 đến x=284):
```text
Màu: 02, 01, 01, 02, 01, 01, 01, 01

Nhị phân: 01101111

Ký tự ASCII: o
```
Byte 6 (Từ x=286 đến x=300):
```text
Màu: 02, 01, 01, 01, 02, 01, 01, 01

Nhị phân: 01110111

Ký tự ASCII: w
```
Byte 7 (Từ x=302 đến x=316):
```text
Màu: 02, 01, 02, 01, 01, 01, 01, 01

Nhị phân: 01011111

Ký tự ASCII: _ (dấu gạch dưới)
```
Byte 8 (Từ x=318 đến x=332):
```text
Màu: 02, 01, 01, 02, 01, 01, 02, 02

Nhị phân: 01101100

Ký tự ASCII: l
```
Byte 9 (Từ x=334 đến x=348):
```text
Màu: 02, 01, 01, 02, 02, 02, 02, 01

Nhị phân: 01100001

Ký tự ASCII: a
```
Byte 10 (Từ x=350 đến x=364):
```text
Màu: 02, 01, 01, 01, 01, 02, 02, 01

Nhị phân: 01111001

Ký tự ASCII: y
```
Byte 11 (Từ x=366 đến x=380):
```text
Màu: 02, 01, 01, 02, 02, 01, 02, 01

Nhị phân: 01100101

Ký tự ASCII: e
```
Byte 12 (Từ x=382 đến x=396):
```text
Màu: 02, 01, 01, 01, 02, 02, 01, 02

Nhị phân: 01110010

Ký tự ASCII: r
```
Byte 13 (Từ x=398 đến x=412):
```text
Màu: 02, 01, 01, 01, 01, 01, 02, 01

Nhị phân: 01111101

Ký tự ASCII: }
```
Kết quả:

```text
shadow_layer}
```

## 4. Ghép flag

Ghép payload QR với dữ liệu trong shadow layer:

```text
blockChainPTIT{qr_shadow_layer}
```
