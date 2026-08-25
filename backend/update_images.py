import os
import psycopg2

DATABASE_URL = os.environ.get(
    'DATABASE_URL_SYNC',
    'postgresql://peblo:peblo@db:5432/peblo'
)

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

try:
    # Update posters
    cur.execute("UPDATE artwork SET storage_key = 'https://picsum.photos/seed/' || id::text || '/400/600' WHERE type = 'poster';")
    # Update banners
    cur.execute("UPDATE artwork SET storage_key = 'https://picsum.photos/seed/' || id::text || '/1200/600' WHERE type = 'banner';")
    # Update thumbnails
    cur.execute("UPDATE artwork SET storage_key = 'https://picsum.photos/seed/' || id::text || '/600/400' WHERE type = 'thumbnail';")
    
    print('Artwork storage keys updated with Picsum placeholder URLs!')
except Exception as e:
    print('Error:', e)
finally:
    cur.close()
    conn.close()
