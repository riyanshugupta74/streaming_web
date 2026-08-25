"""Tests for publishing service logic."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from app.services.publish_service import (
    _build_catalogue,
    _group_episodes_by_content_group,
    _build_trailers,
    SECTION_ORDER,
)


def _make_artwork(art_type, storage_key="artwork/test/abc.jpg"):
    """Create a mock artwork object."""
    art = MagicMock()
    art.type = art_type
    art.storage_key = storage_key
    return art


def _make_episode(
    episode_number=1,
    title="Test Episode",
    description="Test description",
    duration=1800,
    content_group="test-cg",
    language="English",
    status="published",
    artwork=None,
):
    """Create a mock episode object."""
    ep = MagicMock()
    ep.id = uuid4()
    ep.episode_number = episode_number
    ep.title = title
    ep.description = description
    ep.duration = duration
    ep.content_group = content_group
    ep.language = language
    ep.status = status
    ep.artwork = artwork or []
    return ep


def _make_season(season_number=1, title="Season 1", episodes=None):
    """Create a mock season object."""
    season = MagicMock()
    season.id = uuid4()
    season.season_number = season_number
    season.title = title
    season.episodes = episodes or []
    return season


def _make_show(
    title="Test Show",
    synopsis="Test synopsis",
    category="Adventure",
    section="Adventure",
    status="published",
    seasons=None,
    artwork=None,
):
    """Create a mock show object."""
    show = MagicMock()
    show.id = uuid4()
    show.title = title
    show.synopsis = synopsis
    show.category = category
    show.section = section
    show.status = status
    show.seasons = seasons or []
    show.artwork = artwork or []
    return show


class TestLanguageGrouping:
    """Tests for language variant collapsing."""

    def test_collapses_same_content_group(self):
        """Episodes with the same content_group should merge into one."""
        storage = MagicMock()
        storage.get_url = lambda key: f"/storage/{key}"

        episodes = [
            _make_episode(content_group="abc", language="English", title="Ep 1"),
            _make_episode(content_group="abc", language="Hindi", title="Ep 1"),
        ]

        result = _group_episodes_by_content_group(episodes, storage)
        assert len(result) == 1
        assert set(result[0].languages) == {"English", "Hindi"}

    def test_keeps_different_content_groups_separate(self):
        """Different content_groups should remain as separate episodes."""
        storage = MagicMock()
        storage.get_url = lambda key: f"/storage/{key}"

        episodes = [
            _make_episode(content_group="abc", language="English", episode_number=1),
            _make_episode(content_group="def", language="English", episode_number=2),
        ]

        result = _group_episodes_by_content_group(episodes, storage)
        assert len(result) == 2

    def test_language_order_is_deterministic(self):
        """Languages should always be in sorted order."""
        storage = MagicMock()
        storage.get_url = lambda key: f"/storage/{key}"

        episodes = [
            _make_episode(content_group="abc", language="Tamil"),
            _make_episode(content_group="abc", language="English"),
            _make_episode(content_group="abc", language="Hindi"),
        ]

        result = _group_episodes_by_content_group(episodes, storage)
        assert result[0].languages == ["English", "Hindi", "Tamil"]

    def test_english_is_preferred_for_metadata(self):
        """English variant's metadata should be used when available."""
        storage = MagicMock()
        storage.get_url = lambda key: f"/storage/{key}"

        episodes = [
            _make_episode(content_group="abc", language="Hindi", title="हिंदी शीर्षक"),
            _make_episode(content_group="abc", language="English", title="English Title"),
        ]

        result = _group_episodes_by_content_group(episodes, storage)
        assert result[0].title == "English Title"


class TestSeason0Handling:
    """Tests for Season 0 (trailer) handling."""

    def test_season_0_excluded_from_seasons(self):
        """Season 0 should not appear in the catalogue seasons list."""
        storage = MagicMock()
        storage.get_url = lambda key: f"/storage/{key}"

        trailer_ep = _make_episode(content_group="trailer", title="Trailer")
        normal_ep = _make_episode(content_group="ep1", title="Episode 1")

        season0 = _make_season(season_number=0, title="Trailers", episodes=[trailer_ep])
        season1 = _make_season(season_number=1, title="Season 1", episodes=[normal_ep])

        shows = [_make_show(seasons=[season0, season1])]
        catalogue = _build_catalogue(shows, storage)

        for section in catalogue.sections:
            for show in section.shows:
                for season in show.seasons:
                    assert season.season_number != 0, "Season 0 should not appear in seasons"

    def test_season_0_appears_as_trailers(self):
        """Season 0 episodes should appear in trailers."""
        storage = MagicMock()
        storage.get_url = lambda key: f"/storage/{key}"

        trailer_ep = _make_episode(content_group="trailer-01", title="Official Trailer")
        season0 = _make_season(season_number=0, title="Trailers", episodes=[trailer_ep])
        season1 = _make_season(season_number=1, title="Season 1", episodes=[
            _make_episode(content_group="s1e1"),
        ])

        shows = [_make_show(seasons=[season0, season1])]
        catalogue = _build_catalogue(shows, storage)

        for section in catalogue.sections:
            for show in section.shows:
                assert len(show.trailers) > 0, "Trailers should be populated from Season 0"


class TestDeterministicOrdering:
    """Tests for deterministic catalogue ordering."""

    def test_sections_follow_predefined_order(self):
        """Sections should follow the predefined order."""
        storage = MagicMock()
        storage.get_url = lambda key: f"/storage/{key}"

        ep1 = _make_episode(content_group="doc-ep")
        ep2 = _make_episode(content_group="kids-ep")
        ep3 = _make_episode(content_group="feat-ep")

        shows = [
            _make_show(title="Doc Show", section="Documentary", seasons=[
                _make_season(episodes=[ep1])
            ]),
            _make_show(title="Kids Show", section="Kids", seasons=[
                _make_season(episodes=[ep2])
            ]),
            _make_show(title="Featured Show", section="Featured", seasons=[
                _make_season(episodes=[ep3])
            ]),
        ]

        catalogue = _build_catalogue(shows, storage)
        section_names = [s.name for s in catalogue.sections]

        # Should follow SECTION_ORDER
        expected_order = [s for s in SECTION_ORDER if s in section_names]
        assert section_names == expected_order

    def test_shows_sorted_alphabetically(self):
        """Shows within a section should be sorted by title."""
        storage = MagicMock()
        storage.get_url = lambda key: f"/storage/{key}"

        shows = [
            _make_show(title="Zebra Show", section="Kids", seasons=[
                _make_season(episodes=[_make_episode(content_group="z-ep")])
            ]),
            _make_show(title="Apple Show", section="Kids", seasons=[
                _make_season(episodes=[_make_episode(content_group="a-ep")])
            ]),
        ]

        catalogue = _build_catalogue(shows, storage)
        show_titles = [s.title for s in catalogue.sections[0].shows]
        assert show_titles == ["Apple Show", "Zebra Show"]

    def test_episodes_sorted_by_number(self):
        """Episodes should be sorted by episode number."""
        storage = MagicMock()
        storage.get_url = lambda key: f"/storage/{key}"

        episodes = [
            _make_episode(content_group="ep3", episode_number=3),
            _make_episode(content_group="ep1", episode_number=1),
            _make_episode(content_group="ep2", episode_number=2),
        ]

        result = _group_episodes_by_content_group(episodes, storage)
        numbers = [e.episode_number for e in result]
        assert numbers == [1, 2, 3]


class TestUnpublishedContentExclusion:
    """Tests for excluding unpublished content."""

    def test_draft_episodes_excluded(self):
        """Draft episodes should not appear in the catalogue."""
        storage = MagicMock()
        storage.get_url = lambda key: f"/storage/{key}"

        published_ep = _make_episode(content_group="pub-ep", status="published")
        draft_ep = _make_episode(content_group="draft-ep", status="draft")

        season = _make_season(episodes=[published_ep, draft_ep])
        shows = [_make_show(seasons=[season])]

        catalogue = _build_catalogue(shows, storage)

        all_content_groups = []
        for section in catalogue.sections:
            for show in section.shows:
                for s in show.seasons:
                    for ep in s.episodes:
                        all_content_groups.append(ep.content_group)

        assert "pub-ep" in all_content_groups
        assert "draft-ep" not in all_content_groups
