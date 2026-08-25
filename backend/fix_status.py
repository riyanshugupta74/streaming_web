import os
import psycopg2
import uuid
from datetime import datetime, timezone

DATABASE_URL = os.environ.get(
    'DATABASE_URL_SYNC',
    'postgresql://peblo:peblo@db:5432/peblo'
)

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

try:
    cur.execute("UPDATE shows SET status = 'published';")
    cur.execute("UPDATE episodes SET status = 'published';")
    
    # Check if there are any shows without poster/banner
    cur.execute('''
        SELECT s.id FROM shows s
        LEFT JOIN artwork a ON a.show_id = s.id AND a.type = 'poster'
        WHERE a.id IS NULL
    ''')
    for (s_id,) in cur.fetchall():
        cur.execute(
            '''INSERT INTO artwork (id, show_id, type, storage_key, width, height, size_bytes, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (str(uuid.uuid4()), s_id, 'poster', 'placeholder.jpg', 1920, 1080, 1024, datetime.now(timezone.utc))
        )
        
    cur.execute('''
        SELECT s.id FROM shows s
        LEFT JOIN artwork a ON a.show_id = s.id AND a.type = 'banner'
        WHERE a.id IS NULL
    ''')
    for (s_id,) in cur.fetchall():
        cur.execute(
            '''INSERT INTO artwork (id, show_id, type, storage_key, width, height, size_bytes, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (str(uuid.uuid4()), s_id, 'banner', 'placeholder.jpg', 1920, 1080, 1024, datetime.now(timezone.utc))
        )
        
    print('Status updated and dummy artwork added!')
except Exception as e:
    print('Error:', e)
finally:
    cur.close()
    conn.close()
