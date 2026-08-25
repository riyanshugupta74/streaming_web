"""Artwork validation service.

Validates uploaded images against dimension, aspect ratio,
and file size requirements using actual image inspection.
"""

import io
from dataclasses import dataclass
from typing import Optional

from PIL import Image


# ─── Artwork specifications ─────────────────────────────────────────────────

ARTWORK_SPECS = {
    "poster": {
        "aspect_ratio": (2, 3),
        "target_width": 600,
        "target_height": 900,
        "max_size_bytes": 204800,  # 200 KB
        "min_width": 300,
        "max_width": 1200,
        "label": "Poster",
    },
    "banner": {
        "aspect_ratio": (16, 9),
        "target_width": 1280,
        "target_height": 720,
        "max_size_bytes": 204800,  # 200 KB
        "min_width": 640,
        "max_width": 2560,
        "label": "Banner",
    },
    "thumbnail": {
        "aspect_ratio": (16, 9),
        "target_width": 640,
        "target_height": 360,
        "max_size_bytes": 204800,  # 200 KB
        "min_width": 320,
        "max_width": 1280,
        "label": "Thumbnail",
    },
}

ASPECT_RATIO_TOLERANCE = 0.03  # 3% tolerance for aspect ratio matching


@dataclass
class ArtworkValidationResult:
    """Result of artwork validation."""
    valid: bool
    width: int = 0
    height: int = 0
    size_bytes: int = 0
    errors: list[str] = None
    details: Optional[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


def validate_artwork(
    file_data: bytes,
    artwork_type: str,
) -> ArtworkValidationResult:
    """
    Validate an artwork file against specifications.

    Uses actual image inspection via Pillow - not just file extension.
    Returns structured validation result with human-readable errors.
    """
    if artwork_type not in ARTWORK_SPECS:
        return ArtworkValidationResult(
            valid=False,
            errors=[f"Unknown artwork type: {artwork_type}. Must be one of: {', '.join(ARTWORK_SPECS.keys())}"],
        )

    spec = ARTWORK_SPECS[artwork_type]
    errors = []
    width = 0
    height = 0
    size_bytes = len(file_data)

    # 1. Check file size
    max_kb = spec["max_size_bytes"] / 1024
    if size_bytes > spec["max_size_bytes"]:
        actual_kb = size_bytes / 1024
        errors.append(
            f"File is too large ({actual_kb:.1f} KB). Maximum allowed: {max_kb:.0f} KB."
        )

    # 2. Try to open the image
    try:
        img = Image.open(io.BytesIO(file_data))
        img.verify()
        # Re-open after verify (verify() can invalidate the image object)
        img = Image.open(io.BytesIO(file_data))
        width, height = img.size
    except Exception:
        return ArtworkValidationResult(
            valid=False,
            size_bytes=size_bytes,
            errors=["File is not a valid image. Please upload a JPEG or PNG image."],
        )

    # 3. Check aspect ratio
    expected_ratio = spec["aspect_ratio"][0] / spec["aspect_ratio"][1]
    actual_ratio = width / height if height > 0 else 0

    if abs(actual_ratio - expected_ratio) > ASPECT_RATIO_TOLERANCE:
        ratio_str = f"{spec['aspect_ratio'][0]}:{spec['aspect_ratio'][1]}"
        # Try to determine the actual ratio in simple terms
        actual_ratio_str = _simplify_ratio(width, height)
        errors.append(
            f"Wrong aspect ratio. Required: {ratio_str}. "
            f"Your image: {width}×{height} ({actual_ratio_str})."
        )

    # 4. Check dimensions (with tolerance)
    if width < spec["min_width"]:
        errors.append(
            f"Image is too small ({width}×{height}). "
            f"Minimum width: {spec['min_width']}px. "
            f"Recommended size: {spec['target_width']}×{spec['target_height']}."
        )
    elif width > spec["max_width"]:
        errors.append(
            f"Image is too large ({width}×{height}). "
            f"Maximum width: {spec['max_width']}px. "
            f"Recommended size: {spec['target_width']}×{spec['target_height']}."
        )

    if errors:
        ratio_str = f"{spec['aspect_ratio'][0]}:{spec['aspect_ratio'][1]}"
        details = (
            f"{spec['label']} image is invalid.\n\n"
            f"Required:\n"
            f"- Aspect ratio: {ratio_str}\n"
            f"- Approximate size: {spec['target_width']} × {spec['target_height']}\n"
            f"- Maximum file size: {int(max_kb)} KB\n\n"
            f"Your image:\n"
            f"- Size: {width} × {height}\n"
            f"- Aspect ratio: {_simplify_ratio(width, height)}\n"
            f"- File size: {size_bytes / 1024:.1f} KB\n\n"
            f"Please upload a correctly sized image."
        )
    else:
        details = None

    return ArtworkValidationResult(
        valid=len(errors) == 0,
        width=width,
        height=height,
        size_bytes=size_bytes,
        errors=errors,
        details=details,
    )


def _simplify_ratio(width: int, height: int) -> str:
    """Try to express the aspect ratio in simple terms."""
    from math import gcd
    if width == 0 or height == 0:
        return "0:0"
    divisor = gcd(width, height)
    w = width // divisor
    h = height // divisor
    # If the simplified ratio has large numbers, just show the decimal
    if w > 100 or h > 100:
        return f"{width / height:.2f}:1"
    return f"{w}:{h}"
