"""Screenshot capture with compression for upload."""

import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import mss
from PIL import Image

from config import TEMP_DIR, IMAGE_MAX_WIDTH, IMAGE_QUALITY

logger = logging.getLogger(__name__)


def capture_screen(
    monitor: int = 0,
    save_path: Optional[Path] = None,
) -> Tuple[bytes, Path]:
    """
    Capture the screen and return image bytes and file path.
    
    Args:
        monitor: Monitor index (0 = all, 1+ = specific monitor)
        save_path: Optional path to save the image
    
    Returns:
        Tuple of (image_bytes, file_path)
    """
    with mss.mss() as sct:
        mon = sct.monitors[monitor]
        screenshot = sct.grab(mon)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        # Generate filename if not provided
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = TEMP_DIR / f"capture_{timestamp}.jpg"
        
        # Save original for OCR (full quality)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        image_bytes = buffer.getvalue()
        
        # Save to disk
        img.save(save_path, format="JPEG", quality=85, optimize=True)
        
        logger.debug(f"Captured screen: {save_path} ({len(image_bytes)} bytes)")
        
        return image_bytes, save_path


def compress_image_for_upload(
    image_source: bytes | Path,
    max_width: int = IMAGE_MAX_WIDTH,
    quality: int = IMAGE_QUALITY,
) -> bytes:
    """
    Compress and resize image for upload.
    
    Args:
        image_source: Image bytes or path to image file
        max_width: Maximum width (maintains aspect ratio)
        quality: JPEG quality (1-100)
    
    Returns:
        Compressed image bytes
    """
    # Load image
    if isinstance(image_source, Path):
        img = Image.open(image_source)
    else:
        img = Image.open(io.BytesIO(image_source))
    
    # Convert to RGB if needed
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    # Resize if wider than max_width
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    
    # Compress
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    compressed = buffer.getvalue()
    
    logger.debug(f"Compressed image: {len(compressed)} bytes (quality={quality})")
    
    return compressed


def cleanup_old_captures(max_age_minutes: int = 60) -> int:
    """Remove old capture files from temp directory."""
    import time
    
    deleted = 0
    cutoff = time.time() - (max_age_minutes * 60)
    
    for file in TEMP_DIR.glob("capture_*.jpg"):
        if file.stat().st_mtime < cutoff:
            file.unlink()
            deleted += 1
    
    if deleted:
        logger.debug(f"Cleaned up {deleted} old capture files")
    
    return deleted
