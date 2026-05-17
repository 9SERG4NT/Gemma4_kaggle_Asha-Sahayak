import logging
import unicodedata

from PIL import Image

from config import MAX_IMAGE_DIMENSION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def resize_image(image: Image.Image) -> Image.Image:
    """
    Resize image so neither dimension exceeds MAX_IMAGE_DIMENSION.
    Preserves aspect ratio. Returns the original if already within limits.
    No PII or image data is logged.
    """
    w, h = image.size
    if w <= MAX_IMAGE_DIMENSION and h <= MAX_IMAGE_DIMENSION:
        return image

    scale = MAX_IMAGE_DIMENSION / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    logger.info("Resizing image from %dx%d to %dx%d", w, h, new_w, new_h)
    return image.resize((new_w, new_h), Image.LANCZOS)


def contains_devanagari(text: str) -> bool:
    """Return True if text contains at least one Devanagari character."""
    return any(unicodedata.name(ch, "").startswith("DEVANAGARI") for ch in text)
