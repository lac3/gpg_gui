import os
import subprocess
import sys
import platform

def install_gpg():
    """Install GPG on macOS using Homebrew"""
    system = platform.system().lower()
    
    if system != "darwin":  # macOS only
        print(f"Unsupported system: {system}. This installer is for macOS only.")
        return False
    
    print("Installing GPG on macOS...")
    
    # Check if Homebrew is available
    try:
        subprocess.run(["brew", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Homebrew not found. Please run run_gpg_gui.command first to install dependencies.")
        return False
    
    # Install GPG
    try:
        subprocess.run(["brew", "install", "gnupg"], check=True)
        print("GPG installed successfully!")
        
        # Verify installation
        result = subprocess.run(["gpg", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("GPG installation verified successfully!")
            return True
        else:
            print("GPG installation verification failed")
            return False
    except subprocess.CalledProcessError:
        print("Failed to install GPG using Homebrew")
        return False

if __name__ == "__main__":
    install_gpg() 