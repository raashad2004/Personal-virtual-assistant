"""
GUI for Voice Assistant

This module provides a graphical user interface for the voice assistant.
"""

import sys
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, Frame, Canvas, PhotoImage
import time
import pygame
from PIL import Image, ImageTk, ImageDraw
import os
import random
import glob
from datetime import datetime
import json

class ModernButton(tk.Button):
    """Custom modern button class"""
    
    def __init__(self, master=None, **kwargs):
        self.hover_color = kwargs.pop('hover_color', '#2980b9')
        self.normal_color = kwargs.pop('bg', '#3498db')
        
        super().__init__(master, bg=self.normal_color, **kwargs)
        
        # Round edges with border radius styling
        self.config(relief=tk.FLAT, borderwidth=0, padx=10, pady=6)
        
        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        self.config(bg=self.hover_color, cursor="hand2")
    
    def _on_leave(self, e):
        self.config(bg=self.normal_color)

    def start_blink(self):
        if not self._blink:
            self._blink = True
            self._last_bg = self["background"]
            self._animate()
            
    def stop_blink(self):
        self._blink = False
        try:
            self.config(background=self._last_bg)
        except:
            pass
            
    def _animate(self):
        if not self._blink:
            return
            
        current_bg = self["background"]
        next_bg = "#ff5252" if current_bg != "#ff5252" else self._last_bg
        self.config(background=next_bg)
        self.after(40, self._animate)

class CircleAnimationCanvas(Canvas):
    """Canvas for animated audio visualization"""
    
    def __init__(self, master=None, **kwargs):
        self.bg_color = kwargs.pop('bg', '#2c3e50')
        self.circle_color = kwargs.pop('circle_color', '#3498db')
        
        super().__init__(master, bg=self.bg_color, highlightthickness=0, **kwargs)
        
        self.circles = []
        self.is_active = False
        self.max_radius = min(self.winfo_reqwidth(), self.winfo_reqheight()) // 2
        
    def start_animation(self):
        """Start the audio visualization animation"""
        self.is_active = True
        self._animate()
    
    def stop_animation(self):
        """Stop the audio visualization animation"""
        self.is_active = False
        self.delete("all")
        
    def _animate(self):
        """Animate circles pulsing from center to edge"""
        if not self.is_active:
            return
            
        # Create new circle at center
        if random.random() < 0.3:  # Not every frame to avoid too many circles
            self.circles.append({
                "radius": 5,
                "alpha": 0.8,
                "speed": random.uniform(1.0, 3.0)
            })
        
        # Update all circles
        self.delete("all")
        
        center_x = self.winfo_width() // 2
        center_y = self.winfo_height() // 2
        
        new_circles = []
        for circle in self.circles:
            # Increase radius and decrease opacity
            circle["radius"] += circle["speed"]
            circle["alpha"] -= 0.01
            
            # Only keep visible circles
            if circle["alpha"] > 0 and circle["radius"] < self.max_radius:
                # Draw the circle with appropriate opacity
                hex_opacity = format(int(circle["alpha"] * 255), '02x')
                color = f"{self.circle_color}{hex_opacity}"
                
                self.create_oval(
                    center_x - circle["radius"], 
                    center_y - circle["radius"],
                    center_x + circle["radius"], 
                    center_y + circle["radius"],
                    outline=color, 
                    width=2, 
                    fill=""
                )
                new_circles.append(circle)
                
        self.circles = new_circles
        self.after(40, self._animate)

# Define color schemes
LIGHT_THEME = {
    "bg": "#f5f5f5",
    "text_bg": "#ffffff",
    "text_fg": "#000000",
    "button_bg": "#2196f3",
    "button_fg": "#ffffff",
    "status_bg": "#e0e0e0",
    "status_fg": "#000000",
    "user_msg_bg": "#e3f2fd",
    "assistant_msg_bg": "#e8f5e9"
}

DARK_THEME = {
    "bg": "#121212",
    "text_bg": "#1e1e1e",
    "text_fg": "#ffffff",
    "button_bg": "#0d47a1",
    "button_fg": "#ffffff",
    "status_bg": "#333333",
    "status_fg": "#bbbbbb",
    "user_msg_bg": "#01579b",
    "assistant_msg_bg": "#1b5e20"
}

class VoiceAssistantApp:
    """Main GUI application for Voice Assistant"""
    def __init__(self, root, start_callback, stop_callback):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("980x680")
        self.root.minsize(800, 600)
        
        # Set theme colors
        self.bg_color = "#f5f6fa"
        self.dark_bg_color = "#2c3e50"
        self.text_color = "#2c3e50"
        self.light_text_color = "#ecf0f1"
        self.accent_color = "#3498db"
        self.accent_hover = "#2980b9"
        self.secondary_color = "#2ecc71"
        self.warning_color = "#e74c3c"
        self.card_bg = "#ffffff"
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Set callback functions
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        
        # Status variables
        self.is_listening = False
        self.status_text = tk.StringVar()
        self.status_text.set("Ready")
        
        # Initialize pygame for sound effects
        pygame.mixer.init()
        
        # Create assets directory if it doesn't exist
        if not os.path.exists("assets"):
            os.makedirs("assets")
            
        # Create fonts
        self.title_font = ("Segoe UI", 24, "bold")
        self.subtitle_font = ("Segoe UI", 16, "bold")
        self.text_font = ("Segoe UI", 12)
        self.small_font = ("Segoe UI", 10)
        
        # Initialize avatars with default values
        self.assistant_avatar = None
        self.user_avatar = None
        
        # Setup theme support
        self.load_theme_preference()
        
        # Create the UI
        self.create_widgets()
        
        # Load avatars (after widgets are created)
        self.load_avatars()
        
        # Start time updater
        self.update_time()
        
    def load_theme_preference(self):
        """Load theme setting from file"""
        try:
            if not os.path.exists("data"):
                os.makedirs("data")
            
            if os.path.exists("data/settings.json"):
                with open("data/settings.json", "r") as f:
                    settings = json.load(f)
                    self.current_theme = settings.get("theme", "light")
        except Exception as e:
            print(f"Error loading theme setting: {e}")
    
    def save_theme_preference(self):
        """Save theme setting to file"""
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
            print(f"Error saving theme setting: {e}")
    
    def load_avatars(self):
        """Load avatar images for assistant and user"""
        try:
            from PIL import Image, ImageTk
            
            # Try to load assistant avatar from assets folder
            try:
                assistant_img = Image.open("assets/assistant_avatar.png")
                assistant_img = assistant_img.resize((40, 40), Image.LANCZOS)
                self.assistant_avatar = ImageTk.PhotoImage(assistant_img)
            except:
                # Create a default avatar if file doesn't exist
                self.assistant_avatar = self.create_default_avatar("A", "#2196F3")
            
            # Try to load user avatar from assets folder
            try:
                user_img = Image.open("assets/user_avatar.png")
                user_img = user_img.resize((40, 40), Image.LANCZOS)
                self.user_avatar = ImageTk.PhotoImage(user_img)
            except:
                # Create a default avatar if file doesn't exist
                self.user_avatar = self.create_default_avatar("U", "#4CAF50")
                
        except ImportError:
            # Create text-based avatars if PIL is not available
            self.assistant_avatar = self.create_text_avatar("A")
            self.user_avatar = self.create_text_avatar("U")
    
    def create_default_avatar(self, letter, color):
        """Create a simple colored circle with a letter as avatar"""
        try:
            from PIL import Image, ImageDraw, ImageTk, ImageFont
            
            # Create a blank image with RGBA mode
            img = Image.new('RGBA', (40, 40), color)
            draw = ImageDraw.Draw(img)
            
            # Add a letter in the center
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position to center it
            text_width, text_height = draw.textsize(letter, font=font)
            position = ((40-text_width)/2, (40-text_height)/2)
            
            # Draw the text
            draw.text(position, letter, fill="white", font=font)
            
            return ImageTk.PhotoImage(img)
        except:
            return self.create_text_avatar(letter)
    
    def create_text_avatar(self, letter):
        """Create a simple text-based avatar (fallback when PIL is not available)"""
        avatar_label = tk.Label(
            self.root, 
            text=letter,
            width=3,
            height=1,
            relief="raised",
            borderwidth=1
        )
        return avatar_label
    
    def create_widgets(self):
        # Main container
        self.main_container = Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a split view with sidebar and main content
        self.sidebar = Frame(self.main_container, bg=self.dark_bg_color, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        
        # Make the sidebar fixed width
        self.sidebar.pack_propagate(False)
        
        # Main content area
        self.content_frame = Frame(self.main_container, bg=self.bg_color)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create sidebar contents
        self.create_sidebar()
        
        # Create main content
        self.create_main_content()
        
    def create_sidebar(self):
        # App title in sidebar
        self.app_title = tk.Label(
            self.sidebar, 
            text="Voice Assistant",
            font=self.title_font,
            bg=self.dark_bg_color,
            fg=self.light_text_color,
            padx=10,
            pady=20
        )
        self.app_title.pack(fill=tk.X, anchor="n")
        
        # Audio visualization
        self.viz_label = tk.Label(
            self.sidebar,
            text="Audio Visualization",
            font=self.small_font,
            bg=self.dark_bg_color,
            fg=self.light_text_color,
            padx=10
        )
        self.viz_label.pack(fill=tk.X)
        
        # Create canvas for audio visualization
        self.viz_canvas = CircleAnimationCanvas(
            self.sidebar,
            bg=self.dark_bg_color,
            circle_color="#3498db",
            width=180,
            height=180
        )
        self.viz_canvas.pack(padx=20, pady=10)
        
        # Status indicator
        self.status_frame = Frame(self.sidebar, bg=self.dark_bg_color, padx=10, pady=10)
        self.status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Status:",
            font=self.small_font,
            bg=self.dark_bg_color,
            fg=self.light_text_color
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.status_value = tk.Label(
            self.status_frame,
            textvariable=self.status_text,
            font=self.small_font,
            bg=self.dark_bg_color,
            fg=self.accent_color
        )
        self.status_value.pack(side=tk.LEFT, padx=(5, 0))
        
        # Separator
        self.separator = ttk.Separator(self.sidebar, orient='horizontal')
        self.separator.pack(fill=tk.X, padx=10, pady=20)
        
        # Control buttons
        self.button_frame = Frame(self.sidebar, bg=self.dark_bg_color)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ModernButton(
            self.button_frame,
            text="Start Listening",
            font=self.text_font,
            bg=self.accent_color,
            fg=self.light_text_color,
            hover_color=self.accent_hover,
            command=self.start_listening,
            width=15
        )
        self.start_button.pack(fill=tk.X, pady=5)
        
        self.stop_button = ModernButton(
            self.button_frame,
            text="Stop Listening",
            font=self.text_font,
            bg="#95a5a6",  # Gray when disabled
            fg=self.light_text_color,
            hover_color="#7f8c8d",
            command=self.stop_listening,
            width=15,
            state=tk.DISABLED
        )
        self.stop_button.pack(fill=tk.X, pady=5)
        
        self.clear_button = ModernButton(
            self.button_frame,
            text="Clear Output",
            font=self.text_font,
            bg="#9b59b6",  # Purple
            fg=self.light_text_color,
            hover_color="#8e44ad",
            command=self.clear_output,
            width=15
        )
        self.clear_button.pack(fill=tk.X, pady=5)
        
        # Exit button at the bottom of sidebar
        self.sidebar_bottom = Frame(self.sidebar, bg=self.dark_bg_color)
        self.sidebar_bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)
        
        self.exit_button = ModernButton(
            self.sidebar_bottom,
            text="Exit",
            font=self.text_font,
            bg=self.warning_color,
            fg=self.light_text_color,
            hover_color="#c0392b",
            command=self.exit_app,
            width=15
        )
        self.exit_button.pack(fill=tk.X)
        
    def create_main_content(self):
        # Header
        self.header = Frame(self.content_frame, bg=self.card_bg, padx=20, pady=15)
        self.header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        self.header_title = tk.Label(
            self.header,
            text="Conversation",
            font=self.subtitle_font,
            bg=self.card_bg,
            fg=self.text_color
        )
        self.header_title.pack(side=tk.LEFT)
        
        # Time indicator
        self.time_var = tk.StringVar()
        self.update_time()
        
        self.time_label = tk.Label(
            self.header,
            textvariable=self.time_var,
            font=self.small_font,
            bg=self.card_bg,
            fg="#95a5a6"  # Light gray
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Conversation area
        self.chat_frame = Frame(self.content_frame, bg=self.bg_color, padx=20, pady=10)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create a canvas with scrollbar for the chat
        self.chat_canvas = Canvas(self.chat_frame, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas to hold the messages
        self.messages_frame = Frame(self.chat_canvas, bg=self.bg_color)
        self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        
        # Configure the messages frame to expand the full width of the canvas
        self.messages_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(
            scrollregion=self.chat_canvas.bbox("all"),
            width=self.chat_frame.winfo_width()-20
        ))
        
        # Mouse wheel scrolling
        self.chat_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Control area at the bottom
        self.control_frame = Frame(self.content_frame, bg=self.card_bg, height=80)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=20)
        
        # Make the control frame fixed height
        self.control_frame.pack_propagate(False)
        
        # Input hint
        self.input_hint = tk.Label(
            self.control_frame,
            text="Use your voice or press 'Start Listening' to begin",
            font=self.text_font,
            bg=self.card_bg,
            fg="#95a5a6"
        )
        self.input_hint.pack(pady=20)
        
        # Add welcome message
        self.add_message("Hello! I'm your Voice Assistant. Click 'Start Listening' to begin.", "assistant")
        
    def update_time(self):
        """Update the time display"""
        current_time = time.strftime("%I:%M %p")
        self.time_var.set(current_time)
        self.root.after(30000, self.update_time)  # Update every 30 seconds
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def add_message(self, message, sender):
        """Add a message to the conversation history"""
        if not hasattr(self, 'assistant_avatar') or self.assistant_avatar is None:
            # Create fallback avatars if they don't exist
            self.assistant_avatar = self.create_text_avatar("A")
            self.user_avatar = self.create_text_avatar("U")
            
        # Choose the appropriate avatar based on sender
        avatar_img = self.assistant_avatar if sender.lower() == "assistant" else self.user_avatar
        
        # Create message frame
        message_frame = Frame(self.messages_frame, bg=self.bg_color, padx=10, pady=5)
        message_frame.pack(fill=tk.X, pady=8)
        
        # Avatar container
        avatar_frame = Frame(message_frame, bg=self.bg_color)
        avatar_frame.pack(side=tk.LEFT, padx=5)
        
        # Check if avatar is a Label (text avatar) or PhotoImage (image avatar)
        if isinstance(avatar_img, tk.Label):
            # Clone the text avatar for this message
            avatar_label = tk.Label(
                avatar_frame,
                text=avatar_img.cget("text"),
                width=avatar_img.cget("width"),
                height=avatar_img.cget("height"),
                relief=avatar_img.cget("relief"),
                borderwidth=avatar_img.cget("borderwidth"),
                bg=self.accent_color if sender.lower() == "assistant" else self.secondary_color,
                fg="white",
                font=self.small_font
            )
        else:
            # It's a PhotoImage, use it directly
            avatar_label = tk.Label(
                avatar_frame,
                image=avatar_img,
                bg=self.bg_color
            )
        
        avatar_label.pack(padx=5, pady=5)
        
        # Sender name
        sender_label = tk.Label(
            avatar_frame,
            text=sender.capitalize(),
            font=self.small_font,
            bg=self.bg_color,
            fg=self.text_color
        )
        sender_label.pack()
        
        # Message bubble container
        bubble_container = Frame(message_frame, bg=self.bg_color)
        bubble_container.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)
        
        # Message bubble
        message_bubble = Frame(
            bubble_container,
            bg=self.light_text_color,
            padx=12,
            pady=8,
            bd=1,
            relief=tk.SOLID
        )
        message_bubble.pack(side=tk.RIGHT, anchor="e")
        
        # Message text
        message_text = tk.Label(
            message_bubble,
            text=message,
            font=self.text_font,
            bg=self.light_text_color,
            fg=self.text_color,
            justify=tk.LEFT,
            wraplength=400
        )
        message_text.pack(anchor=tk.W)
        
        # Scroll to bottom - check which canvas name is used in the actual implementation
        try:
            # Try the first possible canvas name
            if hasattr(self, 'canvas'):
                self.canvas.update_idletasks()
                self.canvas.yview_moveto(1.0)
            # Try alternative canvas name if the first wasn't found
            elif hasattr(self, 'chat_canvas'):
                self.chat_canvas.update_idletasks()
                self.chat_canvas.yview_moveto(1.0)
            # If neither exists, use the messages_frame's parent if it's a canvas
            elif isinstance(self.messages_frame.master, tk.Canvas):
                self.messages_frame.master.update_idletasks()
                self.messages_frame.master.yview_moveto(1.0)
        except Exception as e:
            print(f"Warning: Could not scroll to bottom: {e}")
            # Don't raise the exception, just log it
    
    def start_listening(self):
        """Start listening for voice commands"""
        if not self.is_listening:
            self.is_listening = True
            self.status_text.set("Listening...")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL, bg=self.accent_color)
            
            # Start visualization
            self.viz_canvas.start_animation()
            
            # Update input hint
            self.input_hint.config(text="Listening... Speak now")
            
            # Call the callback in a separate thread to prevent freezing the GUI
            threading.Thread(target=self.start_callback, daemon=True).start()
    
    def stop_listening(self):
        """Stop listening for voice commands"""
        if self.is_listening:
            self.is_listening = False
            self.status_text.set("Stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED, bg="#95a5a6")
            
            # Stop visualization
            self.viz_canvas.stop_animation()
            
            # Update input hint
            self.input_hint.config(text="Voice detection paused. Press 'Start Listening' to resume")
            
            # Call the callback
            self.stop_callback()
    
    def update_status(self, status):
        """Update the status text"""
        self.status_text.set(status)
    
    def clear_output(self):
        """Clear the output display"""
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
            
        # Add cleared message
        self.add_message("Conversation cleared. How can I help you?", "assistant")
    
    def exit_app(self):
        """Exit the application"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()
            sys.exit()

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        # Switch theme
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        
        # Save preference
        self.save_theme_preference()
        
        # Update UI with new theme
        self.apply_theme()
        
    def apply_theme(self):
        """Apply the current theme to all UI elements"""
        colors = LIGHT_THEME if self.current_theme == "light" else DARK_THEME
        
        # Update root and main containers
        self.root.configure(bg=colors["bg"])
        self.content_frame.configure(bg=colors["bg"])
        
        # Update header
        self.header.configure(bg=colors["bg"])
        self.header_title.configure(bg=colors["bg"], fg=colors["text_fg"])
        self.time_label.configure(bg=colors["bg"], fg=colors["text_fg"])
        
        # Update theme button text
        self.start_button.configure(bg=colors["button_bg"], fg=colors["button_fg"])
        self.start_button.normal_color = colors["button_bg"]
        self.start_button.hover_color = colors["highlight_bg"]
        
        self.stop_button.configure(bg=colors["button_bg"], fg=colors["button_fg"])
        self.stop_button.normal_color = colors["button_bg"]
        self.stop_button.hover_color = colors["highlight_bg"]
        
        # Update sidebar
        self.sidebar.configure(bg=colors["bg"])
        self.sidebar.style.configure("TFrame", background=colors["bg"])
        
        # Update status bar
        self.status_label.configure(bg=colors["status_bg"], fg=colors["status_fg"])
        
        # Update messages
        self.chat_canvas.config(state=tk.NORMAL)
        self.chat_canvas.delete("all")
        self.chat_canvas.config(state=tk.DISABLED)
        
        # Re-add messages with updated colors
        current_messages = self.get_current_messages()
        for sender, message in current_messages:
            self.add_message(message, sender)
            
    def get_current_messages(self):
        """Extract current messages from text area"""
        messages = []
        content = self.chat_canvas.get(1.0, tk.END)
        lines = content.split('\n')
        
        current_sender = None
        current_message = []
        
        for line in lines:
            if line.startswith("User: "):
                if current_sender and current_message:
                    messages.append((current_sender, "\n".join(current_message)))
                current_sender = "User"
                current_message = [line[6:]]  # Remove "User: "
            elif line.startswith("Assistant: "):
                if current_sender and current_message:
                    messages.append((current_sender, "\n".join(current_message)))
                current_sender = "Assistant"
                current_message = [line[11:]]  # Remove "Assistant: "
            elif line.strip() and current_message:
                current_message.append(line)
        
        # Add the last message if any
        if current_sender and current_message:
            messages.append((current_sender, "\n".join(current_message)))
            
        return messages

def create_gui(start_callback, stop_callback):
    """Create and return the GUI instance"""
    root = tk.Tk()
    
    # Add application icon if available
    icon_path = "assets/icon.ico" 
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
        
    app = VoiceAssistantApp(root, start_callback, stop_callback)
    return root, app

if __name__ == "__main__":
    # For testing purposes only
    def mock_start():
        print("Starting...")
    
    def mock_stop():
        print("Stopping...")
    
    root, app = create_gui(mock_start, mock_stop)
    
    # Add some test messages
    app.add_message("Hello, how can I help you today?", "assistant")
    app.add_message("What's the weather like?", "user")
    app.add_message("The current temperature is 72°F with clear skies in New York. Would you like the forecast for the next few days as well?", "assistant")
    
    root.mainloop() 