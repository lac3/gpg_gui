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
    # Try Homebrew Python locations first (check versioned names too)
    for python_path in "/opt/homebrew/bin/python3.13" "/usr/local/bin/python3.13" "/opt/homebrew/bin/python3" "/usr/local/bin/python3"; do
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

echo "========== Python Diagnostics =========="
echo "Python executable: $PYTHON_CMD"
echo "Python version: $($PYTHON_CMD --version)"
echo "Python location: $($PYTHON_CMD -c 'import sys; print(sys.executable)')"
echo "Python version info: $($PYTHON_CMD -c 'import sys; print(sys.version_info[:3])')"
echo ""
echo "Available Python installations:"
if [ -x "/opt/homebrew/bin/python3.13" ]; then
    echo "  Homebrew (Apple Silicon): $(/opt/homebrew/bin/python3.13 --version 2>&1)"
elif [ -x "/opt/homebrew/bin/python3" ]; then
    echo "  Homebrew (Apple Silicon): $(/opt/homebrew/bin/python3 --version 2>&1)"
else
    echo "  Homebrew (Apple Silicon): Not found"
fi
if [ -x "/usr/local/bin/python3.13" ]; then
    echo "  Homebrew (Intel): $(/usr/local/bin/python3.13 --version 2>&1)"
elif [ -x "/usr/local/bin/python3" ]; then
    echo "  Homebrew (Intel): $(/usr/local/bin/python3 --version 2>&1)"
else
    echo "  Homebrew (Intel): Not found"
fi
[ -x "/usr/bin/python3" ] && echo "  System: $(/usr/bin/python3 --version 2>&1)" || echo "  System: Not found"
echo "========================================"

# Check Python source and version
PY_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
PY_REAL_PATH=$($PYTHON_CMD -c 'import sys; print(sys.executable)')

echo ""
echo "Python source analysis:"
NEEDS_HOMEBREW_PYTHON=false
if [[ "$PY_REAL_PATH" == /opt/homebrew/* ]] || [[ "$PY_REAL_PATH" == /usr/local/* ]]; then
    echo "✓ Using Homebrew Python (preferred)"
elif [[ "$PY_REAL_PATH" == /Library/Developer/CommandLineTools/* ]]; then
    echo "⚠ Using Xcode Command Line Tools Python (not recommended)"
    echo "This Python often lacks proper package support."
    NEEDS_HOMEBREW_PYTHON=true
elif [[ "$PY_REAL_PATH" == /usr/bin/* ]]; then
    echo "⚠ Using system Python (not recommended)"
    NEEDS_HOMEBREW_PYTHON=true
else
    echo "? Using Python from: $PY_REAL_PATH"
fi
echo ""

# Install Homebrew Python if needed
if [ "$NEEDS_HOMEBREW_PYTHON" = true ] || [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]; }; then
    if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]; }; then
        echo "WARNING: Python $PY_MAJOR.$PY_MINOR is too old. Python 3.8+ recommended."
    fi
    
    echo "Installing Homebrew Python..."
    
    if brew install python@3.13; then
        echo "✓ Python installation successful!"
        # Update PATH to include newly installed Python
        eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null)"
        
        # Force use of Homebrew Python (check versioned names too)
        echo "Checking for Homebrew Python..."
        if [ -x "/opt/homebrew/bin/python3.13" ]; then
            PYTHON_CMD="/opt/homebrew/bin/python3.13"
            echo "Found at: /opt/homebrew/bin/python3.13"
        elif [ -x "/usr/local/bin/python3.13" ]; then
            PYTHON_CMD="/usr/local/bin/python3.13"
            echo "Found at: /usr/local/bin/python3.13"
        elif [ -x "/opt/homebrew/bin/python3" ]; then
            PYTHON_CMD="/opt/homebrew/bin/python3"
            echo "Found at: /opt/homebrew/bin/python3"
        elif [ -x "/usr/local/bin/python3" ]; then
            PYTHON_CMD="/usr/local/bin/python3"
            echo "Found at: /usr/local/bin/python3"
        else
            echo "Not found in Homebrew paths, using fallback"
            # Fallback to find_python
            PYTHON_CMD=$(find_python)
        fi
        
        if [ -n "$PYTHON_CMD" ]; then
            PY_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
            PY_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
            echo "Now using: $($PYTHON_CMD --version) from $($PYTHON_CMD -c 'import sys; print(sys.executable)')"
        else
            echo "ERROR: Failed to locate newly installed Python"
        fi
    else
        echo "ERROR: Failed to install Python via Homebrew"
        echo "Please install manually with: brew install python@3.13"
    fi
    echo ""
fi

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