import pandas as pd
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def read_exact_gui(file_path):
    df = pd.read_excel(file_path, header=None)
    # The GUI section starts around row 25
    # Let's look at the range where ID starts with TC-XE-G
    for i in range(25, 60):
        try:
            row = df.iloc[i]
            id_val = str(row[2])
            if 'TC-XE-G' in id_val:
                print(f"ROW {i} | ID: {id_val} | Name: {row[3]} | Step: {row[4]} | Expected: {row[6]}")
        except:
            pass

if __name__ == "__main__":
    read_exact_gui(r"d:\03_Projects\LTW\Test2\01_TaiLieu\TC_XoaThongTinXe.xlsx")
