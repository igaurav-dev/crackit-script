# Crackit Installer for Windows
# Usage: irm https://raw.githubusercontent.com/igaurav-dev/crackit-script/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    CRACKIT INSTALLER                       ║" -ForegroundColor Cyan
Write-Host "║           Screen Capture & AI Exam Assistant               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Configuration
$InstallDir = "$env:USERPROFILE\.crackit"
$RepoUrl = "https://github.com/igaurav-dev/crackit-script.git"

# Check Python
Write-Host "Checking dependencies..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is required but not installed." -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    exit 1
}

# Check pip
try {
    pip --version | Out-Null
    Write-Host "✓ pip found" -ForegroundColor Green
} catch {
    Write-Host "❌ pip is required but not installed." -ForegroundColor Red
    exit 1
}

# Check git
try {
    git --version | Out-Null
    Write-Host "✓ git found" -ForegroundColor Green
} catch {
    Write-Host "❌ git is required but not installed." -ForegroundColor Red
    Write-Host "   Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Check Tesseract
try {
    tesseract --version | Out-Null
    Write-Host "✓ tesseract found" -ForegroundColor Green
} catch {
    Write-Host "⚠ Tesseract OCR not found." -ForegroundColor Yellow
    
    # Try Winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Attempting to install via Winget..." -ForegroundColor Yellow
        try {
            winget install -e --id UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements
            
            # Refresh PATH for current session
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            if (Get-Command tesseract -ErrorAction SilentlyContinue) {
                 Write-Host "✓ Tesseract installed successfully" -ForegroundColor Green
            } else {
                 Write-Host "⚠ Tesseract installed but may need restart." -ForegroundColor Yellow
                 Write-Host "   Default path: C:\Program Files\Tesseract-OCR\tesseract.exe" -ForegroundColor Gray
            }
        } catch {
            Write-Host "❌ Winget install failed." -ForegroundColor Red
            Write-Host "   Please install manually from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Winget not found." -ForegroundColor Red
        Write-Host "   Please install Tesseract manually from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Installing Crackit to $InstallDir..." -ForegroundColor Yellow

# Remove existing installation
if (Test-Path $InstallDir) {
    Write-Host "Removing existing installation..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $InstallDir
}

# Clone repository
git clone --depth 1 $RepoUrl $InstallDir

# Change to install directory
Set-Location $InstallDir

# Create virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate and install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& "$InstallDir\venv\Scripts\pip.exe" install --upgrade pip
& "$InstallDir\venv\Scripts\pip.exe" install -r requirements.txt

# Create launcher batch file
$launcherContent = @"
@echo off
call "%USERPROFILE%\.crackit\venv\Scripts\activate.bat"
python "%USERPROFILE%\.crackit\sync_service.py" %*
"@
Set-Content -Path "$InstallDir\crackit.cmd" -Value $launcherContent

# Add to PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$InstallDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$InstallDir", "User")
    Write-Host "✓ Added crackit to PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              INSTALLATION COMPLETE! 🎉                     ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. RESTART your terminal (or open a new one)" -ForegroundColor White
Write-Host ""
Write-Host "  2. Configure your token:" -ForegroundColor White
Write-Host "     crackit setup" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. Start the service:" -ForegroundColor White
Write-Host "     crackit start -f" -ForegroundColor Yellow
Write-Host ""
Write-Host "Commands:" -ForegroundColor Cyan
Write-Host "  crackit setup     - Configure API token and endpoint"
Write-Host "  crackit start -f  - Start screen capture (foreground on Windows)"
Write-Host "  crackit stop      - Stop the service"
Write-Host "  crackit status    - Check if service is running"
Write-Host "  crackit logs      - View recent logs"
Write-Host "  crackit uninstall - Remove Crackit completely"
Write-Host ""
