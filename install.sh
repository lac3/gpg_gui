#!/bin/bash
echo "Installing GPG GUI..."

# Check if GPG is installed
if ! command -v gpg &> /dev/null; then
    echo "GPG not found. Please install GPG first:"
    echo "  macOS: brew install gnupg"
    echo "  Ubuntu/Debian: sudo apt-get install gnupg"
    echo "  CentOS/RHEL: sudo yum install gnupg"
    exit 1
fi

# Copy executable to /usr/local/bin (or appropriate location)
if [ "$(id -u)" -eq 0 ]; then
    cp GpgGui /usr/local/bin/
    chmod +x /usr/local/bin/GpgGui
    echo "GPG GUI installed to /usr/local/bin/GpgGui"
else
    echo "Please run this script with sudo to install system-wide"
    echo "Or copy GpgGui to a directory in your PATH"
fi
