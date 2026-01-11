"""OCR module for text extraction."""

import logging
from pathlib import Path
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

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
