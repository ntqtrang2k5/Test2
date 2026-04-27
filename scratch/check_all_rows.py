import pandas as pd
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def check_all_rows(file_path):
    df = pd.read_excel(file_path, header=None)
    for i in range(30, 55):
        print(f"ROW {i}: {df.iloc[i].tolist()}")

if __name__ == "__main__":
    check_all_rows(r"d:\03_Projects\LTW\Test2\01_TaiLieu\TC_XoaThongTinXe.xlsx")
