"""
Utility functions and constants for the Voice Assistant
"""

# Opening messages that the assistant can use when responding to commands
opening_text = [
    "I'm on it, sir.",
    "Working on it right away.",
    "Let me do that for you.",
    "Just a second.",
    "Consider it done.",
    "I'm processing your request.",
    "Right away, sir.",
    "I'll take care of that.",
    "As you wish."
]

# List of wake words that can be used to activate the assistant
WAKE_WORDS = ["hey assistant", "ok assistant", "hello assistant", "assistant"]

# Default paths for various features
DEFAULT_PATHS = {
    "screenshots": "screenshots",
    "music": "music",
    "notes": "data/notes.json",
    "todos": "data/todos.json",
    "reminders": "data/reminders.json"
}

# Helper function to get the current time in a readable format
def get_formatted_time():
    """Returns the current time in a human-readable format"""
    import datetime
    now = datetime.datetime.now()
    
    # Format: "3:45 PM" or "15:45"
    return now.strftime("%I:%M %p")

# Helper function to get the current date in a readable format
def get_formatted_date():
    """Returns the current date in a human-readable format"""
    import datetime
    now = datetime.datetime.now()
    
    # Format: "Wednesday, April 2, 2025"
    return now.strftime("%A, %B %d, %Y")