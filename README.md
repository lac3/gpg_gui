# GPG GUI

A user-friendly graphical interface for GPG file encryption and decryption on macOS. This application provides an intuitive way to encrypt, decrypt, and manage GPG files and keys without using command-line tools.

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
- **Key Deletion**: Remove unwanted keys from your keyring

### User Experience
- **Dual Encryption Modes**: Use either passphrases or GPG keys for encryption
- **Password Visibility Toggle**: Show/hide passphrases during entry
- **File Browser Integration**: Native file dialogs for selecting files
- **Last Directory Memory**: Remembers your last used directory
- **Automatic GPG Installation**: Installs GPG via Homebrew if not present

## Installation

### Prerequisites
- macOS (tested on macOS 10.13+)
- Python 3.9+ (Python 3.13 recommended)
- Homebrew (will be installed automatically if missing)

### Quick Start
1. Clone or download this repository
2. Run the setup script:
   ```bash
   ./run_gpg_gui.command
   ```
   This script will:
   - Install Homebrew if needed
   - Install GPG if needed
   - Set up Python virtual environment
   - Launch the application

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
   - Save both files to a cloud folder (iCloud, Google Drive, etc.)
3. Open GPG Decrypt on iOS and import both files


## Building Standalone App

To create a standalone macOS application, one option is to use Automator

## File Structure

```
gpg_gui/
├── gpg_gui.py              # Main GUI application
├── gpg_process.py          # GPG operations wrapper
├── install_gpg.py          # GPG installation helper
├── setup.py                # py2app build configuration
├── run_gpg_gui.command     # Launch script
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
├── GpgGui.png             # Application icon (PNG)
├── GpgGui.icns            # Application icon (macOS)
└── README.md              # This file
```

## Technical Details

- **GUI Framework**: Tkinter (built into Python)
- **GPG Backend**: System GPG via subprocess calls
- **File Handling**: Temporary files for secure processing
- **Backup System**: Automatic timestamped backups with cleanup
- **Configuration**: Stores last directory in `~/.gpg_gui_config`

## Security Notes

- Passphrases are handled securely through GPG's built-in mechanisms
- Temporary files are automatically cleaned up after operations
- GPG agent is reloaded before sensitive operations
- All GPG operations use batch mode with proper error handling

## Troubleshooting

### Common Issues
- **"GPG not found"**: Run `./run_gpg_gui.command` to auto-install
- **"Python not found"**: Install Python from [python.org](https://python.org)
- **Key creation fails**: Ensure you have sufficient entropy (move mouse/type)
- **Decryption fails**: Verify passphrase and file integrity

### Debug Mode
Run with debug output:
```bash
python3 gpg_gui.py 2>&1 | tee debug.log
```

## Version

Current version: 2.0

## License

This project is open source. See individual file headers for specific licensing information.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.
