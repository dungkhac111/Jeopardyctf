import re

# 1. Đọc nội dung file SVG (hoặc copy trực tiếp block shadow-layer vào một file txt)
with open('qr_shadow.svg', 'r') as f:
    data = f.read()

# 2. Dùng Regex để tìm tất cả các mã màu trong thẻ có class "shadow-cell"
# Trích xuất ra danh sách các mã hex: '020202', '010101', ...
colors = re.findall(r'<rect class="shadow-cell" .*? fill="#(010101|020202)"/>', data)

# 3. Chuyển đổi màu thành chuỗi nhị phân
binary_string = ""
for color in colors:
    if color == '010101':
        binary_string += '1'
    elif color == '020202':
        binary_string += '0'

# 4. Gom mỗi 8 bit thành 1 byte và chuyển sang mã ASCII
flag_part_2 = ""
for i in range(0, len(binary_string), 8):
    byte = binary_string[i:i+8]
    if len(byte) == 8:
        flag_part_2 += chr(int(byte, 2))

print(f"[+] Phần 2 của Flag là: {flag_part_2}")