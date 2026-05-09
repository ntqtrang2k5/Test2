import openpyxl
import json
import sys
from datetime import datetime

# Set encoding to utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

files = [
    "01_TaiLieu/TC_ChinhSuaThongTinXe.xlsx",
    "01_TaiLieu/TC_ThemThongTinXe.xlsx",
    "01_TaiLieu/TC_XemVaLocThongTinXe.xlsx",
    "01_TaiLieu/TC_XoaThongTinXe.xlsx"
]

all_data = {}

for file in files:
    wb = openpyxl.load_workbook(file, data_only=True)
    sheet = wb.active
    file_data = []
    for row in sheet.iter_rows(min_row=1, max_row=10, values_only=True):
        # Convert row values to serializable types
        serializable_row = [json_serial(cell) if cell is not None else None for cell in row]
        file_data.append(serializable_row)
    all_data[file] = file_data

with open("scratch/excel_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("Done")
