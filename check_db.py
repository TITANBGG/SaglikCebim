import sqlite3

db_path = r'C:\Users\aline\OneDrive\Masaüstü\SaglikCebim\dev.db.new'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

# Check radiology_findings table if exists
if 'radiology_findings' in tables:
    cur.execute('SELECT COUNT(*) FROM radiology_findings')
    count = cur.fetchone()[0]
    print(f"\nTotal findings in database: {count}")
    
    if count > 0:
        cur.execute('SELECT id, finding_type, heatmap_path FROM radiology_findings ORDER BY id DESC LIMIT 10')
        findings = cur.fetchall()
        print("\nLast radiology findings:")
        for f in findings:
            print(f"  ID: {f[0]}, Type: {f[1]}, Heatmap Path: {f[2]}")
    else:
        print("No findings in database yet")
        # Get table schema
        cur.execute("PRAGMA table_info(radiology_findings)")
        schema = cur.fetchall()
        print("\nTable schema:")
        for col in schema:
            print(f"  {col[1]} ({col[2]})")
else:
    print("\nradiology_findings table not found!")

conn.close()
