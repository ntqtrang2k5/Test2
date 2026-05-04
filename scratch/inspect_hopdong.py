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

file = "01_TaiLieu/TC_HopDong.xlsx"

all_data = {}

wb = openpyxl.load_workbook(file, data_only=True)
sheet = wb.active
file_data = []
for row in sheet.iter_rows(min_row=1, max_row=20, values_only=True):
    serializable_row = [json_serial(cell) if cell is not None else None for cell in row]
    file_data.append(serializable_row)

with open("scratch/hopdong_excel_inspect.json", "w", encoding="utf-8") as f:
    json.dump(file_data, f, ensure_ascii=False, indent=2)

print("Done")
