import sqlite3
conn = sqlite3.connect('dev.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables:", tables)

# Check if radiology tables exist
rad_tables = [t for t in tables if 'radiology' in t[0].lower()]
print("Radiology tables:", rad_tables)

# Check columns of radiology_images if it exists
if ('radiology_images',) in tables:
    c.execute("PRAGMA table_info(radiology_images)")
    print("radiology_images columns:", c.fetchall())
    
if ('radiology_findings',) in tables:
    c.execute("PRAGMA table_info(radiology_findings)")
    print("radiology_findings columns:", c.fetchall())

conn.close()
