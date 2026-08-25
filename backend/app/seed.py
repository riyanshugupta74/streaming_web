"""Database seeding script.

Loads seed_shows.json and creates development users.
Idempotent: safe to run multiple times without duplicating records.
"""

import json
import os
import sys
import uuid
import asyncio
from datetime import datetime, timezone

import asyncpg
import bcrypt

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://peblo:peblo@db:5432/peblo"
)
# Render provides postgres:// but asyncpg needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)


SEED_FILE = os.environ.get("SEED_FILE", "/app/seed/seed_shows.json")

# Development users
DEV_USERS = [
    {"email": "admin@example.com", "password": "admin123", "role": "admin"},
    {"email": "editor@example.com", "password": "editor123", "role": "editor"},
]


async def seed():
    """Run the seed operation."""
    print("🌱 Starting database seed...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ Failed to connect to DB for seeding: {e}")
        raise

    try:
        # Seed users (idempotent)
        for user in DEV_USERS:
            record = await conn.fetchrow("SELECT id FROM users WHERE email = $1", user["email"])
            if record is None:
                user_id = str(uuid.uuid4())
                password_hash = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                await conn.execute(
                    """INSERT INTO users (id, email, password_hash, role, created_at)
                    VALUES ($1, $2, $3, $4, $5)""",
                    user_id, user["email"], password_hash, user["role"], datetime.now(timezone.utc),
                )
                print(f"  ✓ Created user: {user['email']} ({user['role']})")
            else:
                print(f"  → User already exists: {user['email']}")

        # Seed shows from seed file
        if os.path.exists(SEED_FILE):
            with open(SEED_FILE) as f:
                seed_data = json.load(f)

            for show_data in seed_data.get("shows", []):
                # Check if show already exists by title
                record = await conn.fetchrow("SELECT id FROM shows WHERE title = $1", show_data["title"])

                if record:
                    print(f"  → Show already exists: {show_data['title']}")
                    continue

                # Create show
                show_id = str(uuid.uuid4())
                now = datetime.now(timezone.utc)
                await conn.execute(
                    """INSERT INTO shows (id, title, synopsis, category, section, status, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
                    show_id,
                    show_data["title"],
                    show_data.get("synopsis", ""),
                    show_data["category"],
                    show_data.get("section", ""),
                    show_data.get("status", "draft"),
                    now,
                    now,
                )
                print(f"  ✓ Created show: {show_data['title']}")

                # Create seasons and episodes
                for season_data in show_data.get("seasons", []):
                    season_id = str(uuid.uuid4())
                    await conn.execute(
                        """INSERT INTO seasons (id, show_id, season_number, title)
                        VALUES ($1, $2, $3, $4)""",
                        season_id,
                        show_id,
                        season_data["season_number"],
                        season_data["title"],
                    )
                    print(f"    ✓ Season {season_data['season_number']}: {season_data['title']}")

                    for ep_data in season_data.get("episodes", []):
                        episode_id = str(uuid.uuid4())
                        await conn.execute(
                            """INSERT INTO episodes
                            (id, season_id, episode_number, title, description,
                             duration, content_group, language, status, created_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)""",
                            episode_id,
                            season_id,
                            ep_data["episode_number"],
                            ep_data["title"],
                            ep_data.get("description", ""),
                            ep_data.get("duration"),  # Can be None!
                            ep_data["content_group"],
                            ep_data["language"],
                            ep_data.get("status", "draft"),
                            now,
                            now,
                        )
                        lang_info = f" [{ep_data['language']}]" if ep_data.get("language") else ""
                        print(f"      ✓ E{ep_data['episode_number']}: {ep_data['title']}{lang_info}")
        else:
            print(f"  ⚠ Seed file not found: {SEED_FILE}")

        print("\n✅ Seed completed successfully!")

    except Exception as e:
        print(f"\n❌ Seed failed: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())
