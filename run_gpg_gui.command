#!/bin/bash
# Development launcher: runs GPG GUI from this source folder.
# Prerequisites: Homebrew, then `brew install gnupg python-tk@3.13`.
# End users should install with: brew install lac3/tap/gpg-gui

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Apps launched from Finder/Automator don't inherit the shell PATH
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

if ! command -v brew &> /dev/null; then
    echo "Homebrew is required: https://brew.sh"
    exit 1
fi

PYTHON_CMD="$(brew --prefix)/bin/python3.13"
if [ ! -x "$PYTHON_CMD" ] || ! "$PYTHON_CMD" -c "import tkinter" &> /dev/null; then
    echo "Python 3.13 with Tk is required: brew install python-tk@3.13"
    exit 1
fi

if ! command -v gpg &> /dev/null; then
    echo "GnuPG is required: brew install gnupg"
    exit 1
fi

exec "$PYTHON_CMD" "$SCRIPT_DIR/gpg_gui.py"
