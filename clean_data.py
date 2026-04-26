import json
import re

# Đọc file data.json gốc
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Hàm quét và cắt bỏ phần giờ phút giây
def clean_dates(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
                # Chỉ lấy 10 ký tự đầu (YYYY-MM-DD)
                obj[key] = value[:10]
            else:
                clean_dates(value)
    elif isinstance(obj, list):
        for item in obj:
            clean_dates(item)

# Tiến hành dọn dẹp
clean_dates(data)

# Lưu lại vào file mới hoặc ghi đè file cũ
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Đã dọn dẹp xong định dạng ngày tháng trong file data.json!")