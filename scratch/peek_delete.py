import pandas as pd
import sys

# Ensure UTF-8 output for terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\03_Projects\LTW\Test2\01_TaiLieu\TC_XoaThongTinXe.xlsx"

def peek_excel():
    xl = pd.ExcelFile(file_path)
    for sheet in xl.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = pd.read_excel(file_path, sheet_name=sheet)
        print(df.head(50).to_string())

if __name__ == "__main__":
    peek_excel()
