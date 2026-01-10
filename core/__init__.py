"""Core modules for screen capture and upload."""

from .capture import capture_screen, compress_image_for_upload, cleanup_old_captures
from .uploader import upload_image, validate_token
from .storage import (
    get_token, set_token,
    get_api_endpoint, set_api_endpoint,
    get_token_permissions, set_token_permissions,
    is_configured,
)

__all__ = [
    "capture_screen",
    "compress_image_for_upload", 
    "cleanup_old_captures",
    "upload_image",
    "validate_token",
    "get_token",
    "set_token",
    "get_api_endpoint",
    "set_api_endpoint",
    "get_token_permissions",
    "set_token_permissions",
    "is_configured",
]
