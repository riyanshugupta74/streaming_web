"""API routes package."""

from app.api.auth_routes import router as auth_router
from app.api.admin_routes import router as admin_router
from app.api.catalog_routes import router as catalog_router

__all__ = ["auth_router", "admin_router", "catalog_router"]
