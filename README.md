# GPG GUI

A user-friendly graphical interface for GPG file encryption and decryption on MacOS, with default options. This application provides an intuitive way to encrypt, decrypt, and manage GPG files and key pairs without using command-line tools.

## Features

### Core Functionality
- **File Encryption**: Create and encrypt text files with password or GPG keys
- **File Decryption**: Decrypt and view GPG-encrypted files
- **Content Editor**: Built-in text editor for creating and modifying encrypted content
- **Automatic Backup**: Creates timestamped backups when overwriting existing files

### GPG Key Management
- **Key Creation**: Generate new GPG key pairs with custom names and emails
- **Key Import/Export**: Import existing keys or export keys to share
- **Key Selection**: Choose which key to use for encryption
- **Key Deletion**: Remove unwanted keys 

### Quick Start
1. Clone or download this repository
2. Run the setup script:
   ```bash
   ./run_gpg_gui.command
   ```
To create a standalone macOS application, one good option is to use Automator

## Usage

### Using Keys (Asymmetric Encryption)
- Click "Use Key for Encryption" if you want to use asymmetric encryption with a public key
- You'll need to select a key and possibly manage keys using the delete/create buttons
- You can import or export keys as needed

### Creating and Encrypting Files
1. Launch the application
2. Click "Create & Encrypt"
3. Enter your content in the text editor
4. Click "Save & Encrypt" and choose where to save the .gpg file

### Decrypting Files
1. Click "Decrypt & View"
2. Select a .gpg file to decrypt
3. Enter the passphrase or key password, depending on option "Use Key for Encryption"
4. View and optionally modify the decrypted content
5. Save changes if needed (automatically creates backup of original)

### Managing GPG Keys
1. Check "Use Key for Encryption"
2. Click "Manage Keys" to:
   - **Create**: Generate new key pairs
   - **Import**: Add existing keys from .asc files
   - **Export**: Save keys to share with others
   - **Delete**: Remove unwanted keys
   - **Select**: Choose which key to use for encryption

### Decrypting on iOS
Files encrypted with this app can be decrypted on iOS using [GPG Decrypt](https://apps.apple.com/us/app/gpg-decrypt/id6744686392). To ensure compatibility:

1. Enable "Use Key for Encryption" when encrypting
2. Export both the encrypted file and your key:
   - Export your key using "Manage Keys" > "Export"
   - Save both files to a cloud folder (iCloud, Google Drive, DropBox...)
3. Open GPG Decrypt on iOS and import both files, type passphrase and depcrypt


