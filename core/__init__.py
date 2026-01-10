"""Core modules for screen capture, OCR, and storage."""

from .capture import capture_screen, compress_image_for_upload
from .ocr import extract_text, get_ocr_reader
from .uploader import upload_to_api
from .storage import get_token, set_token, is_configured

__all__ = [
    "capture_screen",
    "compress_image_for_upload",
    "extract_text",
    "get_ocr_reader",
    "upload_to_api",
    "get_token",
    "set_token",
    "is_configured",
]
