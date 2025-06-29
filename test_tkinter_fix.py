#!/usr/bin/env python3

import os
import sys
import tkinter as tk
from tkinter import ttk

# Set environment variable to suppress deprecation warning
os.environ['TK_SILENCE_DEPRECATION'] = '1'

def test_different_approaches():
    print("=== Testing Different Tkinter Approaches ===")
    
    # Test 1: Basic tkinter with explicit background
    print("\n1. Testing basic tkinter with explicit background...")
    try:
        root = tk.Tk()
        root.configure(bg='white')  # Force white background
        root.title("Test 1: White Background")
        root.geometry("300x200")
        
        label = tk.Label(root, text="Test Window", bg='white', fg='black')
        label.pack(pady=20)
        
        print("✓ Test 1 window created")
        root.after(2000, root.destroy)  # Close after 2 seconds
        root.mainloop()
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
    
    # Test 2: Using ttk widgets
    print("\n2. Testing ttk widgets...")
    try:
        root = tk.Tk()
        root.title("Test 2: ttk Widgets")
        root.geometry("300x200")
        
        style = ttk.Style()
        style.theme_use('aqua')  # Use macOS aqua theme
        
        frame = ttk.Frame(root)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        label = ttk.Label(frame, text="ttk Test Window")
        label.pack(pady=20)
        
        button = ttk.Button(frame, text="Test Button")
        button.pack(pady=10)
        
        print("✓ Test 2 window created")
        root.after(2000, root.destroy)  # Close after 2 seconds
        root.mainloop()
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
    
    # Test 3: Minimal window
    print("\n3. Testing minimal window...")
    try:
        root = tk.Tk()
        root.title("Test 3: Minimal")
        root.geometry("200x100")
        
        # Don't set any background, let system handle it
        label = tk.Label(root, text="Minimal Test")
        label.pack(pady=20)
        
        print("✓ Test 3 window created")
        root.after(2000, root.destroy)  # Close after 2 seconds
        root.mainloop()
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")

if __name__ == "__main__":
    test_different_approaches() 