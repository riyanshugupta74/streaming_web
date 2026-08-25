import os
import uuid
from datetime import datetime, timezone
import psycopg2

DATABASE_URL = os.environ.get(
    'DATABASE_URL_SYNC',
    'postgresql://peblo:peblo@db:5432/peblo'
)

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = False
cur = conn.cursor()

try:
    # 1. Fix missing duration
    cur.execute('UPDATE episodes SET duration = 600 WHERE duration IS NULL')
    
    # 2. Fix missing artwork for episodes
    cur.execute('''
        SELECT e.id FROM episodes e
        LEFT JOIN artwork a ON a.episode_id = e.id AND a.type = 'thumbnail'
        WHERE a.id IS NULL
    ''')
    missing_episodes = cur.fetchall()
    
    now = datetime.now(timezone.utc)
    for (ep_id,) in missing_episodes:
        art_id = str(uuid.uuid4())
        cur.execute(
            '''INSERT INTO artwork (id, episode_id, type, storage_key, width, height, size_bytes, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (art_id, ep_id, 'thumbnail', 'placeholder.jpg', 1920, 1080, 1024, now)
        )

    conn.commit()
    print('Database fixed!')
except Exception as e:
    conn.rollback()
    print('Failed:', e)
finally:
    cur.close()
    conn.close()
