"""Configuration - minimal hardcoded settings."""

import os
import sys
import tempfile
from pathlib import Path

# Platform detection
PLATFORM = sys.platform
IS_WINDOWS = PLATFORM == 'win32'
IS_MACOS = PLATFORM == 'darwin'
IS_LINUX = PLATFORM.startswith('linux')
DAEMON_SUPPORTED = not IS_WINDOWS

# Fixed capture interval (2 seconds)
CAPTURE_INTERVAL = 2  # seconds

# Socket / Upload Endpoint
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://0.0.0.0:8000")
API_TIMEOUT = 30

# OCR Configuration
OCR_LANGUAGES = ["en"]
OCR_GPU = False

# Image compression
IMAGE_MAX_WIDTH = 1280  # Max width for uploaded images
IMAGE_QUALITY = 80      # WebP quality (1-100)
IMAGE_FORMAT = "WEBP"

# Storage directory
def _get_data_dir() -> Path:
    """Get platform-appropriate data directory."""
    if IS_WINDOWS:
        base = Path.home() / "AppData" / "Local" / "SyncService"
    elif IS_MACOS:
        base = Path.home() / "Library" / "Application Support" / "SyncService"
    else:
        base = Path.home() / ".local" / "share" / "SyncService"
    base.mkdir(parents=True, exist_ok=True)
    return base

DATA_DIR = _get_data_dir()
TEMP_DIR = Path(tempfile.gettempdir()) / "sync_cache"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5

# Logging
LOG_LEVEL = "INFO"
