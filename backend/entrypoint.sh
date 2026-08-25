#!/bin/bash
set -e

echo "🚀 Peblo TV Mini Backend Starting..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
until python -c "
import psycopg2
import os
conn = psycopg2.connect(os.environ.get('DATABASE_URL_SYNC', 'postgresql://peblo:peblo@db:5432/peblo'))
conn.close()
print('Database is ready!')
" 2>/dev/null; do
    echo "  Database not ready yet, retrying in 2s..."
    sleep 2
done

# Run migrations
echo "📦 Running database migrations..."
cd /app/backend
alembic upgrade head

# Seed database
echo "🌱 Seeding database..."
python -m app.seed

# Start the API server
echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
