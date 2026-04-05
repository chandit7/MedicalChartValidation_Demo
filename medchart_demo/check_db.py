import sqlite3

conn = sqlite3.connect('medchart.db')
cursor = conn.cursor()

# Show tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables in database:")
for table in cursor.fetchall():
    print(f"  - {table[0]}")

# Show results table structure
print("\nResults table structure:")
cursor.execute("PRAGMA table_info(results)")
for row in cursor.fetchall():
    print(f"  {row[1]:15} {row[2]:10}")

# Show row count
cursor.execute("SELECT COUNT(*) FROM results")
count = cursor.fetchone()[0]
print(f"\nTotal records: {count}")

# Show all records if any exist
if count > 0:
    print("\nRecords:")
    cursor.execute("SELECT member_id, filename, decision, confidence FROM results")
    for row in cursor.fetchall():
        print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]}")

conn.close()

# Made with Bob
