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
    Uses mss as primary engine, falls back to system tools on Linux (Raspberry Pi).
    """
    import subprocess
    import shutil
    import os

    # Generate filename if not provided
    if save_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = TEMP_DIR / f"capture_{timestamp}.jpg"

    # Try Primary: MSS
    try:
        with mss.mss() as sct:
            mon = sct.monitors[monitor]
            screenshot = sct.grab(mon)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img.save(save_path, format="JPEG", quality=85, optimize=True)
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            return buffer.getvalue(), save_path
            
    except Exception as e:
        logger.warning(f"Native capture (mss) failed: {e}. Trying system fallbacks...")

    # Fallback 1: scrot (Standard X11 screenshot tool for Linux/Pi)
    if shutil.which("scrot"):
        try:
            # scrot saves to file directly
            subprocess.run(["scrot", "-o", str(save_path)], check=True, capture_output=True)
            if save_path.exists():
                with open(save_path, "rb") as f:
                    return f.read(), save_path
        except Exception as e:
            logger.warning(f"scrot fallback failed: {e}")

    # Fallback 2: grim (For Wayland, common on newer Raspberry Pi OS)
    if shutil.which("grim"):
        try:
            subprocess.run(["grim", str(save_path)], check=True, capture_output=True)
            if save_path.exists():
                with open(save_path, "rb") as f:
                    return f.read(), save_path
        except Exception as e:
            logger.warning(f"grim fallback failed: {e}")

    # Fallback 3: generic 'import' from ImageMagick
    if shutil.which("import"):
        try:
            subprocess.run(["import", "-window", "root", str(save_path)], check=True, capture_output=True)
            if save_path.exists():
                with open(save_path, "rb") as f:
                    return f.read(), save_path
        except Exception as e:
            logger.warning(f"import (imagemagick) failed: {e}")

    raise RuntimeError("All screen capture methods failed. Please ensure 'scrot' or 'grim' is installed.")


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
