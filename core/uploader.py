"""API upload module - silent, fire-and-forget."""

import logging
from datetime import datetime
from typing import Optional
import base64

import httpx

from config import API_TIMEOUT
from core.storage import get_api_endpoint, get_token_permissions

logger = logging.getLogger(__name__)


def upload_text(token: str, text: str) -> None:
    """Upload text only. Silent operation."""
    try:
        api_base = get_api_endpoint()
        url = f"{api_base.rstrip('/')}/upload/text/{token}"
        
        payload = {
            "text": text,
            "timestamp": datetime.now().isoformat(),
        }
        
        with httpx.Client(timeout=API_TIMEOUT) as client:
            response = client.post(url, json=payload)
            if response.is_success:
                logger.debug("Text upload success")
    except Exception:
        pass


def upload_image(token: str, image_bytes: bytes) -> None:
    """Upload image only. Silent operation."""
    try:
        api_base = get_api_endpoint()
        url = f"{api_base.rstrip('/')}/upload/image/{token}"
        
        payload = {
            "image": base64.b64encode(image_bytes).decode("utf-8"),
            "timestamp": datetime.now().isoformat(),
        }
        
        with httpx.Client(timeout=API_TIMEOUT) as client:
            response = client.post(url, json=payload)
            if response.is_success:
                logger.debug("Image upload success")
    except Exception:
        pass


def upload_to_api(
    token: str,
    text: str,
    image_bytes: Optional[bytes] = None,
) -> None:
    """
    Upload text and/or image based on token permissions.
    
    Silent operation - never raises exceptions.
    """
    permissions = get_token_permissions()
    
    # Upload text if allowed
    if permissions.get("text_upload", True) and text.strip():
        upload_text(token, text)
    
    # Upload image if allowed
    if permissions.get("image_upload", True) and image_bytes:
        upload_image(token, image_bytes)


def validate_token(token: str) -> dict:
    """
    Validate token with the API.
    
    Returns:
        dict with keys: valid, text_upload, image_upload, message
    """
    try:
        api_base = get_api_endpoint()
        url = f"{api_base.rstrip('/')}/validate/{token}"
        
        with httpx.Client(timeout=API_TIMEOUT) as client:
            response = client.get(url)
            
            if response.is_success:
                return response.json()
            else:
                return {"valid": False, "message": "Invalid response"}
    
    except Exception as e:
        return {"valid": False, "message": str(e)}
