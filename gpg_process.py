import os
import shutil
import subprocess
import tempfile

from install_gpg import install_gpg


class GpgProcess:
    def __init__(self, file_path=None, passphrase=None):
        self.file_path = file_path
        self.passphrase = passphrase
        self.gpg_path = shutil.which("gpg")
        self.list_secret_keys()
        self.selected_key = None

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

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # Encrypt the temporary file
            subprocess.run(
                [
                    self.gpg_path,
                    "--batch",
                    "--symmetric",
                    "--passphrase",
                    self.passphrase,
                    "--output",
                    self.file_path,
                    temp_path,
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            raise ValueError("encrypt: Failed to encrypt file")
        except Exception as e:
            raise ValueError(f"encrypt: Unexpected error: {str(e)}")
        finally:
            os.unlink(temp_path)

    def encrypt_with_key(self, content: str) -> None:
        if not self.file_path:
            raise ValueError("encrypt_with_key: File path is required")
        if not self.selected_key:
            raise ValueError("encrypt_with_key: No key selected")

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            subprocess.run("echo reloadagent | gpg-connect-agent", shell=True, check=True)
            # Encrypt the temporary file using the selected key
            subprocess.run(
                [
                    self.gpg_path,
                    "--batch",
                    "--yes",
                    "--recipient",
                    self.selected_key[0],  # Use fingerprint as recipient
                    "--output",
                    self.file_path,
                    "--encrypt",
                    temp_path,
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            raise ValueError("encrypt_with_key: Failed to encrypt file")
        except Exception as e:
            raise ValueError(f"encrypt_with_key: Unexpected error: {str(e)}")
        finally:
            os.unlink(temp_path)

    def decrypt(self) -> str:
        if not self.file_path:
            raise ValueError("decrypt: File path is required")
        if not self.passphrase:
            raise ValueError("decrypt: Passphrase is required")

        # Create a temporary file for decryption
        # "Named" option because GPG needs a file to write to
        with tempfile.NamedTemporaryFile(mode="w+b", delete=False) as temp_file:
            temp_path = temp_file.name
        # Clear GPG agent cache to force passphrase prompt
        try:
            subprocess.run("echo reloadagent | gpg-connect-agent", shell=True, check=True)
            # Decrypt to temporary file
            subprocess.run(
                [
                    self.gpg_path,
                    "--batch",
                    "--yes",
                    "--pinentry-mode=loopback",  # Add this
                    "--decrypt",
                    "--passphrase",
                    self.passphrase,
                    "--output",
                    temp_path,
                    self.file_path,
                ],
                check=True,
            )
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
        except subprocess.CalledProcessError:
            raise ValueError("Failed to decrypt file (wrong passphrase?)")
        except Exception as e:
            raise ValueError(f"decrypt: Unexpected error: {str(e)}")
        finally:
            os.unlink(temp_path)

        return content

    def list_secret_keys(self) -> None:
        self.secret_keys = []
        if not self.gpg_path:
            raise ValueError("list_secret_keys: GPG path is required")

        try:
            result = subprocess.run(
                [
                    self.gpg_path,
                    "--list-secret-keys",
                    "--with-colons",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise ValueError(f"list_secret_keys: Failed to list secret keys: {result.stderr}")

            # Parse the output
            keys: list[tuple[str, str]] = []
            lines = result.stdout.splitlines()
            l_ind = 0
            new_key = False
            while l_ind < len(lines):
                line = lines[l_ind]
                if line.startswith("sec"):
                    new_key = True
                    fingerprint = ""
                    email = ""
                elif line.startswith("fpr") and new_key:
                    fingerprint = line.split(":")[9]
                elif line.startswith("uid") and new_key:
                    email = line.split(":")[9]
                elif line.startswith("ssb"):
                    new_key = False

                if fingerprint and email and new_key:
                    keys.append((fingerprint, email))
                l_ind += 1
            self.secret_keys = keys

        except subprocess.CalledProcessError:
            raise ValueError("list_secret_keys: Failed to list secret keys")
        except Exception as e:
            raise ValueError(f"list_secret_keys: Unexpected error: {str(e)}")

    def delete_key(self, fingerprint: str):
        try:
            # Delete the secret key first, then the public key (order is mandatory)
            subprocess.run(
                [self.gpg_path, "--batch", "--yes", "--delete-secret-key", fingerprint],
                check=True,
            )
            subprocess.run(
                [self.gpg_path, "--batch", "--yes", "--delete-keys", fingerprint],
                check=True,
            )
            # Refresh the key list
            self.list_secret_keys()
        except subprocess.CalledProcessError:
            raise ValueError("delete_key: Failed to delete key")
        except Exception as e:
            raise ValueError(f"delete_key: Unexpected error: {str(e)}")

    def create_key(self, email: str, name: str, passphrase: str):
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
                temp_path = temp_file.name
                temp_file.write(
                    f"""%echo Generate RSA + RSA key
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Key-Usage: cert sign
Subkey-Usage: encrypt auth
Name-Real: {name}
Name-Email: {email}
Expire-Date: 0
Passphrase: {passphrase}
%commit
%echo Done
"""
                )
                temp_file.close()

            subprocess.run([
                self.gpg_path,
                "--default-preference-list", "AES256 AES192 AES CAST5 SHA512 SHA256 SHA1 ZLIB BZIP2 ZIP Uncompressed",
                "--batch",
                "--gen-key",
                temp_path
            ], check=True)
            os.unlink(temp_path)
            # Refresh the key list
            print("created key")
            self.list_secret_keys()
            # Find the key with matching name and email
            for fingerprint, key_email in self.secret_keys:
                if key_email == f"{name} <{email}>":
                    print(f"Setting trust and preferences for key {fingerprint} {key_email}")
                    self.set_key_trust_and_prefs(fingerprint)
                    break
        except subprocess.CalledProcessError:
            raise ValueError("gpg failed to create key")
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")

    def import_key(self, key_file: str, passphrase: str):
        try:
            cmd = [
                self.gpg_path,
                "--pinentry-mode=loopback",
                "--passphrase",
                passphrase,
                "--import",
                key_file,
            ]
            subprocess.run(cmd, check=True)
            self.list_secret_keys()
        except subprocess.CalledProcessError:
            raise ValueError("gpg failed to import key")
        except Exception as e:
            raise ValueError(f"unexpected gpg error: {str(e)}")

    def export_key(self, fingerprint: str, output_file: str, passphrase: str):
        try:
            with open(output_file, "w") as f:
                cmd = [
                    self.gpg_path,
                    "--armor",
                    "--export-secret-keys",
                    "--pinentry-mode=loopback",
                    "--passphrase",
                    passphrase,
                    fingerprint,
                ]
                subprocess.run(cmd, check=True, stdout=f)
        except subprocess.CalledProcessError:
            raise ValueError("export_key: Failed to export key")
        except Exception as e:
            raise ValueError(f"export_key: Unexpected error: {str(e)}")

    def set_key_trust_and_prefs(self, fingerprint: str):
        try:
            commands = (
                "trust\n"
                "5\n"
                "setpref AES256 AES192 AES128 3DES SHA512 SHA384 SHA256 SHA224 SHA1 ZLIB BZIP2 ZIP\n"
                "save\n"
            )
            subprocess.run(
                [
                    self.gpg_path,
                    "--batch",
                    "--command-fd",
                    "0",
                    "--edit-key",
                    fingerprint,
                ],
                input=commands,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            raise ValueError("Failed to set trust and preferences for key")
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    gpg = GpgProcess()
    gpg.list_secret_keys()
    print(gpg.secret_keys)
