import psycopg2
import os
import random

DATABASE_URL = os.environ.get(
    'DATABASE_URL_SYNC',
    'postgresql://peblo:peblo@db:5432/peblo'
)
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

unsplash_ids = [
    '1512820790803-83ca734da794', '1478720568477-152d9b164e26',
    '1536440136628-849c177e76a1', '1501504905252-473c47e087f8',
    '1462331940025-496dfbfc7564', '1556910103-1c02745aae4d',
    '1682687220199-d0124f48f95b', '1464822759023-fed622ff2c3b',
    '1449844908441-8829872d2607', '1485846234645-a62644f84728',
    '1493246507139-91e8fad9978e', '1518709268805-4e9042af9f23',
    '1504109586052-7a56116ac3a0', '1553531384-411a247cad1f',
    '1506157786151-b8491531f063'
]

cur.execute("SELECT id FROM episodes;")
episodes = cur.fetchall()

for (ep_id,) in episodes:
    photo_id = random.choice(unsplash_ids)
    url = f"https://images.unsplash.com/photo-{photo_id}?w=600&h=400&fit=crop"
    
    # Check if artwork exists
    cur.execute("SELECT id FROM artwork WHERE episode_id = %s AND type = 'thumbnail';", (ep_id,))
    res = cur.fetchone()
    if res:
        cur.execute("UPDATE artwork SET storage_key = %s WHERE id = %s;", (url, res[0]))
    else:
        cur.execute("""
            INSERT INTO artwork (id, episode_id, type, storage_key, width, height, size_bytes)
            VALUES (gen_random_uuid(), %s, 'thumbnail', %s, 600, 400, 0)
        """, (ep_id, url))

cur.close()
conn.close()
print("Updated all episodes with random Unsplash images!")
