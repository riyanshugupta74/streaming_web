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
    cur.execute("UPDATE shows SET section = 'Featured', synopsis = 'A great show about cooking' WHERE title = 'Cooking with Grandma';")
    cur.execute("UPDATE episodes SET description = 'A description of whale songs' WHERE title = 'Whale Song';")
    print('Remaining validations fixed!')
except Exception as e:
    print('Error:', e)
finally:
    cur.close()
    conn.close()
