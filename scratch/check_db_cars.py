import sqlite3
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def check_db():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    
    print("--- Active Contracts ---")
    cur.execute("select h.ma_hd, c.xe_id, h.trang_thai from HOPDONGTHUE h join HOPDONGTHUE_CHITIET c on h.ma_hd = c.hop_dong_id")
    rows = cur.fetchall()
    for row in rows:
        print(f"HD: {row[0]}, XE: {row[1]}, STATUS: {row[2]}")

if __name__ == "__main__":
    check_db()
