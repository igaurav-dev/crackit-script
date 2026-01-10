#!/bin/bash
# Setup script for Sync Service
# Checks Python, installs dependencies, makes script runnable

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 Sync Service Setup"
echo "====================="
echo ""

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON="python3"
    VERSION=$($PYTHON --version 2>&1 | cut -d' ' -f2)
    echo "✅ Python found: $VERSION"
elif command -v python &> /dev/null; then
    PYTHON="python"
    VERSION=$($PYTHON --version 2>&1 | cut -d' ' -f2)
    echo "✅ Python found: $VERSION"
else
    echo "❌ Python not found!"
    echo ""
    echo "Please install Python 3.9+ from:"
    echo "  - macOS: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  - Windows: https://python.org/downloads"
    exit 1
fi

# Check pip
echo ""
echo "Checking pip..."
if $PYTHON -m pip --version &> /dev/null; then
    echo "✅ pip available"
else
    echo "❌ pip not found!"
    echo "Installing pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | $PYTHON
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
$PYTHON -m pip install --user -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "⚠️  Some dependencies may have failed"
fi

# Make executable
chmod +x sync_service.py
echo "✅ Made sync_service.py executable"

# Create symlink for easy access (optional)
echo ""
echo "====================="
echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  $PYTHON sync_service.py setup    # Configure"
echo "  $PYTHON sync_service.py start    # Start service"
echo "  $PYTHON sync_service.py stop     # Stop service"
echo "  $PYTHON sync_service.py status   # Check status"
echo ""
