import sys
from pathlib import Path

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sync_service import run_capture_cycle
from core.storage import get_token

def test_sync():
    token = get_token()
    if not token:
        print("❌ Token not found. Run setup first.")
        return
    
    print(f"🚀 Triggering manual capture cycle with token: {token[:8]}...")
    run_capture_cycle(token, include_image=True)
    print("✅ Capture cycle triggered. Check socket server logs.")

if __name__ == "__main__":
    test_sync()
