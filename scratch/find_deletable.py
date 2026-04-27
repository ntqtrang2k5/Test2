import sqlite3
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def find_cars():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    
    print("--- Cars without contracts ---")
    cur.execute("SELECT bien_so, trang_thai FROM XE WHERE bien_so NOT IN (SELECT xe_id FROM HOPDONGTHUE_CHITIET)")
    for row in cur.fetchall():
        print(f"PLATE: {row[0]}, STATUS: {row[1]}")

if __name__ == "__main__":
    find_cars()
