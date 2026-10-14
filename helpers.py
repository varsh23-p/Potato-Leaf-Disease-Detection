import io, random
from PIL import Image, ImageDraw


def _save(img, fmt="PNG"):
    buf = io.BytesIO()
    img.save(buf, fmt)
    return buf.getvalue()


def make_leaf(kind="healthy", size=(200, 200), fmt="PNG", seed=1):
    """Synthetic leaf image. kind: healthy | early | late"""
    rnd = random.Random(seed)
    img = Image.new("RGB", size, (60, 140, 55))
    d = ImageDraw.Draw(img)
    w, h = size
    for _ in range(300):                       # texture
        x, y = rnd.randrange(w), rnd.randrange(h)
        d.point((x, y), fill=(50 + rnd.randrange(30), 120 + rnd.randrange(40), 45 + rnd.randrange(25)))
    if kind == "early":                        # brown concentric spots
        for _ in range(8):
            x, y, r = rnd.randrange(w), rnd.randrange(h), max(3, w // 22)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(140, 85, 40))
    elif kind == "late":                       # large dark patches
        for _ in range(4):
            x, y, r = rnd.randrange(w), rnd.randrange(h), max(8, w // 6)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(35, 30, 25))
    return _save(img, fmt)


def make_non_leaf(size=(200, 200)):
    """Dark photo of a non-plant object (very dark blue-grey)."""
    img = Image.new("RGB", size, (25, 28, 45))
    d = ImageDraw.Draw(img)
    d.rectangle((20, 20, size[0] // 2, size[1] // 2), fill=(40, 40, 60))
    return _save(img)


def make_image(size, fmt="PNG", color=(60, 140, 55)):
    return _save(Image.new("RGB", size, color), fmt)


def pad_to(data, nbytes):
    """Append trailing zero bytes (ignored by decoders) so len(data) == nbytes."""
    assert len(data) <= nbytes
    return data + b"\x00" * (nbytes - len(data))
