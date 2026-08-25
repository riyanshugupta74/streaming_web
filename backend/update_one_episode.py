import psycopg2
import os

DATABASE_URL = os.environ.get(
    'DATABASE_URL_SYNC',
    'postgresql://peblo:peblo@db:5432/peblo'
)
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# Get the first episode
cur.execute("SELECT id FROM episodes LIMIT 1;")
episode_id = cur.fetchone()[0]
new_image_url = "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&h=400&fit=crop"

# update artwork
cur.execute("UPDATE artwork SET storage_key = %s WHERE episode_id = %s AND type = 'thumbnail';", (new_image_url, episode_id))

# Also fix any missing artwork for any shows
default_img = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=400&h=600&fit=crop"
default_banner = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1200&h=600&fit=crop"

cur.execute("""
    INSERT INTO artwork (id, show_id, type, storage_key, width, height, size_bytes)
    SELECT gen_random_uuid(), id, 'poster', %s, 400, 600, 0
    FROM shows
    WHERE id NOT IN (SELECT show_id FROM artwork WHERE type = 'poster' AND show_id IS NOT NULL);
""", (default_img,))

cur.execute("""
    INSERT INTO artwork (id, show_id, type, storage_key, width, height, size_bytes)
    SELECT gen_random_uuid(), id, 'banner', %s, 1200, 600, 0
    FROM shows
    WHERE id NOT IN (SELECT show_id FROM artwork WHERE type = 'banner' AND show_id IS NOT NULL);
""", (default_banner,))

cur.close()
conn.close()
print("Updated episode thumbnail and fixed missing show artwork!")
