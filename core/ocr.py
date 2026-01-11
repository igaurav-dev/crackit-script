"""OCR module for text extraction."""

import logging
from pathlib import Path
import pytesseract
from PIL import Image


import sys
import shutil

logger = logging.getLogger(__name__)

# Auto-configure Tesseract path on Windows
if sys.platform == 'win32':
    # If tesseract is not in PATH, try default locations
    if not shutil.which('tesseract'):
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            Path.home() / "AppData" / "Local" / "Programs" / "Tesseract-OCR" / "tesseract.exe"
        ]
        for p in possible_paths:
            if Path(p).exists():
                pytesseract.pytesseract.tesseract_cmd = str(p)
                # logger.debug(f"Found Tesseract at: {p}")
                break


def extract_text(image_source: Path | bytes) -> str:
    """
    Extract text from image using Tesseract OCR.
    """
    try:
        if isinstance(image_source, Path):
            img = Image.open(image_source)
        else:
            from io import BytesIO
            img = Image.open(BytesIO(image_source))
            
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""
