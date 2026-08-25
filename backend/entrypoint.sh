#!/bin/bash
set -e

echo "🚀 Peblo TV Mini Backend Starting..."

# Wait for database to be ready (with timeout)
echo "⏳ Waiting for database..."
RETRIES=15
until python -c "
import asyncio
import asyncpg
import os
import sys

async def check_db():
    url = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://peblo:peblo@db:5432/peblo')
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    
    # asyncpg expects postgresql:// (without the +asyncpg part for connect)
    if url.startswith('postgresql+asyncpg://'):
        url = url.replace('postgresql+asyncpg://', 'postgresql://', 1)

    try:
        conn = await asyncpg.connect(url)
        await conn.close()
        print('Database is ready!')
    except Exception as e:
        sys.exit(1)

asyncio.run(check_db())
" 2>/dev/null; do
    RETRIES=$((RETRIES - 1))
    if [ $RETRIES -le 0 ]; then
        echo "❌ Database connection failed after max retries. Starting anyway..."
        break
    fi
    echo "  Database not ready yet, retrying in 2s... ($RETRIES retries left)"
    sleep 2
done

# Run migrations
echo "📦 Running database migrations..."
cd /app/backend
alembic upgrade head

# Seed database
echo "🌱 Seeding database..."
python -m app.seed

# Auto-fix missing content/artwork
echo "🛠️ Fixing missing artwork and metadata..."
python fix_db.py

# Start the API server
echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
