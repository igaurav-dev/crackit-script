"""API upload module - image upload only."""

import logging
from datetime import datetime
import base64

import httpx

from config import API_TIMEOUT
from core.storage import get_api_endpoint

logger = logging.getLogger(__name__)


def upload_image(token: str, image_bytes: bytes) -> None:
    """Upload image to the socket server. Silent operation."""
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
            else:
                logger.error(f"Image upload failed: {response.status_code}")
    except Exception as e:
        logger.error(f"Image upload error: {e}")


def upload_text(token: str, text: str) -> None:
    """Upload OCR text to the socket server."""
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
            else:
                logger.error(f"Text upload failed: {response.status_code}")
    except Exception as e:
        logger.error(f"Text upload error: {e}")


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
