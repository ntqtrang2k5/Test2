import openpyxl
import json
import sys

# Set encoding to utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

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
    for row in sheet.iter_rows(values_only=True):
        # Only take rows that have at least some data
        if any(row):
            file_data.append([str(cell) if cell is not None else "" for cell in row])
    all_data[file] = file_data

with open("scratch/excel_full_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("Done")
