import asyncio
import os
import uuid
import asyncpg
from datetime import datetime, timezone

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://peblo:peblo@db:5432/peblo"
)
# Render provides postgres:// but asyncpg needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)

async def main():
    print("Connecting to DB to fix missing data...")
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Fix Shows
        shows = await conn.fetch("SELECT id, title, category FROM shows")
        for show in shows:
            # Fix empty synopsis
            await conn.execute("UPDATE shows SET synopsis = $1 WHERE id = $2 AND (synopsis IS NULL OR synopsis = '')", 
                               f"Experience the epic journey of {show['title']}.", show["id"])
            # Fix missing section
            await conn.execute("UPDATE shows SET section = category WHERE id = $1 AND (section IS NULL OR section = '')", show["id"])
            
            # Fix Artwork for Show (poster, banner)
            for aw_type in ["poster", "banner"]:
                existing = await conn.fetchrow("SELECT id FROM artwork WHERE entity_type = 'show' AND entity_id = $1 AND type = $2", show["id"], aw_type)
                if not existing:
                    # random placeholder image (picsum)
                    url = f"https://picsum.photos/seed/{show['id']}{aw_type}/600/900" if aw_type == "poster" else f"https://picsum.photos/seed/{show['id']}{aw_type}/1280/720"
                    await conn.execute(
                        "INSERT INTO artwork (id, entity_type, entity_id, type, url, created_at) VALUES ($1, 'show', $2, $3, $4, $5)",
                        str(uuid.uuid4()), show["id"], aw_type, url, datetime.now(timezone.utc)
                    )

        # Fix Episodes
        episodes = await conn.fetch("SELECT id, title FROM episodes")
        for ep in episodes:
            # Fix empty description
            await conn.execute("UPDATE episodes SET description = $1 WHERE id = $2 AND (description IS NULL OR description = '')", 
                               f"Watch {ep['title']} now on Peblo TV.", ep["id"])
            # Fix missing duration
            await conn.execute("UPDATE episodes SET duration = 1800 WHERE id = $1 AND duration IS NULL", ep["id"])
            
            # Fix Artwork for Episode (thumbnail)
            existing = await conn.fetchrow("SELECT id FROM artwork WHERE entity_type = 'episode' AND entity_id = $1 AND type = 'thumbnail'", ep["id"])
            if not existing:
                url = f"https://picsum.photos/seed/{ep['id']}thumb/640/360"
                await conn.execute(
                    "INSERT INTO artwork (id, entity_type, entity_id, type, url, created_at) VALUES ($1, 'episode', $2, 'thumbnail', $3, $4)",
                    str(uuid.uuid4()), ep["id"], url, datetime.now(timezone.utc)
                )

        print("Successfully fixed all missing metadata and artwork!")
    except Exception as e:
        print(f"Error fixing DB: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
