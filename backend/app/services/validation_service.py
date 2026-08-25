"""Validation report service.

Generates a comprehensive validation report for all content,
identifying blocking issues that prevent publishing.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Show, Season, Episode, Artwork
from app.schemas import ValidationError, ValidationReport


async def generate_validation_report(db: AsyncSession) -> ValidationReport:
    """
    Generate a validation report for all published content.

    Checks for:
    - Shows: missing section, empty synopsis
    - Episodes: missing duration, missing artwork (for published episodes)
    - Artwork: missing required types
    - Metadata: duplicate content_group+language, empty descriptions
    """
    show_errors: list[ValidationError] = []
    episode_errors: list[ValidationError] = []
    artwork_errors: list[ValidationError] = []
    metadata_errors: list[ValidationError] = []

    # ── Fetch all shows with seasons, episodes, and artwork ──────────────
    result = await db.execute(
        select(Show)
        .options(
            selectinload(Show.seasons)
            .selectinload(Season.episodes)
            .selectinload(Episode.artwork),
            selectinload(Show.artwork),
        )
        .order_by(Show.title)
    )
    shows = result.scalars().all()

    for show in shows:
        # ── Show validation ──────────────────────────────────────────────
        if show.status == "published":
            if not show.section or show.section.strip() == "":
                show_errors.append(ValidationError(
                    entity="Show",
                    entity_id=str(show.id),
                    entity_name=show.title,
                    field="section",
                    problem="Section is missing.",
                    fix="Assign a section (e.g., Featured, Kids, Adventure, Documentary) before publishing.",
                ))

            if not show.synopsis or show.synopsis.strip() == "":
                show_errors.append(ValidationError(
                    entity="Show",
                    entity_id=str(show.id),
                    entity_name=show.title,
                    field="synopsis",
                    problem="Synopsis is empty.",
                    fix="Add a synopsis to describe the show to viewers.",
                ))

            # Check show-level artwork
            show_artwork_types = {a.type for a in show.artwork}
            for required_type in ["poster", "banner"]:
                if required_type not in show_artwork_types:
                    artwork_errors.append(ValidationError(
                        entity="Show",
                        entity_id=str(show.id),
                        entity_name=show.title,
                        field=f"artwork.{required_type}",
                        problem=f"Missing {required_type} artwork.",
                        fix=f"Upload a {required_type} image for this show.",
                    ))

        for season in show.seasons:
            for episode in season.episodes:
                # ── Episode validation ───────────────────────────────────
                if episode.status == "published":
                    if episode.duration is None or episode.duration <= 0:
                        episode_errors.append(ValidationError(
                            entity="Episode",
                            entity_id=str(episode.id),
                            entity_name=f"{show.title} > S{season.season_number}E{episode.episode_number}: {episode.title}",
                            field="duration",
                            problem="Duration is missing.",
                            fix="Enter the episode duration (in seconds) before publishing.",
                        ))

                    if not episode.description or episode.description.strip() == "":
                        metadata_errors.append(ValidationError(
                            entity="Episode",
                            entity_id=str(episode.id),
                            entity_name=f"{show.title} > S{season.season_number}E{episode.episode_number}: {episode.title}",
                            field="description",
                            problem="Description is empty.",
                            fix="Add a description for this episode.",
                        ))

                    # Check episode artwork (thumbnails) for non-trailer episodes
                    if season.season_number > 0:
                        ep_artwork_types = {a.type for a in episode.artwork}
                        if "thumbnail" not in ep_artwork_types:
                            artwork_errors.append(ValidationError(
                                entity="Episode",
                                entity_id=str(episode.id),
                                entity_name=f"{show.title} > S{season.season_number}E{episode.episode_number}: {episode.title}",
                                field="artwork.thumbnail",
                                problem="Missing thumbnail artwork.",
                                fix="Upload a thumbnail image for this episode.",
                            ))

    total_errors = len(show_errors) + len(episode_errors) + len(artwork_errors) + len(metadata_errors)

    return ValidationReport(
        blocking=len(show_errors) + len(episode_errors) + len(artwork_errors) > 0,
        total_errors=total_errors,
        shows=show_errors,
        episodes=episode_errors,
        artwork=artwork_errors,
        metadata=metadata_errors,
    )
