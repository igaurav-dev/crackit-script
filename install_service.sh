#!/bin/bash
# Self-configuring systemd service generator
# Run: ./install_service.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$HOME/.config/systemd/user/sync-service.service"

# Create user systemd directory
mkdir -p "$HOME/.config/systemd/user"

# Find Python
PYTHON_PATH=$(which python3)

# Generate service file
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Sync Service - Screen capture and text sync
After=graphical.target
Wants=graphical.target

[Service]
Type=simple
Environment=DISPLAY=:0
WorkingDirectory=$SCRIPT_DIR
ExecStart=$PYTHON_PATH $SCRIPT_DIR/sync_service.py start -f
Restart=always
RestartSec=30

[Install]
WantedBy=default.target
EOF

echo "✅ Service file created: $SERVICE_FILE"
echo ""
echo "To enable:"
echo "  systemctl --user daemon-reload"
echo "  systemctl --user enable sync-service"
echo "  systemctl --user start sync-service"
echo ""
echo "To check status:"
echo "  systemctl --user status sync-service"
