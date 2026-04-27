import sqlite3

def table_info(name):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    print(f"--- {name} ---")
    cur.execute(f"PRAGMA table_info({name})")
    for row in cur.fetchall():
        print(row[1])

if __name__ == "__main__":
    table_info("HOPDONGTHUE")
    table_info("HOPDONGTHUE_CHITIET")
    table_info("XE")
