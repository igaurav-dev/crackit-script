"""SQLite-based local storage for configuration and tokens."""

import sqlite3
from pathlib import Path
from typing import Optional

from config import DATA_DIR

# Database path - stored in user's app data directory
DB_PATH = DATA_DIR / "sync_data.db"


def _get_connection() -> sqlite3.Connection:
    """Get database connection, creating tables if needed."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def get_setting(key: str) -> Optional[str]:
    """Get a setting value by key."""
    conn = _get_connection()
    cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def set_setting(key: str, value: str) -> None:
    """Set a setting value (insert or update)."""
    conn = _get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()


def delete_setting(key: str) -> bool:
    """Delete a setting by key. Returns True if deleted."""
    conn = _get_connection()
    cursor = conn.execute("DELETE FROM settings WHERE key = ?", (key,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# Token functions
def get_token() -> Optional[str]:
    """Get the stored API token."""
    return get_setting("token")


def set_token(token: str) -> None:
    """Store the API token."""
    set_setting("token", token)


# API endpoint
def get_api_endpoint() -> str:
    """Get stored API endpoint or default."""
    from config import API_ENDPOINT
    return get_setting("api_endpoint") or API_ENDPOINT


def set_api_endpoint(url: str) -> None:
    """Store custom API endpoint."""
    set_setting("api_endpoint", url)


# Token permissions (cached from validation)
def get_token_permissions() -> dict:
    """Get cached token metadata (permissions, expiry, etc)."""
    import json
    data = get_setting("token_metadata")
    if data:
        try:
            return json.loads(data)
        except:
            pass
    return {"text_upload": True, "image_upload": True, "vision_ai": False, "valid_till": None}


def set_token_metadata(data: dict) -> None:
    """Cache token validation response metadata."""
    import json
    # Keep only relevant fields
    meta = {
        "text_upload": data.get("text_upload", True),
        "image_upload": data.get("image_upload", True),
        "vision_ai": data.get("vision_ai", False),
        "valid_till": data.get("valid_till"),
        "status": data.get("status"),
    }
    set_setting("token_metadata", json.dumps(meta))


def is_configured() -> bool:
    """Check if the service has been set up (token exists)."""
    return get_token() is not None
