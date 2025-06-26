import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import platform
from version import VERSION

class GPGGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GPG File Encryption/Decryption")
        self.root.geometry("400x200")
        
        # Find GPG executable
        self.gpg_path = self.find_gpg()
        if not self.gpg_path:
            messagebox.showerror("Error", "GPG not found. Please install GPG first:\n\nmacOS: brew install gnupg\nUbuntu/Debian: sudo apt-get install gnupg\nCentOS/RHEL: sudo yum install gnupg")
            root.destroy()
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
        
        tk.Button(button_frame, text="Encrypt File", command=lambda: self.process_file("encrypt"), width=15, height=2).pack(side='left', padx=10)
        tk.Button(button_frame, text="Decrypt File", command=lambda: self.process_file("decrypt"), width=15, height=2).pack(side='left', padx=10)
        
        # About button
        about_button = tk.Button(main_frame, text="About", command=self.show_about, width=10)
        about_button.pack(pady=10)
        
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
        about_window.geometry("400x300")
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
        tk.Label(content_frame, text="A simple graphical interface for GPG file encryption and decryption.", 
                wraplength=350, justify='center').pack(pady=15)
        
        # Copyright
        tk.Label(content_frame, text="© 2024 Laurent Ach. All rights reserved.", 
                font=("Arial", 10)).pack(pady=10)
        
        # Features
        features_text = """Features:
• Simple two-button interface
• Automatic file extension handling
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
        
    def process_file(self, action):
        # Get input file
        if action == "encrypt":
            filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
        else:
            filetypes = [("GPG files", "*.gpg")]
            
        input_file = filedialog.askopenfilename(
            title=f"Select file to {action}",
            filetypes=filetypes
        )
        
        if not input_file:
            return
            
        # Set output file automatically
        if action == "encrypt":
            output_file = input_file + ".gpg"
        else:
            # For decryption, remove .gpg and add _decrypted to avoid conflicts
            base_name = input_file[:-4]  # Remove .gpg extension
            output_file = base_name + "_decrypted.txt"
            
        # Get passphrase
        passphrase = self.get_passphrase(action)
        if not passphrase:
            return
            
        # Process the file
        try:
            if action == "encrypt":
                # For symmetric encryption, we need to use --symmetric
                subprocess.run([
                    self.gpg_path,
                    "--batch",
                    "--yes",
                    "--symmetric",
                    "--passphrase", passphrase,
                    "--output", output_file,
                    input_file
                ], check=True)
            else:
                # For decryption
                subprocess.run([
                    self.gpg_path,
                    "--batch",
                    "--yes",
                    "--decrypt",
                    "--passphrase", passphrase,
                    "--output", output_file,
                    input_file
                ], check=True)
                
            messagebox.showinfo("Success", f"File {action}ed successfully!\nSaved as: {output_file}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"{action.title()}ion failed: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            
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