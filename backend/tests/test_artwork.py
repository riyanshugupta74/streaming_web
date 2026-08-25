"""Tests for artwork validation service."""

import io
import pytest
from PIL import Image
from app.services.artwork_service import validate_artwork, ARTWORK_SPECS


def _create_test_image(width: int, height: int, format: str = "JPEG") -> bytes:
    """Create a test image in memory."""
    img = Image.new("RGB", (width, height), color=(100, 100, 100))
    buffer = io.BytesIO()
    img.save(buffer, format=format, quality=85)
    return buffer.getvalue()


def _create_large_image(width: int, height: int, target_kb: int = 250) -> bytes:
    """Create a large test image that exceeds size limits."""
    import random
    random.seed(42)
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            pixels[x, y] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    data = buffer.getvalue()
    # If still too small, pad it (though random noise PNG should be large)
    if len(data) < target_kb * 1024:
        # Use BMP for guaranteed size
        buffer = io.BytesIO()
        img.save(buffer, format="BMP")
        data = buffer.getvalue()
    return data


class TestPosterValidation:
    """Tests for poster artwork validation."""

    def test_valid_poster(self):
        """A 600x900 JPEG under 200KB should be valid."""
        data = _create_test_image(600, 900)
        result = validate_artwork(data, "poster")
        assert result.valid is True
        assert result.width == 600
        assert result.height == 900
        assert len(result.errors) == 0

    def test_poster_wrong_ratio(self):
        """An 800x800 image (1:1) should fail the 2:3 ratio check."""
        data = _create_test_image(800, 800)
        result = validate_artwork(data, "poster")
        assert result.valid is False
        assert any("aspect ratio" in e.lower() or "ratio" in e.lower() for e in result.errors)
        assert result.width == 800
        assert result.height == 800

    def test_poster_too_small(self):
        """A tiny poster should fail dimension check."""
        data = _create_test_image(100, 150)  # 2:3 ratio but too small
        result = validate_artwork(data, "poster")
        assert result.valid is False
        assert any("too small" in e.lower() or "minimum" in e.lower() for e in result.errors)

    def test_poster_too_large_file(self):
        """A poster exceeding 200KB should be rejected."""
        data = _create_large_image(600, 900, 250)
        result = validate_artwork(data, "poster")
        assert result.valid is False
        assert any("too large" in e.lower() or "maximum" in e.lower() for e in result.errors)

    def test_poster_invalid_file(self):
        """A non-image file should be rejected."""
        data = b"this is not an image"
        result = validate_artwork(data, "poster")
        assert result.valid is False
        assert any("not a valid image" in e.lower() for e in result.errors)


class TestBannerValidation:
    """Tests for banner artwork validation."""

    def test_valid_banner(self):
        """A 1280x720 JPEG under 200KB should be valid."""
        data = _create_test_image(1280, 720)
        result = validate_artwork(data, "banner")
        assert result.valid is True
        assert result.width == 1280
        assert result.height == 720

    def test_banner_wrong_ratio(self):
        """A square banner should fail."""
        data = _create_test_image(720, 720)
        result = validate_artwork(data, "banner")
        assert result.valid is False


class TestThumbnailValidation:
    """Tests for thumbnail artwork validation."""

    def test_valid_thumbnail(self):
        """A 640x360 JPEG under 200KB should be valid."""
        data = _create_test_image(640, 360)
        result = validate_artwork(data, "thumbnail")
        assert result.valid is True
        assert result.width == 640
        assert result.height == 360

    def test_thumbnail_too_small(self):
        """A 160x90 thumbnail should be rejected (too small)."""
        data = _create_test_image(160, 90)
        result = validate_artwork(data, "thumbnail")
        assert result.valid is False
        assert any("too small" in e.lower() or "minimum" in e.lower() for e in result.errors)


class TestUnknownType:
    """Tests for unknown artwork types."""

    def test_unknown_type(self):
        """An unknown artwork type should be rejected."""
        data = _create_test_image(600, 900)
        result = validate_artwork(data, "unknown")
        assert result.valid is False


class TestHumanReadableErrors:
    """Tests that error messages are useful to non-technical users."""

    def test_error_includes_required_specs(self):
        """Error details should include what is required."""
        data = _create_test_image(800, 800)  # Wrong ratio for poster
        result = validate_artwork(data, "poster")
        assert result.details is not None
        assert "2:3" in result.details
        assert "600" in result.details
        assert "900" in result.details
        assert "200 KB" in result.details

    def test_error_includes_actual_dimensions(self):
        """Error details should include what was uploaded."""
        data = _create_test_image(800, 800)
        result = validate_artwork(data, "poster")
        assert "800 × 800" in result.details or "800" in result.details
