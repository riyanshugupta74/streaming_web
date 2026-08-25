"""Catalogue publishing service.

Handles the complete publish pipeline:
1. Run validation
2. Block if errors exist
3. Read only published content
4. Group language variants
5. Exclude Season 0 from normal seasons
6. Generate deterministic catalogue
7. Atomic publish with immutable versioning
"""

import json
import uuid
from datetime import datetime, timezone
from collections import defaultdict

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Show, Season, Episode, Artwork, PublishRun, User
from app.schemas import (
    Catalogue,
    CatalogueSection,
    CatalogueShow,
    CatalogueSeason,
    CatalogueEpisode,
    CatalogueTrailer,
    PublishRunOut,
    PublishResponse,
)
from app.services.validation_service import generate_validation_report
from app.storage import StorageBackend


# Deterministic section ordering
SECTION_ORDER = ["Featured", "Kids", "Adventure", "Documentary"]


async def publish_catalogue(
    db: AsyncSession,
    user: User,
    storage: StorageBackend,
) -> PublishResponse:
    """
    Publish the catalogue.

    This is an atomic operation:
    1. Creates a publish run record
    2. Runs validation
    3. If validation fails, marks run as 'blocked'
    4. If validation passes, generates catalogue JSON
    5. Writes to immutable file (catalogue-{uuid}.json)
    6. Updates current.json pointer
    7. Records success
    """
    # Create publish run record
    run = PublishRun(
        triggered_by=user.id,
        status="running",
    )
    db.add(run)
    await db.flush()

    try:
        # Step 1: Run validation
        report = await generate_validation_report(db)

        if report.blocking:
            run.status = "blocked"
            run.completed_at = datetime.now(timezone.utc)
            run.error = f"{report.total_errors} blocking validation errors found"
            await db.flush()
            return PublishResponse(
                success=False,
                message=f"Publishing blocked: {report.total_errors} validation errors must be resolved first.",
                publish_run=PublishRunOut.model_validate(run),
                validation_report=report,
            )

        # Step 2: Fetch published shows with all relationships
        result = await db.execute(
            select(Show)
            .where(Show.status == "published")
            .options(
                selectinload(Show.seasons)
                .selectinload(Season.episodes)
                .selectinload(Episode.artwork),
                selectinload(Show.artwork),
            )
            .order_by(Show.title)
        )
        published_shows = result.scalars().all()

        # Step 3: Build the catalogue
        catalogue = _build_catalogue(published_shows, storage)

        # Step 4: Serialize to JSON
        catalogue_json = json.dumps(
            catalogue.model_dump(),
            indent=2,
            sort_keys=False,
            ensure_ascii=False,
        )

        # Step 5: Write to immutable file
        catalogue_key = f"catalogues/catalogue-{uuid.uuid4().hex[:12]}.json"
        await storage.upload(catalogue_key, catalogue_json.encode("utf-8"), "application/json")

        # Step 6: Verify successful write
        exists = await storage.exists(catalogue_key)
        if not exists:
            raise RuntimeError("Failed to write catalogue file")

        # Step 7: Atomically update current pointer
        current_pointer = json.dumps({
            "current": catalogue_key,
            "published_at": catalogue.published_at,
            "version": catalogue.version,
        })
        await storage.upload("catalogues/current.json", current_pointer.encode("utf-8"), "application/json")

        # Step 8: Count content
        shows_count = 0
        episodes_count = 0
        for section in catalogue.sections:
            shows_count += len(section.shows)
            for show in section.shows:
                for season in show.seasons:
                    episodes_count += len(season.episodes)

        # Step 9: Record success
        run.status = "success"
        run.completed_at = datetime.now(timezone.utc)
        run.shows_count = shows_count
        run.episodes_count = episodes_count
        run.catalogue_key = catalogue_key
        await db.flush()

        return PublishResponse(
            success=True,
            message=f"Catalogue published successfully. {shows_count} shows, {episodes_count} episodes.",
            publish_run=PublishRunOut.model_validate(run),
        )

    except Exception as e:
        run.status = "failed"
        run.completed_at = datetime.now(timezone.utc)
        run.error = str(e)
        await db.flush()
        return PublishResponse(
            success=False,
            message=f"Publishing failed: {str(e)}",
            publish_run=PublishRunOut.model_validate(run),
        )


def _build_catalogue(shows: list[Show], storage: StorageBackend) -> Catalogue:
    """Build a deterministic catalogue from published shows."""
    now = datetime.now(timezone.utc)

    # Group shows by section
    section_shows: dict[str, list[Show]] = defaultdict(list)
    for show in shows:
        if show.section and show.section.strip():
            section_shows[show.section].append(show)

    # Build sections in deterministic order
    sections = []
    seen_sections = set()

    # First, add sections in the predefined order
    for section_name in SECTION_ORDER:
        if section_name in section_shows:
            sections.append(_build_section(section_name, section_shows[section_name], storage))
            seen_sections.add(section_name)

    # Then, add any additional sections alphabetically
    for section_name in sorted(section_shows.keys()):
        if section_name not in seen_sections:
            sections.append(_build_section(section_name, section_shows[section_name], storage))

    return Catalogue(
        version=uuid.uuid4().hex[:8],
        published_at=now.isoformat(),
        sections=sections,
    )


def _build_section(name: str, shows: list[Show], storage: StorageBackend) -> CatalogueSection:
    """Build a catalogue section with sorted shows."""
    catalogue_shows = []
    for show in sorted(shows, key=lambda s: s.title):
        catalogue_shows.append(_build_show(show, storage))
    return CatalogueSection(name=name, shows=catalogue_shows)


def _build_show(show: Show, storage: StorageBackend) -> CatalogueShow:
    """Build a catalogue show entry."""
    # Show artwork
    show_artwork = {}
    for art in (show.artwork or []):
        show_artwork[art.type] = storage.get_url(art.storage_key)

    # Build seasons (excluding Season 0)
    seasons = []
    trailers = []

    for season in sorted(show.seasons, key=lambda s: s.season_number):
        published_episodes = [
            ep for ep in season.episodes if ep.status == "published"
        ]
        if not published_episodes:
            continue

        if season.season_number == 0:
            # Season 0 → trailers
            trailers.extend(_build_trailers(published_episodes, storage))
        else:
            # Normal season
            catalogue_season = _build_season(season, published_episodes, storage)
            if catalogue_season.episodes:
                seasons.append(catalogue_season)

    return CatalogueShow(
        id=str(show.id),
        title=show.title,
        synopsis=show.synopsis or "",
        category=show.category,
        artwork=show_artwork,
        seasons=seasons,
        trailers=trailers,
    )


def _build_season(
    season: Season,
    published_episodes: list[Episode],
    storage: StorageBackend,
) -> CatalogueSeason:
    """Build a catalogue season with language-grouped episodes."""
    grouped = _group_episodes_by_content_group(published_episodes, storage)

    return CatalogueSeason(
        season_number=season.season_number,
        title=season.title,
        episodes=sorted(grouped, key=lambda e: e.episode_number),
    )


def _build_trailers(episodes: list[Episode], storage: StorageBackend) -> list[CatalogueTrailer]:
    """Build trailer entries from Season 0 episodes."""
    # Group by content_group
    groups: dict[str, list[Episode]] = defaultdict(list)
    for ep in episodes:
        groups[ep.content_group].append(ep)

    trailers = []
    for content_group in sorted(groups.keys()):
        eps = groups[content_group]
        # Use first episode's metadata, merge languages
        first = sorted(eps, key=lambda e: e.language)[0]
        languages = sorted(set(ep.language for ep in eps))
        
        # Collect artwork from all variants (prefer primary's artwork)
        artwork = {}
        for ep in eps:
            for art in (ep.artwork or []):
                if art.type not in artwork:
                    artwork[art.type] = storage.get_url(art.storage_key)

        trailers.append(CatalogueTrailer(
            content_group=content_group,
            title=first.title,
            duration=first.duration or 0,
            languages=languages,
            artwork=artwork,
        ))

    return trailers


def _group_episodes_by_content_group(
    episodes: list[Episode],
    storage: StorageBackend,
) -> list[CatalogueEpisode]:
    """
    Group language variants by content_group.

    If episodes share the same content_group, they are collapsed into
    a single catalogue entry with a list of available languages.

    For metadata conflicts between language variants:
    - Title: use the English variant if available, otherwise first alphabetically
    - Description: use the English variant if available
    - Duration: use the maximum across variants (they should be equal)
    """
    groups: dict[str, list[Episode]] = defaultdict(list)
    for ep in episodes:
        groups[ep.content_group].append(ep)

    result = []
    for content_group in sorted(groups.keys()):
        eps = groups[content_group]

        # Determine the "primary" episode (English preferred, else alphabetical)
        primary = None
        for ep in eps:
            if ep.language.lower() == "english":
                primary = ep
                break
        if primary is None:
            primary = sorted(eps, key=lambda e: e.language)[0]

        # Merge languages deterministically
        languages = sorted(set(ep.language for ep in eps))

        # Use max duration (should be same across variants)
        duration = max((ep.duration or 0) for ep in eps)

        # Collect artwork from all variants (prefer primary's artwork)
        artwork = {}
        for ep in eps:
            for art in (ep.artwork or []):
                if art.type not in artwork:
                    artwork[art.type] = storage.get_url(art.storage_key)

        result.append(CatalogueEpisode(
            content_group=content_group,
            episode_number=primary.episode_number,
            title=primary.title,
            description=primary.description or "",
            duration=duration,
            languages=languages,
            artwork=artwork,
        ))

    return result


async def get_current_catalogue(storage: StorageBackend) -> dict | None:
    """Read the current published catalogue."""
    pointer_data = await storage.get("catalogues/current.json")
    if not pointer_data:
        return None

    pointer = json.loads(pointer_data.decode("utf-8"))
    catalogue_key = pointer.get("current")
    if not catalogue_key:
        return None

    catalogue_data = await storage.get(catalogue_key)
    if not catalogue_data:
        return None

    return json.loads(catalogue_data.decode("utf-8"))


async def search_catalogue(
    storage: StorageBackend,
    q: str | None = None,
    category: str | None = None,
    language: str | None = None,
    section: str | None = None,
) -> dict:
    """
    Search and filter the published catalogue.

    All conditions are composed together (AND logic).
    Search is performed on the server side, not in the browser.
    """
    catalogue = await get_current_catalogue(storage)
    if not catalogue:
        return {"sections": [], "total_results": 0}

    filtered_sections = []
    total_results = 0
    q_lower = q.lower().strip() if q else None

    for cat_section in catalogue.get("sections", []):
        # Section filter
        if section and cat_section["name"] != section:
            continue

        matched_shows = []
        for show in cat_section.get("shows", []):
            show_matches = True

            # Category filter
            if category and show.get("category", "").lower() != category.lower():
                show_matches = False
                continue

            # Language filter - check if any episode has the language
            if language:
                has_language = False
                for s in show.get("seasons", []):
                    for ep in s.get("episodes", []):
                        if language in ep.get("languages", []):
                            has_language = True
                            break
                    if has_language:
                        break
                if not has_language:
                    show_matches = False
                    continue

            # Text search (q)
            if q_lower:
                text_match = False
                # Search show title
                if q_lower in show.get("title", "").lower():
                    text_match = True
                # Search category
                if q_lower in show.get("category", "").lower():
                    text_match = True
                # Search episode titles
                for s in show.get("seasons", []):
                    for ep in s.get("episodes", []):
                        if q_lower in ep.get("title", "").lower():
                            text_match = True
                            break
                    if text_match:
                        break

                if not text_match:
                    show_matches = False
                    continue

            if show_matches:
                matched_shows.append(show)
                total_results += 1

        if matched_shows:
            filtered_sections.append({
                "name": cat_section["name"],
                "shows": matched_shows,
            })

    return {
        "sections": filtered_sections,
        "total_results": total_results,
    }
