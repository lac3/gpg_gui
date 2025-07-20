import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from gpg_process import GpgProcess

# Set environment variable to suppress deprecation warning
os.environ["TK_SILENCE_DEPRECATION"] = "1"

VERSION = "2.0"


class GpgGui:
    def __init__(self, root):
        self.root = root
        self.root.title("GPG File Encryption/Decryption")
        self.root.geometry("500x300+400+200")
        self.save_to_new_file = tk.BooleanVar()
        self.new_passphrase = tk.BooleanVar()

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
        main_frame.pack(expand=True, fill="both")

        # Title
        title_label = tk.Label(main_frame, text="Choose an action:", font=("Arial", 14))
        title_label.pack(pady=20)

        # Action buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Create & Encrypt",
            command=lambda: self.show_content_window(None, "New File Content"),
            relief="raised",
            borderwidth=2,
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame,
            text="Decrypt & View",
            command=self.decrypt,
            relief="raised",
            borderwidth=2,
        ).pack(side="left", padx=10)

        # Use private / public key toggle
        self.use_key = tk.BooleanVar()

        def on_use_key_toggle():
            if self.use_key.get() and not self.gpg_process.selected_key:
                # Show key selection dialog if no key is selected
                self.manage_keys()

        tk.Checkbutton(
            main_frame,
            text="Use Key for Encryption",
            variable=self.use_key,
            command=on_use_key_toggle,
        ).pack(pady=5)

        # Manage Keys button (initially hidden)
        self.manage_keys_button = tk.Button(
            button_frame,
            text="Manage Keys",
            command=self.manage_keys,
            relief="raised",
            borderwidth=2,
        )

        # Function to show/hide manage keys button
        def update_manage_keys_button():
            if self.use_key.get():
                self.manage_keys_button.pack(side="left", padx=10)
            else:
                self.manage_keys_button.pack_forget()

        # Bind the toggle to update button visibility
        self.use_key.trace_add("write", lambda *args: update_manage_keys_button())

        # Initial state
        update_manage_keys_button()

        # Close button
        close_button = tk.Button(
            main_frame,
            text="Close",
            command=root.destroy,
            relief="raised",
            borderwidth=2,
        )
        close_button.pack(pady=10)

    def decrypt(self):
        # Get input file
        filetypes = [("GPG files", "*.gpg")]

        input_file = filedialog.askopenfilename(
            title="Select file to decrypt", filetypes=filetypes
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
            messagebox.showerror("Error", str(e))
            return

        if content:
            self.show_content_window(
                content, f"Decrypted: {os.path.basename(input_file)}"
            )
        else:
            messagebox.showerror("Error", "Could not get decryption content")

    def backup_existing_file(self, file_path):
        """Backup existing file by adding timestamp to filename"""
        if os.path.exists(file_path):
            # Get file info
            base_path = os.path.splitext(file_path)[0]
            base_name = os.path.basename(base_path)
            extension = os.path.splitext(file_path)[1]

            # Create timestamp
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create backup filename
            backup_path = f"{base_path}_{timestamp}{extension}"

            # clean up old backup files, deleting the ones with oldest timestamps
            # but keep at least 2 backups
            keep_backups = 2
            pattern = re.compile(f"^{base_name}_(\\d{{8}})_(\\d{{6}}).*{extension}$")

            backup_files = [
                f for f in os.listdir(os.path.dirname(file_path)) if pattern.match(f)
            ]
            backup_files.sort(
                key=lambda x: int(pattern.match(x).group(1) + pattern.match(x).group(2))
            )
            for old_backup in backup_files[:-keep_backups]:
                print(
                    pattern.match(old_backup).group(1)
                    + pattern.match(old_backup).group(2)
                )
                print(f"Deleting old backup: {old_backup}")
                os.remove(os.path.join(os.path.dirname(file_path), old_backup))

            # Rename existing file
            os.rename(file_path, backup_path)

            return backup_path
        return None

    def show_content_window(self, content, title):
        """Show content in a text window with modify option"""
        # If content is None for now, it will be stored in a new output file
        if content is None:
            self.gpg_process.file_path = None
            self.save_to_new_file.set(True)
            self.new_passphrase.set(True)
        else:
            self.save_to_new_file.set(False)
            self.new_passphrase.set(False)

        content_window = tk.Toplevel(self.root)
        content_window.title(title)
        content_window.geometry("800x500+350+150")

        # Center the window
        content_window.transient(self.root)
        content_window.grab_set()

        # Content frame
        content_frame = tk.Frame(content_window, padx=20, pady=20)
        content_frame.pack(expand=True, fill="both")

        # Label
        label_text = (
            "Enter your content to encrypt:"
            if content is None
            else "Decrypted content:"
        )
        tk.Label(content_frame, text=label_text, font=("Arial", 12)).pack(pady=10)

        # Text area (initially read-only)
        text_area = scrolledtext.ScrolledText(
            content_frame, wrap=tk.WORD, width=70, height=20, state="disabled"
        )
        text_area.pack(expand=True, fill="both", pady=10)

        # Enable temporarily to set content
        text_area.config(state="normal")
        if content is not None:
            text_area.insert("1.0", content)
        text_area.config(state="disabled")

        # Button frame
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=10)

        def modify_content():
            # Enable editing
            text_area.config(state="normal")
            # Change button text
            modify_btn.config(text="Save & Encrypt")
            modify_btn.config(command=save_and_encrypt)
            # Disable close button during editing
            close_btn.config(state="disabled")
            # Enable change passphrase toggle and save to different file toggle
            if not self.use_key.get():
                new_passphrase_toggle.config(state="normal")
            new_file_toggle.config(state="normal")

            # Set up passphrase toggle update
            def update_passphrase_toggle():
                try:
                    if self.use_key.get():
                        new_passphrase_toggle.config(state="disabled")
                    else:
                        new_passphrase_toggle.config(state="normal")
                except tk.TclError:
                    # Widget doesn't exist yet, ignore
                    pass

            # Bind the toggle to update passphrase state
            self.use_key.trace_add("write", lambda *args: update_passphrase_toggle())

        def save_and_encrypt():
            # Get modified content
            modified_content = text_area.get("1.0", tk.END).strip()

            if not modified_content:
                messagebox.showwarning(
                    "Warning", "Please enter some content to encrypt."
                )
                return

            # Use the new save method
            if self.save_encrypted_content(modified_content):
                content_window.destroy()

        def close_window():
            content_window.destroy()

        # Buttons
        modify_btn = tk.Button(
            button_frame,
            text="Modify",
            command=modify_content,
            relief="raised",
            borderwidth=2,
        )
        modify_btn.pack(side="left", padx=10)

        close_btn = tk.Button(
            button_frame,
            text="Close",
            command=close_window,
            relief="raised",
            borderwidth=2,
        )
        close_btn.pack(side="left", padx=10)

        new_file_toggle = tk.Checkbutton(
            button_frame,
            text="New file",
            variable=self.save_to_new_file,
            state="disabled",
        )
        new_file_toggle.pack(side="left", padx=10)

        new_passphrase_toggle = tk.Checkbutton(
            button_frame,
            text="New passphrase",
            variable=self.new_passphrase,
            state="disabled",
        )
        new_passphrase_toggle.pack(side="left", padx=10)

        if content is None:
            # For new files, start in edit mode
            text_area.config(state="normal")
            modify_btn.config(text="Save & Encrypt")
            modify_btn.config(command=save_and_encrypt)
            close_btn.config(state="disabled")

        content_window.protocol("WM_DELETE_WINDOW", close_window)

    def get_passphrase(self, action):
        if (
            action == "encrypt"
            and self.gpg_process.passphrase
            and not self.new_passphrase.get()
        ):
            return self.gpg_process.passphrase

        # Create a new window for passphrase input
        pass_window = tk.Toplevel(self.root)
        pass_window.title(f"Enter Passphrase to {action.title()}")
        pass_window.geometry("400x180+450+300")

        # Center the window
        pass_window.transient(self.root)
        pass_window.grab_set()

        # Add widgets
        tk.Label(
            pass_window, text=f"Enter passphrase to {action.title()}:", bg="#f0f0f0"
        ).pack(pady=10)

        pass_var = tk.StringVar()
        show_pass = tk.BooleanVar()
        show_pass.set(True)

        def toggle_password():
            if show_pass.get():
                pass_entry.config(show="")
            else:
                pass_entry.config(show="*")

        pass_entry = tk.Entry(pass_window, textvariable=pass_var, show="", width=40)
        pass_entry.pack(pady=5)
        pass_entry.focus()

        # Show password checkbox
        show_check = tk.Checkbutton(
            pass_window,
            text="Show passphrase",
            variable=show_pass,
            command=toggle_password,
        )
        show_check.pack(pady=5)

        result = [None]  # Use list to store result

        def on_ok():
            result[0] = pass_var.get()
            pass_window.destroy()

        def on_cancel():
            pass_window.destroy()

        # Bind Enter key to OK button
        pass_entry.bind("<Return>", lambda event: on_ok())

        # Buttons
        button_frame = tk.Frame(pass_window)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame, text="OK", command=on_ok, relief="raised", borderwidth=2
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame,
            text="Cancel",
            command=on_cancel,
            relief="raised",
            borderwidth=2,
        ).pack(side="left", padx=10)

        pass_window.protocol("WM_DELETE_WINDOW", on_cancel)
        self.root.wait_window(pass_window)

        # If decrypting (for opening the file), store passphrase for when the content will be modified and reencrypted
        # If encrypting (for saving the file), reinitialize the passphrase
        if action == "decrypt":
            self.gpg_process.passphrase = result[0]
        else:
            self.gpg_process.passphrase = None  # Reinitialize the passphrase
        return result[0]

    def get_output_file(self):
        if self.gpg_process.file_path and not self.save_to_new_file.get():
            return self.gpg_process.file_path

        # use asksaveasfile to get the filename
        initial_dir = (
            self.last_directory if self.last_directory else os.path.expanduser("~")
        )
        output_file = filedialog.asksaveasfilename(
            title="Select filename to save file",
            initialdir=initial_dir,
            defaultextension=".gpg",
        )
        if not output_file:
            return False
        directory = os.path.dirname(output_file)
        self.save_last_directory(directory)
        if not output_file.endswith(".gpg"):
            output_file += ".gpg"
        self.gpg_process.file_path = output_file
        return output_file

    def save_encrypted_content(self, content):
        # Get output file
        output_file = self.get_output_file()
        if not output_file:
            return False
        self.gpg_process.file_path = output_file

        if self.use_key.get():
            # Use key for encryption
            if not self.gpg_process.selected_key:
                messagebox.showwarning("Warning", "Please select a key first")
                return False
            try:
                self.gpg_process.encrypt_with_key(content)
                success_message = f"Content encrypted and saved as: {output_file}"
                messagebox.showinfo("Success", success_message)
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {str(e)}")
                return False
        else:
            # Use passphrase for encryption
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

    def load_last_directory(self):
        """Load the last used directory from a file"""
        config_file = os.path.expanduser("~") + "/.gpg_gui_config"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                return f.read().strip()
        return None

    def save_last_directory(self, directory):
        """Save the last used directory to a file"""
        config_file = os.path.expanduser("~") + "/.gpg_gui_config"
        with open(config_file, "w") as f:
            f.write(directory)

    def manage_keys(self):
        key_window = tk.Toplevel(self.root)
        key_window.title("Select GPG Key")
        key_window.geometry("600x400")
        key_window.transient(self.root)
        key_window.grab_set()

        # Create listbox with scrollbar
        frame = tk.Frame(key_window, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        listbox = tk.Listbox(frame, width=70, height=15)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)

        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate listbox with keys
        for i, key in enumerate(self.gpg_process.secret_keys):
            listbox.insert(tk.END, f"{key[1]} ({key[0]})")
            # Highlight currently selected key if any
            if self.gpg_process.selected_key and key == self.gpg_process.selected_key:
                listbox.selection_set(i)

        def on_select():
            selection = listbox.curselection()
            if selection:
                self.gpg_process.selected_key = self.gpg_process.secret_keys[
                    selection[0]
                ]
                key_window.destroy()
            else:
                messagebox.showwarning("Warning", "Please select a key to select")

        def on_delete():
            selection = listbox.curselection()
            if selection:
                # Get the selected key info for confirmation
                selected_key = self.gpg_process.secret_keys[selection[0]]
                key_info = f"{selected_key[1]} ({selected_key[0]})"

                # Show confirmation dialog
                if messagebox.askyesno(
                    "Confirm Deletion",
                    f"Are you sure you want to delete this key?\n\n{key_info}",
                ):
                    try:
                        self.gpg_process.delete_key(selected_key[0])
                        messagebox.showinfo("Success", "Key deleted successfully")
                        # Refresh the listbox instead of closing
                        listbox.delete(0, tk.END)
                        for i, key in enumerate(self.gpg_process.secret_keys):
                            listbox.insert(tk.END, f"{key[1]} ({key[0]})")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete key: {str(e)}")
            else:
                messagebox.showwarning("Warning", "Please select a key to delete")

        def on_create():
            # Create dialog for name and email
            create_window = tk.Toplevel(key_window)
            create_window.title("Create New GPG Key")
            create_window.geometry("400x300")
            create_window.transient(key_window)
            create_window.grab_set()

            frame = tk.Frame(create_window, padx=20, pady=20)
            frame.pack(fill="both", expand=True)

            tk.Label(frame, text="Enter key details:").pack(pady=5)

            # Name entry
            tk.Label(frame, text="Name:").pack(anchor="w")
            name_var = tk.StringVar()
            name_entry = tk.Entry(frame, textvariable=name_var, width=40)
            name_entry.pack(pady=5, fill="x")

            # Email entry
            tk.Label(frame, text="Email:").pack(anchor="w")
            email_var = tk.StringVar()
            email_entry = tk.Entry(frame, textvariable=email_var, width=40)
            email_entry.pack(pady=5, fill="x")

            # Passphrase entry
            tk.Label(frame, text="Passphrase:").pack(anchor="w")
            passphrase_var = tk.StringVar()
            passphrase_entry = tk.Entry(
                frame, textvariable=passphrase_var, show="", width=40
            )
            passphrase_entry.pack(pady=5, fill="x")

            def create_key():
                name = name_var.get().strip()
                email = email_var.get().strip()
                passphrase = passphrase_var.get().strip()
                if name and email and passphrase:
                    try:
                        self.gpg_process.create_key(email, name, passphrase)
                        messagebox.showinfo("Success", "Key created successfully")
                        create_window.destroy()
                        # Refresh the listbox instead of closing
                        listbox.delete(0, tk.END)
                        for i, key in enumerate(self.gpg_process.secret_keys):
                            listbox.insert(tk.END, f"{key[1]} ({key[0]})")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to create key: {str(e)}")
                else:
                    messagebox.showwarning(
                        "Warning", "Please enter name, email and passphrase"
                    )

            def cancel():
                create_window.destroy()

            # Buttons
            button_frame = tk.Frame(frame)
            button_frame.pack(pady=10)

            tk.Button(button_frame, text="OK", command=create_key).pack(
                side="left", padx=5
            )
            tk.Button(button_frame, text="Cancel", command=cancel).pack(
                side="left", padx=5
            )

            name_entry.focus()
            name_entry.bind("<Return>", lambda e: email_entry.focus())
            email_entry.bind("<Return>", lambda e: passphrase_entry.focus())
            passphrase_entry.bind("<Return>", lambda e: create_key())

        def on_import():
            # Get file to import
            filetypes = [("GPG key files", "*.asc")]
            import_file = filedialog.askopenfilename(
                title="Select key file to import", filetypes=filetypes
            )
            print(import_file)
            if import_file:
                # Get passphrase for import
                passphrase = self.get_passphrase("import")
                if not passphrase:
                    return

                try:
                    self.gpg_process.import_key(import_file, passphrase)
                    messagebox.showinfo("Success", "Key imported successfully")
                    # Refresh the listbox
                    listbox.delete(0, tk.END)
                    for i, key in enumerate(self.gpg_process.secret_keys):
                        listbox.insert(tk.END, f"{key[1]} ({key[0]})")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to import key: {str(e)}")

        def on_export():
            selection = listbox.curselection()
            if selection:
                selected_key = self.gpg_process.secret_keys[selection[0]]
                filetypes = [("GPG key files", "*.asc")]
                export_file = filedialog.asksaveasfilename(
                    title="Save exported key as",
                    filetypes=filetypes,
                    defaultextension=".asc",
                )
                if export_file:
                    # Prompt for passphrase
                    passphrase = self.get_passphrase("export")
                    if not passphrase:
                        return
                    try:
                        self.gpg_process.export_key(
                            selected_key[0], export_file, passphrase
                        )
                        messagebox.showinfo(
                            "Success", f"Key exported successfully to {export_file}"
                        )
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to export key: {str(e)}")
            else:
                messagebox.showwarning("Warning", "Please select a key to export")

        def on_close():
            key_window.destroy()

        # Button frame
        button_frame = tk.Frame(key_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Select", command=on_select).pack(
            side="left", padx=5
        )
        tk.Button(button_frame, text="Delete", command=on_delete).pack(
            side="left", padx=5
        )
        tk.Button(button_frame, text="Create", command=on_create).pack(
            side="left", padx=5
        )
        tk.Button(button_frame, text="Import", command=on_import).pack(
            side="left", padx=5
        )
        tk.Button(button_frame, text="Export", command=on_export).pack(
            side="left", padx=5
        )
        tk.Button(button_frame, text="Close", command=on_close).pack(
            side="left", padx=5
        )

        print(self.gpg_process.secret_keys)


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = GpgGui(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback

        traceback.print_exc()
