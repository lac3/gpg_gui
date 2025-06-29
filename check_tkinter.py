#!/usr/bin/env python3

import tkinter as tk
import sys

def check_tkinter_info():
    print("=== Tkinter Version Information ===")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check tkinter version
    try:
        print(f"Tkinter version: {tk.TkVersion}")
    except AttributeError:
        print("Tkinter version: Not available")
    
    # Check Tcl version
    try:
        print(f"Tcl version: {tk.TclVersion}")
    except AttributeError:
        print("Tcl version: Not available")
    
    # Try to create a root window to test functionality
    print("\n=== Testing Tkinter Functionality ===")
    try:
        root = tk.Tk()
        print("✓ Tkinter root window created successfully")
        
        # Get window info
        print(f"Window ID: {root.winfo_id()}")
        print(f"Window path: {root.winfo_pathname(root.winfo_id())}")
        
        # Test basic functionality
        root.title("Tkinter Test")
        print("✓ Window title set successfully")
        
        # Close the window
        root.destroy()
        print("✓ Window destroyed successfully")
        
    except Exception as e:
        print(f"✗ Error creating tkinter window: {e}")
    
    print("\n=== Additional Information ===")
    
    # Check if we can import ttk
    try:
        from tkinter import ttk
        print("✓ ttk module available")
        
        # Check ttk themes
        style = ttk.Style()
        themes = style.theme_names()
        print(f"Available ttk themes: {list(themes)}")
        print(f"Current theme: {style.theme_use()}")
        
    except Exception as e:
        print(f"✗ ttk module error: {e}")

if __name__ == "__main__":
    check_tkinter_info() 