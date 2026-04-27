import sqlite3

def list_tables():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for row in cur.fetchall():
        print(row[0])

if __name__ == "__main__":
    list_tables()
