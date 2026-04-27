import openpyxl
import json

def read_sheet(file_path, sheet_name):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb[sheet_name]
    data = []
    for row in sheet.iter_rows(values_only=True):
        # Only add rows that have at least one non-null value
        if any(cell is not None for cell in row):
            data.append(row)
    return data

file_path = r"d:\03_Projects\LTW\Test2\01_TaiLieu\TC_ChinhSuaThongTinXe.xlsx"
sheet_name = "Chỉnh Sửa Thông Tin Xe"
content = read_sheet(file_path, sheet_name)

with open(r"d:\03_Projects\LTW\Test2\scratch\edit_car_tc.json", "w", encoding="utf-8") as f:
    json.dump(content, f, ensure_ascii=False, indent=2)
print("Saved to scratch/edit_car_tc.json")
