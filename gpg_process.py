import shutil
import subprocess
from install_gpg import install_gpg
import tempfile
import os

class GpgProcess:
    def __init__(self, file_path=None, passphrase=None):
        self.file_path = file_path
        self.passphrase = passphrase

        self.gpg_path = shutil.which("gpg")
        if not self.gpg_path:
            if install_gpg():
                self.gpg_path = shutil.which("gpg")
            if not self.gpg_path:
                raise FileNotFoundError("GPG installation failed")
    
    def encrypt(self, content: str) -> None:
        if not self.file_path:
            raise ValueError("encrypt: File path is required")
        if not self.passphrase:
            raise ValueError("encrypt: Passphrase is required")

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Encrypt the temporary file
            subprocess.run([
                self.gpg_path,
                "--batch",
                "--symmetric",
                "--passphrase", self.passphrase,
                "--output", self.file_path,
                temp_path
            ], check=True)
        except subprocess.CalledProcessError:
            raise ValueError("encrypt: Failed to encrypt file")
        except Exception as e:
            raise ValueError(f"encrypt: Unexpected error: {str(e)}")
        finally:
            os.unlink(temp_path)

    def decrypt(self) -> str:
        if not self.file_path:
            raise ValueError("decrypt: File path is required")
        if not self.passphrase:
            raise ValueError("decrypt: Passphrase is required")

        # Create a temporary file for decryption ("Named" option because GPG needs a file to write to
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Decrypt to temporary file
            subprocess.run([
                self.gpg_path,
                "--batch",
                "--yes",
                "--decrypt",
                "--passphrase", self.passphrase,
                "--output", temp_path,
                self.file_path
            ], check=True)
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except subprocess.CalledProcessError:
            raise ValueError("decrypt: Failed to decrypt file")
        except Exception as e:
            raise ValueError(f"decrypt: Unexpected error: {str(e)}")
        finally:
            os.unlink(temp_path)
       
        return content
    