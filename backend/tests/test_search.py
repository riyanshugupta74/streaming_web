"""Tests for catalogue search logic."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.publish_service import search_catalogue


def _make_storage_with_catalogue(catalogue_data: dict):
    """Create a mock storage backend with a catalogue."""
    storage = MagicMock()

    pointer = json.dumps({
        "current": "catalogues/test-catalogue.json",
    }).encode("utf-8")

    catalogue_bytes = json.dumps(catalogue_data).encode("utf-8")

    async def mock_get(key):
        if key == "catalogues/current.json":
            return pointer
        if key == "catalogues/test-catalogue.json":
            return catalogue_bytes
        return None

    storage.get = mock_get
    return storage


SAMPLE_CATALOGUE = {
    "version": "test",
    "published_at": "2024-01-01T00:00:00",
    "sections": [
        {
            "name": "Kids",
            "shows": [
                {
                    "id": "show-1",
                    "title": "Space Rangers",
                    "synopsis": "Space adventure for kids",
                    "category": "Kids",
                    "artwork": {},
                    "seasons": [
                        {
                            "season_number": 1,
                            "title": "Season 1",
                            "episodes": [
                                {
                                    "content_group": "space-s1e1",
                                    "episode_number": 1,
                                    "title": "Launch Day",
                                    "description": "The rangers prepare.",
                                    "duration": 1800,
                                    "languages": ["English", "Hindi"],
                                    "artwork": {},
                                }
                            ],
                        }
                    ],
                    "trailers": [],
                }
            ],
        },
        {
            "name": "Adventure",
            "shows": [
                {
                    "id": "show-2",
                    "title": "The Lion's Journey",
                    "synopsis": "A young lion...",
                    "category": "Adventure",
                    "artwork": {},
                    "seasons": [
                        {
                            "season_number": 1,
                            "title": "Season 1",
                            "episodes": [
                                {
                                    "content_group": "lions-s1e1",
                                    "episode_number": 1,
                                    "title": "The Cub",
                                    "description": "A lion cub is born.",
                                    "duration": 2700,
                                    "languages": ["English", "Hindi"],
                                    "artwork": {},
                                }
                            ],
                        }
                    ],
                    "trailers": [],
                }
            ],
        },
    ],
}


class TestSearchByTitle:
    """Tests for title-based search."""

    @pytest.mark.asyncio
    async def test_search_show_title(self):
        """Searching for 'lion' should find The Lion's Journey."""
        storage = _make_storage_with_catalogue(SAMPLE_CATALOGUE)
        result = await search_catalogue(storage, q="lion")
        assert result["total_results"] == 1
        assert result["sections"][0]["shows"][0]["title"] == "The Lion's Journey"

    @pytest.mark.asyncio
    async def test_search_episode_title(self):
        """Searching for 'launch' should find Space Rangers (via episode title)."""
        storage = _make_storage_with_catalogue(SAMPLE_CATALOGUE)
        result = await search_catalogue(storage, q="launch")
        assert result["total_results"] == 1
        assert result["sections"][0]["shows"][0]["title"] == "Space Rangers"

    @pytest.mark.asyncio
    async def test_search_category(self):
        """Searching for 'kids' should match the category."""
        storage = _make_storage_with_catalogue(SAMPLE_CATALOGUE)
        result = await search_catalogue(storage, q="kids")
        assert result["total_results"] >= 1


class TestFilters:
    """Tests for filter composition."""

    @pytest.mark.asyncio
    async def test_category_filter(self):
        """Category filter should only return matching shows."""
        storage = _make_storage_with_catalogue(SAMPLE_CATALOGUE)
        result = await search_catalogue(storage, category="Kids")
        assert result["total_results"] == 1
        assert all(
            s["category"] == "Kids"
            for section in result["sections"]
            for s in section["shows"]
        )

    @pytest.mark.asyncio
    async def test_language_filter(self):
        """Language filter should only return shows with episodes in that language."""
        storage = _make_storage_with_catalogue(SAMPLE_CATALOGUE)
        result = await search_catalogue(storage, language="Hindi")
        assert result["total_results"] == 2  # Both shows have Hindi

    @pytest.mark.asyncio
    async def test_section_filter(self):
        """Section filter should only return the matching section."""
        storage = _make_storage_with_catalogue(SAMPLE_CATALOGUE)
        result = await search_catalogue(storage, section="Kids")
        assert len(result["sections"]) == 1
        assert result["sections"][0]["name"] == "Kids"

    @pytest.mark.asyncio
    async def test_composed_filters(self):
        """Multiple filters should compose together (AND)."""
        storage = _make_storage_with_catalogue(SAMPLE_CATALOGUE)
        result = await search_catalogue(storage, q="lion", category="Kids")
        # Lion's Journey is Adventure, not Kids, so should return 0
        assert result["total_results"] == 0

    @pytest.mark.asyncio
    async def test_no_results(self):
        """A search with no matches should return empty results."""
        storage = _make_storage_with_catalogue(SAMPLE_CATALOGUE)
        result = await search_catalogue(storage, q="nonexistent")
        assert result["total_results"] == 0
        assert len(result["sections"]) == 0
