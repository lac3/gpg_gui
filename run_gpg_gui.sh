#!/bin/bash

# Change to script directory
cd "$(dirname "$0")"

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

# Find Python executable
PYTHON_CMD=$(find_python)
if [ $? -ne 0 ]; then
    echo "Python not found. Please install Python 3.7+ first:"
    echo "  Visit: https://www.python.org/downloads/"
    echo "  Or use Homebrew: brew install python"
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    PYTHON_CMD="python"  # Use 'python' when venv is active
fi

# Check if GPG is available
if ! command -v gpg &> /dev/null; then
    echo "GPG not found. Attempting to install..."
    $PYTHON_CMD install_gpg.py
    if [ $? -ne 0 ]; then
        echo "Failed to install GPG. Please install it manually:"
        echo "  brew install gnupg"
        exit 1
    fi
fi

# Run the GPG GUI
echo "Starting GPG GUI..."
$PYTHON_CMD gpg_gui.py 