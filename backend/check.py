import sqlite3

conn = sqlite3.connect("expenses.db")

cursor = conn.execute("""
    SELECT sql
    FROM sqlite_master
    WHERE type = 'table'
    AND name = 'expenses'
""")

row = cursor.fetchone()

print(row[0])

conn.close()