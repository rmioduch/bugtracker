@echo off
REM TaskMaster BugTracker - Build Script for Windows
REM This script automates the build process

echo ========================================
echo TaskMaster BugTracker - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller==6.3.0

REM Create assets directory if it doesn't exist
if not exist "assets" (
    echo Creating assets directory...
    mkdir assets
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del *.spec

REM Build the executable
echo.
echo Building TaskMaster BugTracker.exe...
echo This may take a few minutes...
echo.

REM Choose build method
if exist "assets\icon.ico" (
    echo Found icon.ico, building with icon...
    pyinstaller --onefile --windowed --icon=assets\icon.ico --name="TaskMaster BugTracker" main.py
) else (
    echo No icon found, building without icon...
    pyinstaller --onefile --windowed --name="TaskMaster BugTracker" main.py
)

REM Check if build was successful
if exist "dist\TaskMaster BugTracker.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable location: dist\TaskMaster BugTracker.exe
    echo Size:
    dir "dist\TaskMaster BugTracker.exe" | find "TaskMaster"
    echo.

    REM Ask if user wants to copy to desktop
    set /p copyToDesktop="Copy to Desktop? (Y/N): "
    if /i "%copyToDesktop%"=="Y" (
        echo Copying to Desktop...
        copy "dist\TaskMaster BugTracker.exe" "%USERPROFILE%\Desktop\"
        echo Done! Check your Desktop.
    )

    REM Ask if user wants to run the app
    echo.
    set /p runApp="Run TaskMaster BugTracker now? (Y/N): "
    if /i "%runApp%"=="Y" (
        start "" "dist\TaskMaster BugTracker.exe"
    )
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo.
    echo Check the error messages above.
    echo Common issues:
    echo - Missing modules
    echo - Antivirus interference
    echo - Path too long
)

echo.
echo Press any key to exit...
pause >nul