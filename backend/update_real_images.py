import os
import psycopg2

DATABASE_URL = os.environ.get(
    'DATABASE_URL_SYNC',
    'postgresql://peblo:peblo@db:5432/peblo'
)

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# Get all shows
cur.execute("SELECT id, title FROM shows;")
shows = cur.fetchall()

unsplash_mapping = {
    'Cosmic Journey': '1462331940025-496dfbfc7564',
    'Cooking with Grandma': '1556910103-1c02745aae4d',
    'Deep Blue': '1682687220199-d0124f48f95b',
    'Mountain High': '1464822759023-fed622ff2c3b',
    'Urban Legends': '1449844908441-8829872d2607',
    # Fallback
    'default': '1536440136628-849c177e76a1'
}

try:
    for show_id, title in shows:
        photo_id = unsplash_mapping.get(title, unsplash_mapping['default'])
        
        # Update poster
        poster_url = f"https://images.unsplash.com/{photo_id}?w=400&h=600&fit=crop"
        cur.execute("UPDATE artwork SET storage_key = %s WHERE show_id = %s AND type = 'poster';", (poster_url, show_id))
        
        # Update banner
        banner_url = f"https://images.unsplash.com/{photo_id}?w=1200&h=600&fit=crop"
        cur.execute("UPDATE artwork SET storage_key = %s WHERE show_id = %s AND type = 'banner';", (banner_url, show_id))
        
        # Update thumbnails (episodes of this show)
        cur.execute("""
            UPDATE artwork 
            SET storage_key = %s 
            WHERE type = 'thumbnail' AND episode_id IN (
                SELECT id FROM episodes WHERE season_id IN (
                    SELECT id FROM seasons WHERE show_id = %s
                )
            );
        """, (f"https://images.unsplash.com/{photo_id}?w=600&h=400&fit=crop", show_id))

    print('Artwork storage keys updated with REAL Unsplash images!')
except Exception as e:
    print('Error:', e)
finally:
    cur.close()
    conn.close()
