import pandas as pd
import glob
import os

def search_excels(keyword):
    files = glob.glob(r"d:\03_Projects\LTW\Test2\01_TaiLieu\*.xlsx")
    for f in files:
        print(f"Checking {os.path.basename(f)}...")
        try:
            df = pd.read_excel(f, header=None)
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    val = str(df.iloc[i, j])
                    if keyword.lower() in val.lower():
                        print(f"  Row {i} Col {j}: {val}")
        except Exception as e:
            print(f"  Error reading {f}: {e}")

if __name__ == "__main__":
    search_excels("GUI")
