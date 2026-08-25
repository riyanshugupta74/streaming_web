"""Admin CRUD API routes for shows, seasons, episodes, and artwork."""

import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.auth import get_current_user, require_role
from app.models import User
from app.repositories import (
    ShowRepository,
    SeasonRepository,
    EpisodeRepository,
    ArtworkRepository,
    PublishRunRepository,
)
from app.schemas import (
    ShowCreate,
    ShowUpdate,
    ShowOut,
    ShowListItem,
    ShowListResponse,
    SeasonCreate,
    SeasonUpdate,
    SeasonOut,
    EpisodeCreate,
    EpisodeUpdate,
    EpisodeOut,
    ArtworkOut,
    ValidationReport,
    PublishRunOut,
    PublishResponse,
)
from app.services import validate_artwork, generate_validation_report, publish_catalogue
from app.storage import get_storage, generate_storage_key
from app.config import get_settings

router = APIRouter(prefix="/admin", tags=["Admin"])


# ─── Dependency helpers ─────────────────────────────────────────────────────

def get_storage_backend():
    """Get the configured storage backend."""
    settings = get_settings()
    return get_storage(settings.storage_type, settings.storage_path)


# ─── Shows ──────────────────────────────────────────────────────────────────

@router.get("/shows", response_model=ShowListResponse)
async def list_shows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    section: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    language: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List shows with pagination and filtering."""
    repo = ShowRepository(db)
    shows, total = await repo.list_shows(
        page=page,
        page_size=page_size,
        search=search,
        section=section,
        status=status_filter,
        language=language,
    )

    items = []
    for show in shows:
        season_count, episode_count = await repo.get_show_counts(show)
        items.append(ShowListItem(
            id=show.id,
            title=show.title,
            category=show.category,
            section=show.section or "",
            status=show.status,
            updated_at=show.updated_at,
            season_count=season_count,
            episode_count=episode_count,
        ))

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ShowListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/shows", response_model=ShowOut, status_code=201)
async def create_show(
    data: ShowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new show."""
    repo = ShowRepository(db)
    show = await repo.create_show(**data.model_dump())
    return await repo.get_show(show.id)


@router.get("/shows/{show_id}", response_model=ShowOut)
async def get_show(
    show_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a show by ID with all relationships."""
    repo = ShowRepository(db)
    show = await repo.get_show(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    return show


@router.put("/shows/{show_id}", response_model=ShowOut)
async def update_show(
    show_id: UUID,
    data: ShowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a show."""
    repo = ShowRepository(db)
    update_data = data.model_dump(exclude_unset=True)
    show = await repo.update_show(show_id, **update_data)
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    return await repo.get_show(show_id)


@router.delete("/shows/{show_id}", status_code=204)
async def delete_show(
    show_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a show and all associated content."""
    repo = ShowRepository(db)
    if not await repo.delete_show(show_id):
        raise HTTPException(status_code=404, detail="Show not found")


# ─── Seasons ────────────────────────────────────────────────────────────────

@router.post("/shows/{show_id}/seasons", response_model=SeasonOut, status_code=201)
async def create_season(
    show_id: UUID,
    data: SeasonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new season for a show."""
    show_repo = ShowRepository(db)
    show = await show_repo.get_show(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")

    season_repo = SeasonRepository(db)
    try:
        season = await season_repo.create_season(show_id, **data.model_dump())
        return await season_repo.get_season(season.id)
    except Exception as e:
        if "uq_season_show_number" in str(e):
            raise HTTPException(
                status_code=409,
                detail=f"Season {data.season_number} already exists for this show",
            )
        raise


@router.put("/seasons/{season_id}", response_model=SeasonOut)
async def update_season(
    season_id: UUID,
    data: SeasonUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a season."""
    repo = SeasonRepository(db)
    update_data = data.model_dump(exclude_unset=True)
    season = await repo.update_season(season_id, **update_data)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    return season


@router.delete("/seasons/{season_id}", status_code=204)
async def delete_season(
    season_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a season and all associated episodes."""
    repo = SeasonRepository(db)
    if not await repo.delete_season(season_id):
        raise HTTPException(status_code=404, detail="Season not found")


# ─── Episodes ───────────────────────────────────────────────────────────────

@router.post("/seasons/{season_id}/episodes", response_model=EpisodeOut, status_code=201)
async def create_episode(
    season_id: UUID,
    data: EpisodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new episode in a season."""
    season_repo = SeasonRepository(db)
    season = await season_repo.get_season(season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")

    episode_repo = EpisodeRepository(db)
    try:
        episode = await episode_repo.create_episode(season_id, **data.model_dump())
        return await episode_repo.get_episode(episode.id)
    except Exception as e:
        if "uq_episode_content_group_language" in str(e):
            raise HTTPException(
                status_code=409,
                detail=f"An episode with content_group '{data.content_group}' and language '{data.language}' already exists",
            )
        raise


@router.put("/episodes/{episode_id}", response_model=EpisodeOut)
async def update_episode(
    episode_id: UUID,
    data: EpisodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an episode."""
    repo = EpisodeRepository(db)
    update_data = data.model_dump(exclude_unset=True)
    episode = await repo.update_episode(episode_id, **update_data)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode


@router.delete("/episodes/{episode_id}", status_code=204)
async def delete_episode(
    episode_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an episode."""
    repo = EpisodeRepository(db)
    if not await repo.delete_episode(episode_id):
        raise HTTPException(status_code=404, detail="Episode not found")


# ─── Artwork ────────────────────────────────────────────────────────────────

@router.post("/artwork", response_model=ArtworkOut, status_code=201)
async def upload_artwork(
    file: UploadFile = File(...),
    artwork_type: str = Form(...),
    show_id: UUID | None = Form(None),
    episode_id: UUID | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload artwork for a show or episode."""
    if not show_id and not episode_id:
        raise HTTPException(
            status_code=400,
            detail="Either show_id or episode_id must be provided",
        )

    if artwork_type not in ("poster", "banner", "thumbnail"):
        raise HTTPException(
            status_code=400,
            detail="artwork_type must be one of: poster, banner, thumbnail",
        )

    # Read file data
    file_data = await file.read()
    if not file_data:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    # Validate the image
    validation = validate_artwork(file_data, artwork_type)
    if not validation.valid:
        raise HTTPException(
            status_code=400,
            detail={
                "message": validation.errors[0] if validation.errors else "Invalid image",
                "errors": validation.errors,
                "details": validation.details,
            },
        )

    # Determine file extension
    ext = "jpg"
    if file.content_type == "image/png":
        ext = "png"

    # Store the file
    storage = get_storage_backend()
    storage_key = generate_storage_key(f"artwork/{artwork_type}", ext)
    await storage.upload(storage_key, file_data, file.content_type or "image/jpeg")

    # Remove existing artwork of this type for the entity
    artwork_repo = ArtworkRepository(db)
    existing = await artwork_repo.get_existing_artwork(show_id, episode_id, artwork_type)
    if existing:
        await storage.delete(existing.storage_key)
        await artwork_repo.delete_artwork(existing.id)

    # Create artwork record
    artwork = await artwork_repo.create_artwork(
        show_id=show_id,
        episode_id=episode_id,
        type=artwork_type,
        storage_key=storage_key,
        width=validation.width,
        height=validation.height,
        size_bytes=validation.size_bytes,
    )

    return artwork


@router.delete("/artwork/{artwork_id}", status_code=204)
async def delete_artwork(
    artwork_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete artwork."""
    repo = ArtworkRepository(db)
    artwork = await repo.get_artwork(artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Delete file from storage
    storage = get_storage_backend()
    await storage.delete(artwork.storage_key)

    await repo.delete_artwork(artwork_id)


# ─── Validation Report ──────────────────────────────────────────────────────

@router.get("/validation-report", response_model=ValidationReport)
async def get_validation_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the validation report for all content."""
    return await generate_validation_report(db)


# ─── Catalogue Publishing ───────────────────────────────────────────────────

@router.post("/catalog/publish", response_model=PublishResponse)
async def publish(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """
    Publish the catalogue.

    Only admins can call this endpoint.
    Editors will receive HTTP 403.
    """
    storage = get_storage_backend()
    return await publish_catalogue(db, current_user, storage)


@router.get("/catalog/publish-runs", response_model=list[PublishRunOut])
async def list_publish_runs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Get publish run history. Admin only."""
    repo = PublishRunRepository(db)
    return await repo.list_runs()
