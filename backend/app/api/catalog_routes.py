"""Viewer/public catalogue API routes.

These routes serve ONLY published catalogue data.
They never call admin endpoints or expose unpublished content.
"""

from fastapi import APIRouter, Query

from app.services import get_current_catalogue, search_catalogue
from app.storage import get_storage
from app.config import get_settings

router = APIRouter(prefix="/catalog", tags=["Catalogue (Viewer)"])


def _get_storage():
    settings = get_settings()
    return get_storage(settings.storage_type, settings.storage_path)


@router.get("")
async def get_catalogue():
    """Get the current published catalogue."""
    storage = _get_storage()
    catalogue = await get_current_catalogue(storage)
    if not catalogue:
        return {"sections": [], "version": None, "published_at": None}
    return catalogue


@router.get("/search")
async def search(
    q: str | None = Query(None, description="Search text"),
    category: str | None = Query(None, description="Category filter"),
    language: str | None = Query(None, description="Language filter"),
    section: str | None = Query(None, description="Section filter"),
):
    """
    Search the published catalogue.

    All conditions are composed together with AND logic:
    - q: matches show title, episode title, category
    - category: exact match
    - language: shows with episodes in this language
    - section: exact match

    Search happens on the backend - NOT in the browser.
    """
    storage = _get_storage()
    return await search_catalogue(storage, q=q, category=category, language=language, section=section)
