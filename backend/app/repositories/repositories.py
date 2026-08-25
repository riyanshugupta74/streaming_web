"""Repository layer for database operations.

Keeps business logic out of route handlers by providing
clean data access methods.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Show, Season, Episode, Artwork, PublishRun


# ─── Show Repository ────────────────────────────────────────────────────────

class ShowRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_shows(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        section: str | None = None,
        status: str | None = None,
        language: str | None = None,
    ) -> tuple[list[Show], int]:
        """List shows with pagination and filtering."""
        query = select(Show)

        # Apply filters
        if search:
            query = query.where(Show.title.ilike(f"%{search}%"))
        if section:
            query = query.where(Show.section == section)
        if status:
            query = query.where(Show.status == status)

        # Language filter: shows that have episodes in the given language
        if language:
            query = query.where(
                Show.id.in_(
                    select(Show.id)
                    .join(Season, Season.show_id == Show.id)
                    .join(Episode, Episode.season_id == Season.id)
                    .where(Episode.language == language)
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginate
        query = query.order_by(Show.title).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        shows = result.scalars().all()

        return shows, total

    async def get_show(self, show_id: UUID) -> Show | None:
        """Get a show by ID with all relationships."""
        result = await self.db.execute(
            select(Show)
            .where(Show.id == show_id)
            .options(
                selectinload(Show.seasons)
                .selectinload(Season.episodes)
                .selectinload(Episode.artwork),
                selectinload(Show.artwork),
            )
        )
        return result.scalar_one_or_none()

    async def create_show(self, **kwargs) -> Show:
        """Create a new show."""
        show = Show(**kwargs)
        self.db.add(show)
        await self.db.flush()
        return show

    async def update_show(self, show_id: UUID, **kwargs) -> Show | None:
        """Update a show."""
        show = await self.get_show(show_id)
        if not show:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(show, key, value)
        await self.db.flush()
        return show

    async def delete_show(self, show_id: UUID) -> bool:
        """Delete a show."""
        show = await self.get_show(show_id)
        if not show:
            return False
        await self.db.delete(show)
        await self.db.flush()
        return True

    async def get_show_counts(self, show: Show) -> tuple[int, int]:
        """Get season and episode counts for a show."""
        season_count = (await self.db.execute(
            select(func.count()).where(Season.show_id == show.id)
        )).scalar() or 0

        episode_count = (await self.db.execute(
            select(func.count())
            .select_from(Episode)
            .join(Season, Episode.season_id == Season.id)
            .where(Season.show_id == show.id)
        )).scalar() or 0

        return season_count, episode_count


# ─── Season Repository ──────────────────────────────────────────────────────

class SeasonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_season(self, season_id: UUID) -> Season | None:
        """Get a season by ID with episodes."""
        result = await self.db.execute(
            select(Season)
            .where(Season.id == season_id)
            .options(selectinload(Season.episodes).selectinload(Episode.artwork))
        )
        return result.scalar_one_or_none()

    async def create_season(self, show_id: UUID, **kwargs) -> Season:
        """Create a new season."""
        season = Season(show_id=show_id, **kwargs)
        self.db.add(season)
        await self.db.flush()
        return season

    async def update_season(self, season_id: UUID, **kwargs) -> Season | None:
        """Update a season."""
        season = await self.get_season(season_id)
        if not season:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(season, key, value)
        await self.db.flush()
        return season

    async def delete_season(self, season_id: UUID) -> bool:
        """Delete a season."""
        season = await self.get_season(season_id)
        if not season:
            return False
        await self.db.delete(season)
        await self.db.flush()
        return True


# ─── Episode Repository ─────────────────────────────────────────────────────

class EpisodeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_episode(self, episode_id: UUID) -> Episode | None:
        """Get an episode by ID with artwork."""
        result = await self.db.execute(
            select(Episode)
            .where(Episode.id == episode_id)
            .options(selectinload(Episode.artwork))
        )
        return result.scalar_one_or_none()

    async def create_episode(self, season_id: UUID, **kwargs) -> Episode:
        """Create a new episode."""
        episode = Episode(season_id=season_id, **kwargs)
        self.db.add(episode)
        await self.db.flush()
        return episode

    async def update_episode(self, episode_id: UUID, **kwargs) -> Episode | None:
        """Update an episode."""
        episode = await self.get_episode(episode_id)
        if not episode:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(episode, key, value)
        await self.db.flush()
        return episode

    async def delete_episode(self, episode_id: UUID) -> bool:
        """Delete an episode."""
        episode = await self.get_episode(episode_id)
        if not episode:
            return False
        await self.db.delete(episode)
        await self.db.flush()
        return True


# ─── Artwork Repository ─────────────────────────────────────────────────────

class ArtworkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_artwork(self, **kwargs) -> Artwork:
        """Create a new artwork record."""
        artwork = Artwork(**kwargs)
        self.db.add(artwork)
        await self.db.flush()
        return artwork

    async def get_artwork(self, artwork_id: UUID) -> Artwork | None:
        """Get an artwork by ID."""
        result = await self.db.execute(
            select(Artwork).where(Artwork.id == artwork_id)
        )
        return result.scalar_one_or_none()

    async def delete_artwork(self, artwork_id: UUID) -> bool:
        """Delete an artwork."""
        artwork = await self.get_artwork(artwork_id)
        if not artwork:
            return False
        await self.db.delete(artwork)
        await self.db.flush()
        return True

    async def get_existing_artwork(
        self,
        show_id: UUID | None,
        episode_id: UUID | None,
        artwork_type: str,
    ) -> Artwork | None:
        """Get existing artwork of a given type for a show or episode."""
        query = select(Artwork).where(Artwork.type == artwork_type)
        if episode_id:
            query = query.where(Artwork.episode_id == episode_id)
        elif show_id:
            query = query.where(
                Artwork.show_id == show_id,
                Artwork.episode_id.is_(None),
            )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


# ─── PublishRun Repository ───────────────────────────────────────────────────

class PublishRunRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_runs(self, limit: int = 50) -> list[PublishRun]:
        """List recent publish runs."""
        result = await self.db.execute(
            select(PublishRun)
            .order_by(PublishRun.started_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
