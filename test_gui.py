"""
Simple test GUI with dark mode

This is a minimal GUI implementation that includes a dark mode toggle button.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import json
import time
from datetime import datetime

# Define color schemes
LIGHT_THEME = {
    "bg": "#f5f5f5",
    "text_bg": "#ffffff",
    "text_fg": "#000000",
    "button_bg": "#2196f3",
    "button_fg": "#ffffff",
    "status_bg": "#e0e0e0",
    "status_fg": "#000000"
}

DARK_THEME = {
    "bg": "#121212",
    "text_bg": "#1e1e1e",
    "text_fg": "#ffffff",
    "button_bg": "#0d47a1",
    "button_fg": "#ffffff",
    "status_bg": "#333333",
    "status_fg": "#bbbbbb"
}

class SimpleVoiceAssistantGUI:
    """A simple implementation of the Voice Assistant GUI"""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize theme
        self.current_theme = "light"
        self.load_theme_preference()
        
        # Create GUI
        self.create_gui()
        
        # Start time updater
        self.update_time()
    
    def load_theme_preference(self):
        """Load theme preference from file"""
        try:
            if not os.path.exists("data"):
                os.makedirs("data")
            
            if os.path.exists("data/settings.json"):
                with open("data/settings.json", "r") as f:
                    settings = json.load(f)
                    self.current_theme = settings.get("theme", "light")
        except Exception as e:
            print(f"Error loading theme: {e}")
    
    def save_theme_preference(self):
        """Save theme preference to file"""
        try:
            if not os.path.exists("data"):
                os.makedirs("data")
            
            settings = {}
            if os.path.exists("data/settings.json"):
                with open("data/settings.json", "r") as f:
                    settings = json.load(f)
            
            settings["theme"] = self.current_theme
            
            with open("data/settings.json", "w") as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving theme: {e}")
    
    def create_gui(self):
        """Create the GUI elements"""
        colors = LIGHT_THEME if self.current_theme == "light" else DARK_THEME
        
        # Configure root window
        self.root.title("Voice Assistant - Dark Mode Test")
        self.root.geometry("600x400")
        self.root.configure(bg=colors["bg"])
        
        # Create header frame
        self.header = tk.Frame(self.root, bg=colors["bg"], pady=10)
        self.header.pack(fill="x")
        
        # Add title
        self.title_label = tk.Label(
            self.header,
            text="Dark Mode Test",
            font=("Helvetica", 16, "bold"),
            bg=colors["bg"],
            fg=colors["text_fg"]
        )
        self.title_label.pack(side="left", padx=20)
        
        # Add theme toggle button
        self.theme_button = tk.Button(
            self.header,
            text="🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode",
            command=self.toggle_theme,
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        self.theme_button.pack(side="right", padx=20)
        
        # Add time display
        self.time_label = tk.Label(
            self.header,
            text="",
            font=("Helvetica", 12),
            bg=colors["bg"],
            fg=colors["text_fg"]
        )
        self.time_label.pack(side="right", padx=20)
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg=colors["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create text area
        self.text_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap="word",
            bg=colors["text_bg"],
            fg=colors["text_fg"],
            font=("Helvetica", 11)
        )
        self.text_area.pack(fill="both", expand=True)
        
        # Add sample text
        self.text_area.insert("1.0", "This is a dark mode test for the Voice Assistant.\n\n")
        self.text_area.insert("end", "You can toggle between light and dark mode using the button in the header.\n\n")
        self.text_area.insert("end", "The settings are saved between runs in data/settings.json.\n\n")
        
        # Create button frame
        self.button_frame = tk.Frame(self.root, bg=colors["bg"], pady=10)
        self.button_frame.pack(fill="x")
        
        # Add test button
        self.test_button = tk.Button(
            self.button_frame,
            text="Test Button",
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=20,
            pady=5
        )
        self.test_button.pack(side="left", padx=20)
        
        # Create status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief="sunken",
            anchor="w",
            bg=colors["status_bg"],
            fg=colors["status_fg"],
            padx=10
        )
        self.status_bar.pack(fill="x", side="bottom")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        # Switch theme
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        
        # Save preference
        self.save_theme_preference()
        
        # Update UI
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme to all UI elements"""
        colors = LIGHT_THEME if self.current_theme == "light" else DARK_THEME
        
        # Update root
        self.root.configure(bg=colors["bg"])
        
        # Update header
        self.header.configure(bg=colors["bg"])
        self.title_label.configure(bg=colors["bg"], fg=colors["text_fg"])
        self.time_label.configure(bg=colors["bg"], fg=colors["text_fg"])
        
        # Update theme button
        self.theme_button.configure(
            text="🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode",
            bg=colors["button_bg"],
            fg=colors["button_fg"]
        )
        
        # Update main frame and text area
        self.main_frame.configure(bg=colors["bg"])
        self.text_area.configure(bg=colors["text_bg"], fg=colors["text_fg"])
        
        # Update button frame and button
        self.button_frame.configure(bg=colors["bg"])
        self.test_button.configure(bg=colors["button_bg"], fg=colors["button_fg"])
        
        # Update status bar
        self.status_bar.configure(bg=colors["status_bg"], fg=colors["status_fg"])
        
        # Update status message
        self.status_bar.config(text=f"Theme changed to {self.current_theme}")
    
    def update_time(self):
        """Update the time display"""
        current_time = time.strftime("%I:%M:%S %p")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

if __name__ == "__main__":
    # Create and run the GUI
    root = tk.Tk()
    app = SimpleVoiceAssistantGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    root.mainloop() 