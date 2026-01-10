@echo off
REM Setup script for Sync Service (Windows)
REM Checks Python, installs dependencies

echo.
echo ============================
echo   Sync Service Setup
echo ============================
echo.

REM Check Python
echo Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python not found!
        echo.
        echo Please install Python 3.9+ from:
        echo   https://python.org/downloads
        echo.
        echo Make sure to check "Add Python to PATH" during install.
        pause
        exit /b 1
    ) else (
        set PYTHON=python3
    )
) else (
    set PYTHON=python
)

%PYTHON% --version
echo [OK] Python found

REM Check pip
echo.
echo Checking pip...
%PYTHON% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found!
    echo Please reinstall Python with pip included.
    pause
    exit /b 1
)
echo [OK] pip available

REM Install dependencies
echo.
echo Installing dependencies...
%PYTHON% -m pip install --user -q -r requirements.txt

if %errorlevel% equ 0 (
    echo [OK] Dependencies installed
) else (
    echo [WARNING] Some dependencies may have failed
)

echo.
echo ============================
echo   Setup complete!
echo ============================
echo.
echo Usage:
echo   %PYTHON% sync_service.py setup    # Configure
echo   %PYTHON% sync_service.py start -f # Start (foreground)
echo   %PYTHON% sync_service.py stop     # Stop
echo   %PYTHON% sync_service.py status   # Check status
echo.
echo For background: use Task Scheduler with pythonw.exe
echo.
pause
