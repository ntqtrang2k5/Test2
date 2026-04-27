import openpyxl
import json
import sys

file_path = r'D:\03_Projects\LTW\Test2\01_TaiLieu\TC_ChinhSuaThongTinXe.xlsx'
sys.stdout.reconfigure(encoding='utf-8')

try:
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    
    rows = list(sheet.rows)
    test_cases = []
    for i, row in enumerate(rows):
        vals = [str(cell.value) if cell.value else "" for cell in row]
        # Look for Test Case ID (TC-XE-U*)
        if len(vals) > 2 and "TC-XE-U" in vals[2]:
            test_cases.append({
                "id": vals[2].strip(),
                "scenario": vals[3].strip(),
                "steps": vals[4].strip(),
                "condition": vals[5].strip(),
                "expected": vals[6].strip(),
                "data": vals[8].strip() if len(vals) > 8 else ""
            })
            
    print(json.dumps(test_cases, ensure_ascii=False, indent=2))
        
except Exception as e:
    print(f"Error: {e}")
