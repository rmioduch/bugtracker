#!/bin/bash
# TaskMaster BugTracker - Build Script for Linux/macOS
# This script automates the build process

echo "========================================"
echo "TaskMaster BugTracker - Build Script"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "Python version:"
python3 --version
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created.${NC}"
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install PyInstaller
echo "Installing PyInstaller..."
pip install pyinstaller==6.3.0

# Create assets directory if it doesn't exist
if [ ! -d "assets" ]; then
    echo "Creating assets directory..."
    mkdir -p assets
fi

# Clean previous builds
echo
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Build the executable
echo
echo "Building TaskMaster BugTracker..."
echo "This may take a few minutes..."
echo

# Determine platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    APP_NAME="TaskMaster BugTracker.app"
    if [ -f "assets/icon.icns" ]; then
        echo "Found icon.icns, building with icon..."
        pyinstaller --onefile --windowed --icon=assets/icon.icns --name="TaskMaster BugTracker" main.py
    else
        echo "No icon found, building without icon..."
        pyinstaller --onefile --windowed --name="TaskMaster BugTracker" main.py
    fi
else
    # Linux
    APP_NAME="TaskMaster BugTracker"
    if [ -f "assets/icon.png" ]; then
        echo "Found icon.png, building with icon..."
        pyinstaller --onefile --windowed --icon=assets/icon.png --name="TaskMaster BugTracker" main.py
    else
        echo "No icon found, building without icon..."
        pyinstaller --onefile --windowed --name="TaskMaster BugTracker" main.py
    fi
fi

# Check if build was successful
if [ -f "dist/$APP_NAME" ] || [ -d "dist/$APP_NAME" ]; then
    echo
    echo -e "${GREEN}========================================"
    echo "BUILD SUCCESSFUL!"
    echo "========================================${NC}"
    echo
    echo "Executable location: dist/$APP_NAME"
    ls -lh "dist/$APP_NAME"
    echo

    # Ask if user wants to copy to Desktop
    read -p "Copy to Desktop? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            cp -r "dist/$APP_NAME" ~/Desktop/
        else
            # Linux
            cp "dist/$APP_NAME" ~/Desktop/
        fi
        echo -e "${GREEN}Done! Check your Desktop.${NC}"
    fi

    # Ask if user wants to run the app
    echo
    read -p "Run TaskMaster BugTracker now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "dist/$APP_NAME"
        else
            "dist/$APP_NAME" &
        fi
    fi
else
    echo
    echo -e "${RED}========================================"
    echo "BUILD FAILED!"
    echo "========================================${NC}"
    echo
    echo "Check the error messages above."
    echo "Common issues:"
    echo "- Missing modules"
    echo "- Permission denied"
    echo "- Missing dependencies"
fi

echo
echo "Press Enter to exit..."
read