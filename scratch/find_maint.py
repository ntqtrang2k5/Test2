import sqlite3
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def find_maintenance():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    
    print("--- Cars in Maintenance ---")
    cur.execute("SELECT bien_so FROM XE WHERE trang_thai LIKE '%Bảo trì%'")
    for row in cur.fetchall():
        print(row[0])

if __name__ == "__main__":
    find_maintenance()
