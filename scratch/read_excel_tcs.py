import openpyxl
import json
import sys

file_path = r'D:\03_Projects\LTW\Test2\01_TaiLieu\TC_ThemThongTinXe.xlsx'
sys.stdout.reconfigure(encoding='utf-8')

try:
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    
    rows = list(sheet.rows)
    new_tcs = []
    for i, row in enumerate(rows):
        vals = [str(cell.value) if cell.value else "" for cell in row]
        if len(vals) > 2 and "TC-XE-G" in vals[2]:
            new_tcs.append({
                "id": vals[2].strip(),
                "scenario": vals[3].strip(),
                "steps": vals[4].strip(),
                "condition": vals[5].strip(),
                "expected": vals[6].strip(),
                "data": vals[8].strip() if len(vals) > 8 else ""
            })
            
    print(json.dumps(new_tcs, ensure_ascii=False, indent=2))
        
except Exception as e:
    print(f"Error: {e}")
