import sqlite3
import os
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
conn = sqlite3.connect(DB)
cur = conn.cursor()
try:
    cur.execute('DELETE FROM pets_petloghistory WHERE pet_id IS NULL')
    deleted = cur.rowcount
    conn.commit()
    print('Deleted rows:', deleted)
except Exception as e:
    print('Error:', e)
finally:
    conn.close()
