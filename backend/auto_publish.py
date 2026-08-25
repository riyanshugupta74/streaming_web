import asyncio
import os
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models import User
from app.services.publish_service import publish_catalogue
from app.storage.local import LocalStorageBackend

async def main():
    print("Auto-publishing catalogue on startup...")
    storage = LocalStorageBackend("data")
    
    async with async_session_maker() as db:
        # Find the admin user
        result = await db.execute(select(User).where(User.role == "admin").limit(1))
        admin = result.scalars().first()
        
        if not admin:
            print("No admin user found. Cannot auto-publish.")
            return

        try:
            response = await publish_catalogue(db, admin, storage)
            if response.success:
                print(f"✅ Auto-publish successful! {response.message}")
            else:
                print(f"❌ Auto-publish blocked: {response.message}")
        except Exception as e:
            print(f"Error during auto-publish: {e}")

if __name__ == "__main__":
    asyncio.run(main())
