#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Set PATH to include Homebrew locations (needed for Automator)
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

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
    # Try Homebrew Python locations first (more reliable)
    for python_path in "/opt/homebrew/bin/python3" "/usr/local/bin/python3"; do
        if [ -x "$python_path" ]; then
            echo "$python_path"
            return 0
        fi
    done
    
    # Try command line python3
    if command -v python3 &> /dev/null; then
        echo "python3"
        return 0
    fi
    
    # Last resort: system Python (may have version issues)
    if [ -x "/usr/bin/python3" ]; then
        echo "/usr/bin/python3"
        return 0
    fi
    
    return 1
}

# Check and install Homebrew
check_homebrew

# Find Python executable
PYTHON_CMD=$(find_python)
if [ $? -ne 0 ]; then
    echo "Python not found. Please install it from python.org"
    exit 0
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Check if tkinter is available, install if needed (only when interactive)
if ! $PYTHON_CMD -c "import tkinter" &> /dev/null; then
    echo "tkinter not available. Attempting to install python-tk..."
    if [ -t 0 ]; then
        # Running interactively (Terminal), can install
        brew install python-tk || echo "Warning: Could not install python-tk"
    else
        echo "Error: tkinter not available and running non-interactively."
        echo "Please run this script from Terminal first: ./run_gpg_gui.command"
        exit 1
    fi
fi

# Add venv packages to PYTHONPATH if venv exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "Adding virtual environment packages to PYTHONPATH..."
    # Get Python version to construct site-packages path
    PY_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    export PYTHONPATH="$SCRIPT_DIR/venv/lib/python${PY_VERSION}/site-packages:$PYTHONPATH"
fi

# Check if GPG is available (but don't try to install from Automator)
if ! command -v gpg &> /dev/null; then
    echo "Error: GPG not found in PATH."
    echo "Please run this script from Terminal first to set up dependencies."
    exit 1
fi

# Run the GPG GUI
echo "Starting GPG GUI..."
$PYTHON_CMD "$SCRIPT_DIR/gpg_gui.py" 