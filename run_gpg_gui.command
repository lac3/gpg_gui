#!/bin/bash

# Change to script directory
cd "$(dirname "$0")"

# Function to check and install Homebrew
check_homebrew() {
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        # Add Homebrew to PATH for current session
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    echo "Homebrew found"
}

# Function to find Python
find_python() {
    # Check for python3 first
    if command -v python3 &> /dev/null; then
        echo "python3"
        return 0
    fi
    # Check for python
    if command -v python &> /dev/null; then
        echo "python"
        return 0
    fi
    return 1
}

# Check and install Homebrew
check_homebrew

# Find Python executable
PYTHON_CMD=$(find_python)
if [ $? -ne 0 ]; then
    echo "Python not found. Please instal from python.org"
    exit 0
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    # Keep using python3 even in venv for macOS compatibility
    PYTHON_CMD="python3"
fi

# Check if GPG is available
if ! command -v gpg &> /dev/null; then
    echo "GPG not found. Installing using Homebrew..."
    brew install gnupg
    if [ $? -ne 0 ]; then
        echo "Failed to install GPG. Please install it manually:"
        echo "  brew install gnupg"
        exit 1
    fi
fi

# Run the GPG GUI
echo "Starting GPG GUI..."
$PYTHON_CMD gpg_gui.py 