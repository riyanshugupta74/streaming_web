"""Database seeding script.

Loads seed_shows.json and creates development users.
Idempotent: safe to run multiple times without duplicating records.
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone

import psycopg2
import bcrypt

DATABASE_URL = os.environ.get(
    "DATABASE_URL_SYNC",
    "postgresql://peblo:peblo@db:5432/peblo"
)

SEED_FILE = os.environ.get("SEED_FILE", "/app/seed/seed_shows.json")

# Development users
DEV_USERS = [
    {"email": "admin@example.com", "password": "admin123", "role": "admin"},
    {"email": "editor@example.com", "password": "editor123", "role": "editor"},
]


def seed():
    """Run the seed operation."""
    print("🌱 Starting database seed...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # Seed users (idempotent)
        for user in DEV_USERS:
            cur.execute("SELECT id FROM users WHERE email = %s", (user["email"],))
            if cur.fetchone() is None:
                user_id = str(uuid.uuid4())
                password_hash = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute(
                    """INSERT INTO users (id, email, password_hash, role, created_at)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (user_id, user["email"], password_hash, user["role"], datetime.now(timezone.utc)),
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
                cur.execute("SELECT id FROM shows WHERE title = %s", (show_data["title"],))
                existing = cur.fetchone()

                if existing:
                    print(f"  → Show already exists: {show_data['title']}")
                    continue

                # Create show
                show_id = str(uuid.uuid4())
                now = datetime.now(timezone.utc)
                cur.execute(
                    """INSERT INTO shows (id, title, synopsis, category, section, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        show_id,
                        show_data["title"],
                        show_data.get("synopsis", ""),
                        show_data["category"],
                        show_data.get("section", ""),
                        show_data.get("status", "draft"),
                        now,
                        now,
                    ),
                )
                print(f"  ✓ Created show: {show_data['title']}")

                # Create seasons and episodes
                for season_data in show_data.get("seasons", []):
                    season_id = str(uuid.uuid4())
                    cur.execute(
                        """INSERT INTO seasons (id, show_id, season_number, title)
                        VALUES (%s, %s, %s, %s)""",
                        (
                            season_id,
                            show_id,
                            season_data["season_number"],
                            season_data["title"],
                        ),
                    )
                    print(f"    ✓ Season {season_data['season_number']}: {season_data['title']}")

                    for ep_data in season_data.get("episodes", []):
                        episode_id = str(uuid.uuid4())
                        cur.execute(
                            """INSERT INTO episodes
                            (id, season_id, episode_number, title, description,
                             duration, content_group, language, status, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (
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
                            ),
                        )
                        lang_info = f" [{ep_data['language']}]" if ep_data.get("language") else ""
                        print(f"      ✓ E{ep_data['episode_number']}: {ep_data['title']}{lang_info}")
        else:
            print(f"  ⚠ Seed file not found: {SEED_FILE}")

        conn.commit()
        print("\n✅ Seed completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Seed failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    seed()
