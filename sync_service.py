#!/usr/bin/env python3
"""
Sync Service - Screen capture and text sync CLI.

Usage:
    sync_service setup    # Configure token (one-time)
    sync_service start    # Start the background service
    sync_service stop     # Stop the running service
    sync_service status   # Check service status
"""

import argparse
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    CAPTURE_INTERVAL,
    LOG_LEVEL,
    DATA_DIR,
    TEMP_DIR,
    IS_WINDOWS,
    DAEMON_SUPPORTED,
)
from core.capture import capture_screen, compress_image_for_upload, cleanup_old_captures
from core.uploader import upload_image
from core.storage import (
    get_token, set_token,
    get_api_endpoint, set_api_endpoint,
    is_configured,
)

# PID and Log files
PID_FILE = DATA_DIR / "sync_service.pid"
LOG_FILE = DATA_DIR / "sync_service.log"

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE)
    ],
)
logger = logging.getLogger(__name__)

# Shutdown flag
_running = True


def signal_handler(signum, frame):
    global _running
    logger.info("Shutdown signal received...")
    _running = False


def setup_signal_handlers():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if not IS_WINDOWS:
        signal.signal(signal.SIGHUP, signal_handler)


def write_pid():
    PID_FILE.write_text(str(os.getpid()))


def read_pid() -> int | None:
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except (ValueError, IOError):
            return None
    return None


def remove_pid():
    if PID_FILE.exists():
        PID_FILE.unlink()


def is_running() -> bool:
    pid = read_pid()
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        remove_pid()
        return False


def run_capture_cycle(token: str) -> None:
    """Run a single capture -> upload cycle."""
    try:
        # 1. Capture screen
        _, image_path = capture_screen()
        
        # 2. Upload Image
        try:
            compressed_image = compress_image_for_upload(image_path)
            upload_image(token, compressed_image)
            logger.info("📸 Image uploaded")
        except Exception as e:
            logger.error(f"❌ Image upload failed: {e}")
        finally:
            # Cleanup image after upload
            if image_path.exists():
                image_path.unlink()
        
    except Exception as e:
        logger.error(f"❌ Capture cycle failed: {e}")


def run_loop(token: str):
    """Run the capture loop (2 second interval)."""
    global _running
    
    logger.info(f"Starting capture loop (interval: {CAPTURE_INTERVAL}s)")
    
    cycle_count = 0
    
    while _running:
        cycle_count += 1
        
        run_capture_cycle(token, include_image=include_image)
        
        if cycle_count % 10 == 0:
            cleanup_old_captures()
        
        # Wait for next cycle
        for _ in range(CAPTURE_INTERVAL):
            if not _running:
                break
            time.sleep(1)
    
    logger.info(f"Stopped after {cycle_count} cycles")
    remove_pid()


def daemonize():
    """Fork to daemon (Unix only)."""
    if IS_WINDOWS:
        return
    
    try:
        if os.fork() > 0:
            sys.exit(0)
    except OSError:
        sys.exit(1)
    
    os.chdir("/")
    os.setsid()
    os.umask(0)
    
    try:
        if os.fork() > 0:
            sys.exit(0)
    except OSError:
        sys.exit(1)
    
    sys.stdout.flush()
    sys.stderr.flush()
    with open("/dev/null", "r") as f:
        os.dup2(f.fileno(), sys.stdin.fileno())


# ===== CLI Commands =====

def cmd_setup(args):
    """Setup: configure token and API endpoint."""
    from core.uploader import validate_token
    from core.storage import set_token_metadata
    
    print("\n🔧 Sync Service Setup\n")
    
    # API endpoint
    current_endpoint = get_api_endpoint()
    print(f"Current API endpoint: {current_endpoint}")
    new_endpoint = input(f"Enter API endpoint (or press Enter to keep): ").strip()
    if new_endpoint:
        set_api_endpoint(new_endpoint)
        print(f"✅ API endpoint set to: {new_endpoint}")
    
    # Token
    current_token = get_token()
    if current_token:
        print(f"\nCurrent token: {current_token[:8]}...")
    
    token = input("Enter your API token: ").strip()
    if not token:
        if current_token:
            print("Keeping existing token.")
            return 0
        else:
            print("❌ Token required.")
            return 1
    
    # Validate token with API
    print("\nValidating token...")
    result = validate_token(token)
    
    if not result.get("valid", False):
        print(f"❌ Token invalid: {result.get('message', 'Unknown error')}")
        return 1
    
    # Save token and metadata
    set_token(token)
    set_token_metadata(result)
    
    print(f"✅ Token validated and saved!")
    print(f"   Text upload: {'✓' if result.get('text_upload') else '✗'}")
    print(f"   Image upload: {'✓' if result.get('image_upload') else '✗'}")
    print(f"   Valid until: {result.get('valid_till', 'N/A')}")
    
    # Pre-download OCR models

    print(f"\nData stored at: {DATA_DIR}")
    print("\nRun 'sync_service start' to begin.")
    return 0


def cmd_start(args):
    """Start the capture service."""
    print("\n🚀 Starting Sync Service...\n")
    
    if not is_configured():
        print("❌ Not configured. Run 'sync_service setup' first.")
        return 1
    
    if is_running():
        print(f"⚠️  Already running (PID: {read_pid()})")
        return 1
    
    token = get_token()
    
    if args.foreground:
        print("Running in foreground (Ctrl+C to stop)...")
        print(f"Capture interval: {CAPTURE_INTERVAL} seconds")
        setup_signal_handlers()
        write_pid()
        run_loop(token)
    else:
        if not DAEMON_SUPPORTED:
            print("Use 'sync_service start -f' on Windows.")
            return 1
        
        print("Daemonizing...")
        daemonize()
        setup_signal_handlers()
        write_pid()
        run_loop(token)
    
    return 0


def cmd_stop(args):
    """Stop the service."""
    print("\n🛑 Stopping Sync Service...\n")
    
    pid = read_pid()
    if pid is None:
        print("Service is not running.")
        return 0
    
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"✅ Sent stop signal to PID {pid}")
        
        for _ in range(5):
            time.sleep(1)
            if not is_running():
                print("Service stopped.")
                return 0
        
        if is_running():
            os.kill(pid, signal.SIGKILL)
            print("Force killed.")
        
        remove_pid()
        return 0
        
    except ProcessLookupError:
        print("Service was not running.")
        remove_pid()
        return 0
    except PermissionError:
        print(f"❌ Permission denied for PID {pid}")
        return 1


def cmd_status(args):
    """Show status."""
    if is_running():
        pid = read_pid()
        token = get_token()
        endpoint = get_api_endpoint()
        print(f"✅ Service is RUNNING (PID: {pid})")
        print(f"   Endpoint: {endpoint}")
        print(f"   Token: {token[:8]}..." if token else "   Token: not set")
        print(f"   Interval: {CAPTURE_INTERVAL}s")
        print(f"   Log File: {LOG_FILE}")
    else:
        print("⏹️  Service is NOT RUNNING")
        if is_configured():
            print("   Ready to start")
        else:
            print("   Run 'sync_service setup' first")
    return 0


def cmd_logs(args):
    """View service logs."""
    if not LOG_FILE.exists():
        print("No log file found.")
        return 0
    
    print(f"\n📑 Last {args.lines} log lines:\n")
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines[-args.lines:]:
                print(line.strip())
    except Exception as e:
        print(f"Error reading logs: {e}")
    return 0


def cmd_uninstall(args):
    """Uninstall Crackit completely."""
    import shutil
    
    print("\n🗑️  Uninstalling Crackit...")
    
    # Stop service if running
    if is_running():
        print("Stopping running service...")
        pid = read_pid()
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
            except:
                pass
        remove_pid()
    
    # Remove data directory
    if DATA_DIR.exists():
        print(f"Removing data directory: {DATA_DIR}")
        shutil.rmtree(DATA_DIR, ignore_errors=True)
    
    # Remove temp directory
    if TEMP_DIR.exists():
        print(f"Removing temp directory: {TEMP_DIR}")
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    
    # Instructions for PATH cleanup
    install_dir = Path.home() / ".crackit"
    if install_dir.exists():
        print(f"Removing installation: {install_dir}")
        shutil.rmtree(install_dir, ignore_errors=True)
    
    print("\n✅ Uninstall complete!")
    print("\nTo finish cleanup, remove this line from your shell config (~/.bashrc or ~/.zshrc):")
    print('   export PATH="$HOME/.crackit:$PATH"')
    print("")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Sync Service - Screen capture and text sync",
        prog="sync_service",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # setup
    setup_parser = subparsers.add_parser("setup", help="Configure API token")
    setup_parser.set_defaults(func=cmd_setup)
    
    # start
    start_parser = subparsers.add_parser("start", help="Start the service")
    start_parser.add_argument("-f", "--foreground", action="store_true", help="Run in foreground")
    start_parser.add_argument("--no-image", action="store_true", help="Don't upload images")
    start_parser.set_defaults(func=cmd_start)
    
    # stop
    stop_parser = subparsers.add_parser("stop", help="Stop the service")
    stop_parser.set_defaults(func=cmd_stop)
    
    # status
    status_parser = subparsers.add_parser("status", help="Check status")
    status_parser.set_defaults(func=cmd_status)
    
    # logs
    logs_parser = subparsers.add_parser("logs", help="View background logs")
    logs_parser.add_argument("-n", "--lines", type=int, default=50, help="Number of lines to show")
    logs_parser.set_defaults(func=cmd_logs)
    
    # uninstall
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall Crackit completely")
    uninstall_parser.set_defaults(func=cmd_uninstall)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
