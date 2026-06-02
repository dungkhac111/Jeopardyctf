# Metadata Gallery - Writeup

## 1. Khảo sát web

Trang chủ là một gallery ảnh nội bộ. Ảnh được render bình thường và không có flag trong HTML.

Kiểm tra `robots.txt`:

```bash
curl http://127.0.0.1:8080/robots.txt
```

Kết quả có thư mục bị chặn:

```text
Disallow: /archive/
```

## 2. Xem header của ảnh thumbnail

Ảnh trên trang được load từ endpoint `/static-view/<id>`. Kiểm tra header:

```bash
curl -I http://127.0.0.1:8080/static-view/silent-lake
```

Header đáng chú ý:

```text
X-Origin-Path: /archive/original?id=silent-lake
```

Điều này cho biết thumbnail là bản đã được sanitizer/cache xử lý, còn bản gốc nằm trong archive.

## 3. Tải file gốc

```bash
curl -o lake_original.png "http://127.0.0.1:8080/archive/original?id=silent-lake"
```

File này vẫn là PNG hợp lệ. Tuy nhiên flag không nằm trực tiếp trong pixel.

## 4. Phân tích metadata PNG

PNG gồm nhiều chunk. Các chunk dạng text như `tEXt` có thể chứa metadata:

```text
length | type | data | crc
```

Khi parse file gốc, có chunk:

```text
tEXt archive.note=<base64>
```

Giá trị này là dữ liệu đã XOR bằng key 1 byte rồi base64.

## 5. Giải mã

Brute force key XOR 1 byte và tìm chuỗi bắt đầu bằng `blockChainPTIT{`:

```python
raw = base64.b64decode(value)
for key in range(256):
    text = bytes(byte ^ key for byte in raw)
    if text.startswith(b"blockChainPTIT{"):
        print(text.decode())
```

Kết quả:

```text
blockChainPTIT{web_cache_metadata_leak}
```

Flag:

```text
blockChainPTIT{web_cache_metadata_leak}
```
