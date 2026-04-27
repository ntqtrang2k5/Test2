import pandas as pd
import os
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\03_Projects\LTW\Test2\01_TaiLieu\TC_XoaThongTinXe.xlsx"
output_path = r"d:\03_Projects\LTW\Test2\scratch\delete_car_tc.md"

def read_excel():
    xl = pd.ExcelFile(file_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Test Cases: Xóa Thông Tin Xe\n\n")
        
        for sheet in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            f.write(f"# Sheet: {sheet}\n\n")
            
            # Map columns by content for this specific sheet
            # ID is usually in col 2 or 3
            # In the peek, it was col index 2 (df.iloc[:, 2])
            
            for index, row in df.iterrows():
                # Search for ID in col index 2
                id_val = str(row.iloc[2]) if not pd.isna(row.iloc[2]) else ""
                
                if "TC-XE-" in id_val:
                    title = str(row.iloc[3]) if not pd.isna(row.iloc[3]) else ""
                    steps = str(row.iloc[4]) if not pd.isna(row.iloc[4]) else ""
                    # Steps might continue in next row if ID is empty
                    
                    # Look ahead for more steps
                    next_idx = index + 1
                    while next_idx < len(df) and pd.isna(df.iloc[next_idx, 2]) and not pd.isna(df.iloc[next_idx, 4]):
                        steps += "\n" + str(df.iloc[next_idx, 4])
                        next_idx += 1
                        
                    expected = str(row.iloc[6]) if not pd.isna(row.iloc[6]) else ""
                    # Also check col index 7 or 8 for expected results in some sheets
                    if expected == "nan" or expected == "":
                        expected = str(row.iloc[7]) if not pd.isna(row.iloc[7]) else ""

                    f.write(f"## {id_val}: {title}\n")
                    f.write(f"**Steps:**\n{steps}\n\n")
                    f.write(f"**Expected:**\n{expected}\n\n")
                    f.write("---\n\n")

    print(f"Extracted to {output_path}")

if __name__ == "__main__":
    read_excel()
