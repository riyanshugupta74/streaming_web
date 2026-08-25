"""Generate test asset images for Peblo TV Mini challenge."""
from PIL import Image
import io
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def save_image(img, path, max_kb=None, format="JPEG"):
    """Save image, optionally ensuring it's within or exceeds a size limit."""
    if max_kb and format == "JPEG":
        # Try to hit approximate target size
        quality = 85
        buf = io.BytesIO()
        img.save(buf, format=format, quality=quality)
        if max_kb == "over":
            # Make it too big - fill with random-ish data
            quality = 99
            buf = io.BytesIO()
            img.save(buf, format=format, quality=quality)
            while buf.tell() < 205000:
                # Add noise to increase size
                import random
                pixels = img.load()
                for x in range(img.width):
                    for y in range(img.height):
                        r, g, b = pixels[x, y]
                        pixels[x, y] = (
                            min(255, max(0, r + random.randint(-5, 5))),
                            min(255, max(0, g + random.randint(-5, 5))),
                            min(255, max(0, b + random.randint(-5, 5)))
                        )
                buf = io.BytesIO()
                img.save(buf, format=format, quality=99)
            with open(path, 'wb') as f:
                f.write(buf.getvalue())
            return
        buf = io.BytesIO()
        img.save(buf, format=format, quality=quality)
        with open(path, 'wb') as f:
            f.write(buf.getvalue())
    elif format == "PNG":
        img.save(path, format="PNG")
    else:
        img.save(path, format=format, quality=85)

def create_gradient_image(width, height, color1, color2):
    """Create a simple gradient image."""
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    for y in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * y / height)
        g = int(color1[1] + (color2[1] - color1[1]) * y / height)
        b = int(color1[2] + (color2[2] - color1[2]) * y / height)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    return img

# 1. banner_good.jpg - 1280x720, 16:9, under 200KB
print("Creating banner_good.jpg (1280x720, 16:9)...")
img = create_gradient_image(1280, 720, (30, 60, 120), (60, 120, 200))
save_image(img, os.path.join(ASSETS_DIR, "banner_good.jpg"))

# 2. banner_too_big.png - 1280x720 but as PNG (will be > 200KB)
print("Creating banner_too_big.png (1280x720, 16:9, oversized)...")
img = create_gradient_image(1280, 720, (200, 50, 50), (255, 100, 100))
# Add noise to make it large
import random
random.seed(42)
pixels = img.load()
for x in range(img.width):
    for y in range(img.height):
        r, g, b = pixels[x, y]
        pixels[x, y] = (
            min(255, max(0, r + random.randint(-30, 30))),
            min(255, max(0, g + random.randint(-30, 30))),
            min(255, max(0, b + random.randint(-30, 30)))
        )
save_image(img, os.path.join(ASSETS_DIR, "banner_too_big.png"), format="PNG")

# 3. thumb_good.jpg - 640x360, 16:9, under 200KB
print("Creating thumb_good.jpg (640x360, 16:9)...")
img = create_gradient_image(640, 360, (20, 100, 80), (40, 180, 140))
save_image(img, os.path.join(ASSETS_DIR, "thumb_good.jpg"))

# 4. thumb_tiny.jpg - 160x90, 16:9 ratio but way too small
print("Creating thumb_tiny.jpg (160x90, 16:9 but too small)...")
img = create_gradient_image(160, 90, (80, 80, 80), (150, 150, 150))
save_image(img, os.path.join(ASSETS_DIR, "thumb_tiny.jpg"))

# 5. poster_good.jpg - 600x900, 2:3, under 200KB
print("Creating poster_good.jpg (600x900, 2:3)...")
img = create_gradient_image(600, 900, (100, 30, 100), (180, 60, 180))
save_image(img, os.path.join(ASSETS_DIR, "poster_good.jpg"))

# 6. poster_wrong_ratio.jpg - 800x800, 1:1 (wrong aspect ratio)
print("Creating poster_wrong_ratio.jpg (800x800, 1:1 - wrong ratio)...")
img = create_gradient_image(800, 800, (200, 180, 50), (255, 220, 100))
save_image(img, os.path.join(ASSETS_DIR, "poster_wrong_ratio.jpg"))

# Print file sizes
print("\n--- Asset file sizes ---")
for fname in sorted(os.listdir(ASSETS_DIR)):
    fpath = os.path.join(ASSETS_DIR, fname)
    if os.path.isfile(fpath):
        size = os.path.getsize(fpath)
        print(f"  {fname}: {size:,} bytes ({size/1024:.1f} KB)")

print("\nDone! All test assets created.")
