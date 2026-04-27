import openpyxl
import os

def read_excel(file_path, output_file):
    output_file.write(f"--- Reading {os.path.basename(file_path)} ---\n")
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    for row in sheet.iter_rows(values_only=True):
        output_file.write(str(row) + "\n")
    output_file.write("\n")

docs_dir = r"D:\03_Projects\LTW\Test2\01_TaiLieu"
with open(r"D:\03_Projects\LTW\Test2\scratch\tcs_output.txt", "w", encoding="utf-8") as f:
    read_excel(os.path.join(docs_dir, "TC_ThemThongTinXe.xlsx"), f)
    read_excel(os.path.join(docs_dir, "TC_ChinhSuaThongTinXe.xlsx"), f)
