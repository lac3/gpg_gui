import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from gpg_process import GpgProcess
import os
# Set environment variable to suppress deprecation warning
os.environ['TK_SILENCE_DEPRECATION'] = '1'

VERSION = "2.0"

class GpgGui:
    def __init__(self, root):
        self.root = root
        self.root.title("GPG File Encryption/Decryption")
        self.root.geometry("500x300+400+200")
        self.passphrase = None
        self.output_file = None

        # Set app icon
        icon_path = "GpgGui.png"
        if os.path.exists(icon_path):
            try:
                from tkinter import PhotoImage
                icon = PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
            except Exception:
                # Silently fail if icon loading fails
                pass

        try:
            self.gpg_process = GpgProcess()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize GPG process: {str(e)}")
                
        # Bring window to front and give it focus
        self.root.lift()
        self.root.focus_force()
                
        # Load last used directory
        self.last_directory = self.load_last_directory()
        
        # Create main frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title_label = tk.Label(main_frame, text="Choose an action:", font=("Arial", 14))
        title_label.pack(pady=20)
        
        # Action buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Create & Encrypt", command=lambda: self.show_content_window(None, "New File Content"), 
                 relief='raised', borderwidth=2).pack(side='left', padx=10)
        tk.Button(button_frame, text="Decrypt & View", command=self.decrypt, 
                 relief='raised', borderwidth=2).pack(side='left', padx=10)
        
        # Close button
        close_button = tk.Button(main_frame, text="Close", command=root.destroy, 
                               relief='raised', borderwidth=2)
        close_button.pack(pady=10)
        
    def decrypt(self):
        # Get input file
        filetypes = [("GPG files", "*.gpg")]

        input_file = filedialog.askopenfilename(
            title=f"Select file to decrypt",
            filetypes=filetypes
        )
        
        if not input_file:
            return
        self.gpg_process.file_path = input_file
        # Get passphrase
        passphrase = self.get_passphrase("decrypt")
        if not passphrase:
            return
        self.gpg_process.passphrase = passphrase
            
        # Process the file
        try:
            content = self.gpg_process.decrypt()
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error decrypting file: {str(e)}")
            return
        
        if content:
            self.show_content_window(content, f"Decrypted: {os.path.basename(input_file)}")
        else:
            messagebox.showerror("Error", "Could not get decryption content")
        
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
    
    def show_content_window(self, content, title):
        # If content is None for now, it will be stored in a new output file
        if content is None:
            self.output_file = None

        """Show content in a text window with modify option"""
        content_window = tk.Toplevel(self.root)
        content_window.title(title)
        content_window.geometry("600x500+350+150")
        
        # Center the window
        content_window.transient(self.root)
        content_window.grab_set()
        
        # Content frame
        content_frame = tk.Frame(content_window, padx=20, pady=20)
        content_frame.pack(expand=True, fill='both')
        
        # Label
        label_text = "Enter your content to encrypt:" if content is None else "Decrypted content:"
        tk.Label(content_frame, text=label_text, font=("Arial", 12)).pack(pady=10)
        
        # Text area (initially read-only)
        text_area = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=70, height=20, state='disabled')
        text_area.pack(expand=True, fill='both', pady=10)
        
        # Enable temporarily to set content
        text_area.config(state='normal')
        if content is not None:
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
            
            if not modified_content:
                messagebox.showwarning("Warning", "Please enter some content to encrypt.")
                return
            
            # Use the new save method
            if self.save_encrypted_content(modified_content):
                content_window.destroy()
        
        def close_window():
            content_window.destroy()
        
        # Buttons
        modify_btn = tk.Button(button_frame, text="Modify", command=modify_content, 
                              relief='raised', borderwidth=2)
        modify_btn.pack(side='left', padx=10)
        
        close_btn = tk.Button(button_frame, text="Close", command=close_window, 
                              relief='raised', borderwidth=2)
        close_btn.pack(side='left', padx=10)
        
        if content is None:
            # For new files, start in edit mode
            text_area.config(state='normal')
            modify_btn.config(text="Save & Encrypt")
            modify_btn.config(command=save_and_encrypt)
            close_btn.config(state='disabled')
            
    def get_passphrase(self, action):
        # If passphrase was already entered when decrypting the file, use it
        if action == "encrypt" and self.passphrase:
            return self.passphrase
        
        # Create a new window for passphrase input
        pass_window = tk.Toplevel(self.root)
        pass_window.title(f"Enter Passphrase for {action.title()}ion")
        pass_window.geometry("400x180+450+300")
        
        # Center the window
        pass_window.transient(self.root)
        pass_window.grab_set()
        
        # Add widgets
        tk.Label(pass_window, text=f"Enter passphrase for {action}ion:", 
                bg='#f0f0f0').pack(pady=10)
        
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
            
        # Bind Enter key to OK button
        pass_entry.bind('<Return>', lambda event: on_ok())
        
        # Buttons
        button_frame = tk.Frame(pass_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=on_ok, relief='raised', borderwidth=2).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=on_cancel, relief='raised', borderwidth=2).pack(side='left', padx=10)
        
        self.root.wait_window(pass_window)

        # If decrypting (for opening the file), store passphrase for when the content will be modified and reencrypted
        # If encrypting (for saving the file), reinitialize the passphrase
        if action == "decrypt":
            self.passphrase = result[0]
        else:
            self.passphrase = None  # Reinitialize the passphrase
        return result[0]

    def get_output_file(self):
        if self.output_file:
            return self.output_file
        
        initial_dir = self.last_directory if self.last_directory else os.path.expanduser("~")
        directory = filedialog.askdirectory(
            title="Select directory to save file",
            initialdir=initial_dir
        )
        if not directory:
            return False
            
        self.save_last_directory(directory)
        
        filename = self.get_filename_dialog("Enter filename (without .gpg extension)", directory)
        if not filename:
            return False

        if not filename.endswith('.gpg'):
            filename += '.gpg'

        output_file = os.path.join(directory, filename)
        self.output_file = output_file
        return output_file

    def save_encrypted_content(self, content):
        """Handle the complete save process: filename selection, backup, and encryption"""

        # Get output file
        output_file = self.get_output_file()
        if not output_file:
            return False
        self.gpg_process.file_path = output_file
        
        # Get passphrase
        passphrase = self.get_passphrase("encrypt")
        if not passphrase:
            return False
        self.gpg_process.passphrase = passphrase

        # Handle backup if file exists
        backup_path = self.backup_existing_file(output_file)

        try:
            self.gpg_process.encrypt(content)

            success_message = f"Content encrypted and saved as: {output_file}"
            if backup_path:
                success_message += f"\n\nPrevious version backed up as: {os.path.basename(backup_path)}"
            
            messagebox.showinfo("Success", success_message)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            return False
    
    def get_filename_dialog(self, title, directory):
        """Simple dialog to get filename from user"""
        filename_window = tk.Toplevel(self.root)
        filename_window.title(title)
        filename_window.geometry("500x200+400+250")
        
        filename_window.transient(self.root)
        filename_window.grab_set()
        
        # Frame
        frame = tk.Frame(filename_window, padx=20, pady=20)
        frame.pack(expand=True, fill='both')
        
        # Show selected directory
        tk.Label(frame, text=f"Directory: {directory}", font=("Arial", 10)).pack(pady=5)
        tk.Label(frame, text="Enter filename:").pack(pady=5)
        
        filename_var = tk.StringVar()
        entry = tk.Entry(frame, textvariable=filename_var, width=50)
        entry.pack(pady=10)
        entry.focus()
        
        result = [None]
        
        def on_ok():
            filename = filename_var.get().strip()
            if filename:
                result[0] = filename
            filename_window.destroy()
            
        def on_cancel():
            filename_window.destroy()
            
        # Bind Enter key to OK button
        entry.bind('<Return>', lambda event: on_ok())
        
        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=on_ok, relief='raised', borderwidth=2).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=on_cancel, relief='raised', borderwidth=2).pack(side='left', padx=10)
        
        self.root.wait_window(filename_window)
        return result[0]

    def load_last_directory(self):
        """Load the last used directory from a file"""
        config_file = os.path.expanduser("~") + "/.gpg_gui_config"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return f.read().strip()
        return None
    
    def save_last_directory(self, directory):
        """Save the last used directory to a file"""
        config_file = os.path.expanduser("~") + "/.gpg_gui_config"
        with open(config_file, 'w') as f:
            f.write(directory)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = GpgGui(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc() 