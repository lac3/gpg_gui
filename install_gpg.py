import os
import subprocess
import sys
import platform

def install_gpg():
    system = platform.system().lower()
    
    print(f"Detected system: {system}")
    
    if system == "darwin":  # macOS
        print("Installing GPG using Homebrew...")
        try:
            # Check if Homebrew is installed
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Homebrew not found. Installing Homebrew first...")
            install_homebrew()
        
        # Install GPG
        subprocess.run(["brew", "install", "gnupg"])
        
    elif system == "linux":
        print("Installing GPG using package manager...")
        # Try different package managers
        package_managers = [
            ["apt-get", "update", "&&", "apt-get", "install", "-y", "gnupg"],
            ["yum", "install", "-y", "gnupg"],
            ["dnf", "install", "-y", "gnupg"],
            ["pacman", "-S", "--noconfirm", "gnupg"]
        ]
        
        for manager in package_managers:
            try:
                subprocess.run(manager, check=True)
                print(f"GPG installed successfully using {manager[0]}")
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        else:
            print("Could not install GPG automatically. Please install it manually.")
            
    elif system == "windows":
        print("For Windows, please install GPG4Win manually from: https://www.gpg4win.org/")
        print("After installation, make sure 'gpg' is available in your PATH")
        
    else:
        print(f"Unsupported system: {system}")
        return False
    
    # Verify installation
    try:
        result = subprocess.run(["gpg", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("GPG installation verified successfully!")
            return True
    except FileNotFoundError:
        print("GPG not found in PATH after installation")
        return False

def install_homebrew():
    """Install Homebrew on macOS"""
    install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    subprocess.run(install_script, shell=True)

if __name__ == "__main__":
    install_gpg() 