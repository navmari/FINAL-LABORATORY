import sqlite3
import os
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
conn = sqlite3.connect(DB)
cur = conn.cursor()
try:
    cur.execute('SELECT COUNT(*) FROM pets_petloghistory WHERE pet_id IS NULL')
    nulls = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM pets_petloghistory')
    total = cur.fetchone()[0]
    print('Null pet_id rows:', nulls)
    print('Total rows:', total)
except Exception as e:
    print('Error querying DB:', e)
finally:
    conn.close()
