#!/bin/bash
# Setup script for Sync Service
# Creates virtual environment and installs dependencies

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
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Create virtual environment
VENV_DIR="$SCRIPT_DIR/venv"
echo ""
echo "Creating virtual environment..."

if [ -d "$VENV_DIR" ]; then
    echo "✅ Virtual environment already exists"
else
    $PYTHON -m venv "$VENV_DIR"
    echo "✅ Virtual environment created"
fi

# Activate venv
source "$VENV_DIR/bin/activate"
echo "✅ Activated virtual environment"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt -q

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "⚠️  Some dependencies may have failed"
fi

# Make executable
chmod +x sync_service.py

# Create launcher script
cat > "$SCRIPT_DIR/run" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
python "$SCRIPT_DIR/sync_service.py" "$@"
EOF
chmod +x "$SCRIPT_DIR/run"
echo "✅ Created launcher script: ./run"

echo ""
echo "====================="
echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  ./run setup    # Configure"
echo "  ./run start    # Start service"
echo "  ./run stop     # Stop service"
echo "  ./run status   # Check status"
echo ""
