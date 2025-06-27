import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import tempfile
from install_gpg import install_gpg

VERSION = "2.0"

class GPGGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GPG File Encryption/Decryption")
        self.root.geometry("500x300")
        
        # Center the window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
        
        # Bring window to front and give it focus
        self.root.lift()
        self.root.focus_force()
        
        # Find GPG executable
        self.gpg_path = self.find_gpg()
        if not self.gpg_path:
            if install_gpg():
                # Re-check for GPG after installation
                self.gpg_path = self.find_gpg()
            if not self.gpg_path:
                messagebox.showerror("Error", "GPG installation failed")
                return
        
        # Create main frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title_label = tk.Label(main_frame, text="Choose an action:", font=("Arial", 14))
        title_label.pack(pady=20)
        
        # Action buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Create & Encrypt", command=self.create_and_encrypt, width=15, height=2).pack(side='left', padx=10)
        tk.Button(button_frame, text="Decrypt & View", command=lambda: self.decrypt(), width=15, height=2).pack(side='left', padx=10)
        
        # Close button
        close_button = tk.Button(main_frame, text="Close", command=root.destroy, width=10)
        close_button.pack(pady=10)
        
    def find_gpg(self):
        """Find the GPG executable path"""
        # Common GPG paths
        possible_paths = [
            "/opt/homebrew/bin/gpg",  # Homebrew on Apple Silicon
            "/usr/local/bin/gpg",     # Homebrew on Intel
            "/usr/bin/gpg",           # System GPG
            "/opt/local/bin/gpg",     # MacPorts
        ]
        
        # Check if GPG is in PATH
        try:
            result = subprocess.run(["which", "gpg"], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass
        
        # Check common paths
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
        
    def show_about(self):
        """Show custom About dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About GPG GUI")
        about_window.geometry("400x350")
        about_window.resizable(False, False)
        
        # Center the window
        about_window.transient(self.root)
        about_window.grab_set()
        
        # About content
        content_frame = tk.Frame(about_window, padx=20, pady=20)
        content_frame.pack(expand=True, fill='both')
        
        # App name and version
        tk.Label(content_frame, text="GPG GUI", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Label(content_frame, text="Version " + VERSION, font=("Arial", 12)).pack()
        
        # Description
        tk.Label(content_frame, text="A secure graphical interface for GPG file encryption and decryption.", 
                wraplength=350, justify='center').pack(pady=15)
        
        # Copyright
        tk.Label(content_frame, text="© 2024 Laurent Ach. All rights reserved.", 
                font=("Arial", 10)).pack(pady=10)
        
        # Features
        features_text = """Features:
• Encrypt files to disk
• Decrypt and view content in memory
• Create and encrypt new content
• No decrypted files saved to disk
• Secure passphrase input
• Cross-platform support"""
        
        tk.Label(content_frame, text=features_text, justify='left', 
                font=("Arial", 10)).pack(pady=10)
        
        # Close button
        tk.Button(content_frame, text="OK", command=about_window.destroy, width=10).pack(pady=10)
        
        # Center the window
        about_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - about_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - about_window.winfo_height()) // 2
        about_window.geometry(f"+{x}+{y}")
        
    def decrypt(self):
        # Get input file
        filetypes = [("GPG files", "*.gpg")]

        input_file = filedialog.askopenfilename(
            title=f"Select file to decrypt",
            filetypes=filetypes
        )
        
        if not input_file:
            return
            
        # Get passphrase
        passphrase = self.get_passphrase("decrypt")
        if not passphrase:
            return
            
        # Process the file
        try:                # Decrypt to memory and show in window
            self.decrypt_and_show(input_file, passphrase)
                
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"decryption failed")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def decrypt_and_show(self, input_file, passphrase):
        """Decrypt file and show content in a text window"""
        try:
            # Create a temporary file for decryption ("Named" option because GPG needs a file to write to
            with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Decrypt to temporary file
            subprocess.run([
                self.gpg_path,
                "--batch",
                "--yes",
                "--decrypt",
                "--passphrase", passphrase,
                "--output", temp_path,
                input_file
            ], check=True)
            
            # Read the decrypted content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean up temporary file immediately
            os.unlink(temp_path)
            
            # Show content in window
            self.show_content_window(content, f"Decrypted: {os.path.basename(input_file)}")
            
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Decryption failed - wrong passphrase?")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def create_and_encrypt(self):
        """Create new content and encrypt it"""
        # Create content window
        content_window = tk.Toplevel(self.root)
        content_window.title("Create New Content")
        content_window.geometry("600x500")
        
        # Center the window
        content_window.transient(self.root)
        content_window.grab_set()
        
        # Content frame
        content_frame = tk.Frame(content_window, padx=20, pady=20)
        content_frame.pack(expand=True, fill='both')
        
        # Label
        tk.Label(content_frame, text="Enter your content to encrypt:", font=("Arial", 12)).pack(pady=10)
        
        # Text area
        text_area = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=70, height=20)
        text_area.pack(expand=True, fill='both', pady=10)
        text_area.focus()
        
        # Button frame
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=10)
        
        def save_and_encrypt():
            content = text_area.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Warning", "Please enter some content to encrypt.")
                return
            
            # Get save location
            output_file = filedialog.asksaveasfilename(
                title="Save encrypted file as",
                defaultextension=".gpg",
                filetypes=[("GPG files", "*.gpg")]
            )
            
            if not output_file:
                return
            
            # Get passphrase
            passphrase = self.get_passphrase("encrypt")
            if not passphrase:
                return
            
            try:
                # Create temporary file with content
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                    temp_file.write(content)
                    temp_path = temp_file.name
                
                # Encrypt the temporary file
                subprocess.run([
                    self.gpg_path,
                    "--batch",
                    "--yes",
                    "--symmetric",
                    "--passphrase", passphrase,
                    "--output", output_file,
                    temp_path
                ], check=True)
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                messagebox.showinfo("Success", f"Content encrypted and saved as: {output_file}")
                content_window.destroy()
                
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Encryption failed")
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            finally:
                # Ensure temp file is cleaned up
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        def cancel():
            content_window.destroy()
        
        # Buttons
        tk.Button(button_frame, text="Encrypt & Save", command=save_and_encrypt).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=cancel).pack(side='left', padx=10)
        
        # Center the window
        content_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - content_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - content_window.winfo_height()) // 2
        content_window.geometry(f"+{x}+{y}")
    
    def backup_existing_file(self, file_path):
        """Backup existing file by adding timestamp to filename"""
        if os.path.exists(file_path):
            # Get file info
            base_name = os.path.splitext(file_path)[0]
            extension = os.path.splitext(file_path)[1]
            
            # Create timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create backup filename
            backup_path = f"{base_name}_{timestamp}{extension}"
            
            # Rename existing file
            os.rename(file_path, backup_path)
            
            return backup_path
        return None
    
    def show_content_window(self, content, title, original_file=None):
        """Show content in a text window with modify option"""
        content_window = tk.Toplevel(self.root)
        content_window.title(title)
        content_window.geometry("600x500")
        
        # Center the window
        content_window.transient(self.root)
        content_window.grab_set()
        
        # Content frame
        content_frame = tk.Frame(content_window, padx=20, pady=20)
        content_frame.pack(expand=True, fill='both')
        
        # Label
        tk.Label(content_frame, text="Decrypted content:", font=("Arial", 12)).pack(pady=10)
        
        # Text area (initially read-only)
        text_area = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=70, height=20, state='disabled')
        text_area.pack(expand=True, fill='both', pady=10)
        
        # Enable temporarily to set content
        text_area.config(state='normal')
        text_area.insert("1.0", content)
        text_area.config(state='disabled')
        
        # Button frame
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=10)
        
        def modify_content():
            # Enable editing
            text_area.config(state='normal')
            # Change button text
            modify_btn.config(text="Save & Encrypt")
            modify_btn.config(command=save_and_encrypt)
            # Disable close button during editing
            close_btn.config(state='disabled')
        
        def save_and_encrypt():
            # Get modified content
            modified_content = text_area.get("1.0", tk.END).strip()
            
            # Get save location
            output_file = filedialog.asksaveasfilename(
                title="Save encrypted file as",
                defaultextension=".gpg",
                filetypes=[("GPG files", "*.gpg"), ("All files", "*.*")]
            )
            
            if not output_file:
                return
            
            # Check if file exists and backup if needed
            backup_path = self.backup_existing_file(output_file)
            if backup_path:
                messagebox.showinfo("Backup Created", 
                    f"Existing file backed up as:\n{os.path.basename(backup_path)}")
            
            # Get passphrase
            passphrase = self.get_passphrase("encrypt")
            if not passphrase:
                return
            
            try:
                # Create temporary file with modified content
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                    temp_file.write(modified_content)
                    temp_path = temp_file.name
                
                # Encrypt the temporary file
                subprocess.run([
                    self.gpg_path,
                    "--batch",
                    "--yes",
                    "--symmetric",
                    "--passphrase", passphrase,
                    "--output", output_file,
                    temp_path
                ], check=True)
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                success_message = f"Modified content encrypted and saved as: {output_file}"
                if backup_path:
                    success_message += f"\n\nPrevious version backed up as: {os.path.basename(backup_path)}"
                
                messagebox.showinfo("Success", success_message)
                content_window.destroy()
                
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Encryption failed")
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            finally:
                # Ensure temp file is cleaned up
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        def close_window():
            content_window.destroy()
        
        # Buttons
        modify_btn = tk.Button(button_frame, text="Modify", command=modify_content)
        modify_btn.pack(side='left', padx=10)
        
        close_btn = tk.Button(button_frame, text="Close", command=close_window, width=10)
        close_btn.pack(side='left', padx=10)
        
        # Center the window
        content_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - content_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - content_window.winfo_height()) // 2
        content_window.geometry(f"+{x}+{y}")
            
    def get_passphrase(self, action):
        # Create a new window for passphrase input
        pass_window = tk.Toplevel(self.root)
        pass_window.title(f"Enter Passphrase for {action.title()}ion")
        pass_window.geometry("400x180")
        
        # Center the window
        pass_window.transient(self.root)
        pass_window.grab_set()
        
        # Add widgets
        tk.Label(pass_window, text=f"Enter passphrase for {action}ion:").pack(pady=10)
        
        pass_var = tk.StringVar()
        show_pass = tk.BooleanVar()
        
        def toggle_password():
            if show_pass.get():
                pass_entry.config(show="")
            else:
                pass_entry.config(show="*")
                
        pass_entry = tk.Entry(pass_window, textvariable=pass_var, show="*", width=40)
        pass_entry.pack(pady=5)
        
        # Show password checkbox
        show_check = tk.Checkbutton(pass_window, text="Show passphrase", variable=show_pass, command=toggle_password)
        show_check.pack(pady=5)
        
        result = [None]  # Use list to store result
        
        def on_ok():
            result[0] = pass_var.get()
            pass_window.destroy()
            
        def on_cancel():
            pass_window.destroy()
            
        # Buttons
        button_frame = tk.Frame(pass_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=on_ok).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=on_cancel).pack(side='left', padx=10)
        
        # Center the window and wait for it to be closed
        pass_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - pass_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - pass_window.winfo_height()) // 2
        pass_window.geometry(f"+{x}+{y}")
        
        self.root.wait_window(pass_window)
        return result[0]

if __name__ == "__main__":
    root = tk.Tk()
    app = GPGGUI(root)
    root.mainloop() 