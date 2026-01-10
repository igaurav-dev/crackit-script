#!/bin/bash
#
# Crackit Installer - One-liner installation script
# Usage: curl -fsSL https://raw.githubusercontent.com/igaurav-dev/crackit-script/main/install.sh | bash
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    CRACKIT INSTALLER                       ║"
echo "║           Screen Capture & AI Exam Assistant               ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for required tools
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    # Check Python 3.8+
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
        echo "   Install it with: sudo apt install python3 python3-pip python3-venv"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}❌ pip3 is required but not installed.${NC}"
        echo "   Install it with: sudo apt install python3-pip"
        exit 1
    fi
    echo -e "${GREEN}✓ pip3 found${NC}"
    
    # Check git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ git is required but not installed.${NC}"
        echo "   Install it with: sudo apt install git"
        exit 1
    fi
    echo -e "${GREEN}✓ git found${NC}"
    
    # Check for screen capture tool (Linux)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v scrot &> /dev/null; then
            echo -e "${GREEN}✓ scrot found (screen capture)${NC}"
        elif command -v grim &> /dev/null; then
            echo -e "${GREEN}✓ grim found (screen capture)${NC}"
        else
            echo -e "${YELLOW}⚠ No screen capture tool found. Installing scrot...${NC}"
            sudo apt install -y scrot || echo -e "${RED}Failed to install scrot. Please install manually.${NC}"
        fi
    fi
}

# Installation directory
INSTALL_DIR="$HOME/.crackit"
REPO_URL="https://github.com/igaurav-dev/crackit-script.git"

install_crackit() {
    echo ""
    echo -e "${YELLOW}Installing Crackit to ${INSTALL_DIR}...${NC}"
    
    # Remove existing installation
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}Removing existing installation...${NC}"
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone repository
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create launcher script
    echo -e "${YELLOW}Creating launcher script...${NC}"
    cat > "$INSTALL_DIR/crackit" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$HOME/.crackit"
source "$SCRIPT_DIR/venv/bin/activate"
python "$SCRIPT_DIR/sync_service.py" "$@"
EOF
    chmod +x "$INSTALL_DIR/crackit"
    
    # Add to PATH
    SHELL_RC=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    fi
    
    if [ -n "$SHELL_RC" ]; then
        if ! grep -q "crackit" "$SHELL_RC"; then
            echo "" >> "$SHELL_RC"
            echo "# Crackit" >> "$SHELL_RC"
            echo "export PATH=\"\$HOME/.crackit:\$PATH\"" >> "$SHELL_RC"
            echo -e "${GREEN}✓ Added crackit to PATH in $SHELL_RC${NC}"
        fi
    fi
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              INSTALLATION COMPLETE! 🎉                     ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Quick Start:${NC}"
    echo ""
    echo "  1. Restart your terminal or run:"
    echo -e "     ${YELLOW}source $SHELL_RC${NC}"
    echo ""
    echo "  2. Configure your token:"
    echo -e "     ${YELLOW}crackit setup${NC}"
    echo ""
    echo "  3. Start the service:"
    echo -e "     ${YELLOW}crackit start${NC}"
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo "  crackit setup   - Configure API token and endpoint"
    echo "  crackit start   - Start screen capture service"
    echo "  crackit stop    - Stop the service"
    echo "  crackit status  - Check if service is running"
    echo "  crackit logs    - View recent logs"
    echo ""
}

# Run installation
check_dependencies
install_crackit
