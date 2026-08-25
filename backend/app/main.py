"""Peblo TV Mini - FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api import auth_router, admin_router, catalog_router
from app.config import get_settings
from app.db import engine

settings = get_settings()

app = FastAPI(
    title="Peblo TV Mini API",
    description="Miniature streaming content platform API",
    version="1.0.0",
)

# CORS
origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount storage for serving artwork and catalogue files
storage_path = Path(settings.storage_path)
storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(catalog_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    db_status = "unknown"
    try:
        from app.db import async_session_factory
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    storage_status = "healthy"
    try:
        if not storage_path.exists():
            storage_status = "unhealthy: storage path does not exist"
    except Exception as e:
        storage_status = f"unhealthy: {str(e)}"

    overall = "healthy" if db_status == "healthy" and storage_status == "healthy" else "degraded"

    return {
        "status": overall,
        "database": db_status,
        "storage": storage_status,
    }
