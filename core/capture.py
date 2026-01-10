"""Screenshot capture with compression for upload."""

import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import mss
from PIL import Image

from config import TEMP_DIR, IMAGE_MAX_WIDTH, IMAGE_QUALITY, IMAGE_FORMAT

logger = logging.getLogger(__name__)

# Sticky engine state
_last_engine = "mss"


def capture_screen(
    monitor: int = 0,
    save_path: Optional[Path] = None,
) -> Tuple[bytes, Path]:
    """
    Capture the screen and return image bytes and file path.
    Uses a 'sticky' engine to remember what worked last time.
    """
    global _last_engine
    import subprocess
    import shutil
    import os

    # Generate filename if not provided
    if save_path is None:
        ext = IMAGE_FORMAT.lower()
        if ext == "jpeg": ext = "jpg"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = TEMP_DIR / f"capture_{timestamp}.{ext}"

    def try_mss():
        with mss.mss() as sct:
            mon = sct.monitors[monitor]
            screenshot = sct.grab(mon)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Save to disk
            img.save(save_path, format=IMAGE_FORMAT, quality=IMAGE_QUALITY, optimize=True)
            
            # Get bytes
            buffer = io.BytesIO()
            img.save(buffer, format=IMAGE_FORMAT, quality=IMAGE_QUALITY, optimize=True)
            return buffer.getvalue()

    def try_scrot():
        if not shutil.which("scrot"): raise Exception("scrot not found")
        # scrot saves to file directly
        subprocess.run(["scrot", "-o", str(save_path)], check=True, capture_output=True)
        if save_path.exists():
            with open(save_path, "rb") as f:
                return f.read()
        raise Exception("scrot failed to create file")

    def try_grim():
        if not shutil.which("grim"): raise Exception("grim not found")
        subprocess.run(["grim", str(save_path)], check=True, capture_output=True)
        if save_path.exists():
            with open(save_path, "rb") as f:
                return f.read()
        raise Exception("grim failed to create file")

    engines = {
        "mss": try_mss,
        "scrot": try_scrot,
        "grim": try_grim
    }

    # 1. Try last successful engine first (Sticky)
    if _last_engine in engines:
        try:
            image_bytes = engines[_last_engine]()
            return image_bytes, save_path
        except Exception as e:
            logger.warning(f"Sticky engine '{_last_engine}' failed: {e}. Resetting to search.")

    # 2. Search for a working engine
    for name, func in engines.items():
        if name == _last_engine: continue  # Already tried
        try:
            image_bytes = func()
            _last_engine = name
            logger.info(f"✨ Found working capture engine: {name}")
            return image_bytes, save_path
        except Exception:
            continue

    raise RuntimeError("All screen capture methods failed. Please ensure 'scrot' or 'grim' is installed.")


def compress_image_for_upload(
    image_source: bytes | Path,
    max_width: int = IMAGE_MAX_WIDTH,
    quality: int = IMAGE_QUALITY,
) -> bytes:
    """
    Compress and resize image for upload.
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
    
    # Compress using WebP or preferred format
    buffer = io.BytesIO()
    img.save(buffer, format=IMAGE_FORMAT, quality=quality, optimize=True)
    compressed = buffer.getvalue()
    
    logger.debug(f"Compressed {IMAGE_FORMAT}: {len(compressed)} bytes (quality={quality})")
    
    return compressed


def cleanup_old_captures(max_age_minutes: int = 60) -> int:
    """Remove old capture files from temp directory."""
    import time
    
    deleted = 0
    cutoff = time.time() - (max_age_minutes * 60)
    
    # Look for both jpg and webp
    for ext in ["*.jpg", "*.webp"]:
        for file in TEMP_DIR.glob(f"capture_{ext}"):
            if file.stat().st_mtime < cutoff:
                file.unlink()
                deleted += 1
    
    if deleted:
        logger.debug(f"Cleaned up {deleted} old capture files")
    
    return deleted
