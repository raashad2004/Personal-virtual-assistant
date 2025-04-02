"""
Functions

This package contains the modules for voice assistant functionalities.
"""

import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import importlib

# Functions version
__version__ = "1.0.2"

# Set up logging
def setup_module_logging(module_name):
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        
    # Create logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    
    # Skip setup if already configured
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create file handler
    module_log_file = os.path.join(logs_dir, f"modules_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    file_handler = TimedRotatingFileHandler(
        module_log_file,
        when='midnight',
        interval=1,
        backupCount=14
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger

# Create a logger for the Functions package
logger = setup_module_logging("Functions")

# Ensure the Functions directory is in sys.path
# This allows direct imports like "from Functions.module import func"
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Helper function to safely import and get attributes
def safe_import(module_name, names):
    try:
        module = importlib.import_module(module_name)
        return {name: getattr(module, name) for name in names}
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import {module_name}: {str(e)}")
        return {}

# Import all function modules with error handling
try:
    logger.info("Importing OS operations from init.py")
    
    # First try importing from init.py (preferred naming)
    init_funcs = safe_import("Functions.init", [
        "launch_notepad",
        "launch_calculator",
        "launch_discord",
        "open_command_prompt",
        "activate_camera"
    ])
    
    # If not found, try _init_.py as fallback
    if not init_funcs:
        init_funcs = safe_import("Functions._init_", [
            "launch_notepad",
            "launch_calculator",
            "launch_discord",
            "open_command_prompt",
            "activate_camera"
        ])
    
    # If either import worked, set the functions in the namespace
    if init_funcs:
        logger.info("Successfully imported OS operations")
        launch_notepad = init_funcs.get("launch_notepad", lambda: "Notepad functionality not available")
        launch_calculator = init_funcs.get("launch_calculator", lambda: "Calculator functionality not available")
        launch_discord = init_funcs.get("launch_discord", lambda: "Discord functionality not available")
        open_command_prompt = init_funcs.get("open_command_prompt", lambda: "Command prompt functionality not available")
        activate_camera = init_funcs.get("activate_camera", lambda: "Camera functionality not available")
    else:
        logger.error("Failed to import OS operations from both init.py and _init_.py")
        # Define fallback functions
        def launch_notepad(): return "Notepad functionality not available"
        def launch_calculator(): return "Calculator functionality not available"
        def launch_discord(): return "Discord functionality not available"
        def open_command_prompt(): return "Command prompt functionality not available"
        def activate_camera(): return "Camera functionality not available"

    # Import online operations
    logger.info("Importing online operations")
    online_ops_funcs = safe_import("Functions.online_ops", [
        "get_ip_address",
        "fetch_latest_news",
        "get_advice",
        "get_joke",
        "fetch_trending_movies",
        "get_weather",
        "play_video_on_youtube",
        "google_search",
        "search_wikipedia",
        "send_email",
        "send_whatsapp_msg"
    ])
    
    if online_ops_funcs:
        logger.info("Successfully imported online operations")
        get_ip_address = online_ops_funcs.get("get_ip_address")
        fetch_latest_news = online_ops_funcs.get("fetch_latest_news")
        get_advice = online_ops_funcs.get("get_advice")
        get_joke = online_ops_funcs.get("get_joke")
        fetch_trending_movies = online_ops_funcs.get("fetch_trending_movies")
        get_weather = online_ops_funcs.get("get_weather")
        play_video_on_youtube = online_ops_funcs.get("play_video_on_youtube")
        google_search = online_ops_funcs.get("google_search")
        search_wikipedia = online_ops_funcs.get("search_wikipedia")
        send_email = online_ops_funcs.get("send_email")
        send_whatsapp_msg = online_ops_funcs.get("send_whatsapp_msg")
    else:
        logger.error("Failed to import online operations")
        # Define fallback functions
        def get_ip_address(): return "IP address functionality not available"
        def fetch_latest_news(): return ["News functionality not available"]
        def get_advice(): return "Advice functionality not available"
        def get_joke(): return "Joke functionality not available"
        def fetch_trending_movies(): return ["Movies functionality not available"]
        def get_weather(city): return {"condition": "unavailable", "temperature": "N/A", "feels_like": "N/A"}
        def play_video_on_youtube(video): return f"YouTube functionality not available"
        def google_search(query): return f"Google search functionality not available"
        def search_wikipedia(topic): return f"Wikipedia functionality not available"
        def send_email(to, subject, content): return False
        def send_whatsapp_msg(number, text): return False

    # Import task manager
    logger.info("Importing task manager")
    task_manager_funcs = safe_import("Functions.task_manager", [
        "add_todo",
        "complete_todo",
        "list_todos",
        "add_reminder",
        "check_due_reminders",
        "add_note",
        "find_note"
    ])
    
    if task_manager_funcs:
        logger.info("Successfully imported task manager")
        add_todo = task_manager_funcs.get("add_todo")
        complete_todo = task_manager_funcs.get("complete_todo")
        list_todos = task_manager_funcs.get("list_todos")
        add_reminder = task_manager_funcs.get("add_reminder")
        check_due_reminders = task_manager_funcs.get("check_due_reminders")
        add_note = task_manager_funcs.get("add_note")
        find_note = task_manager_funcs.get("find_note")
    else:
        logger.error("Failed to import task manager")
        # Define fallback functions
        def add_todo(task, priority="medium"): return f"Added task: {task} (placeholder)"
        def complete_todo(task_id): return f"Marked task {task_id} as completed (placeholder)"
        def list_todos(show_completed=False): return "No tasks found (placeholder)"
        def add_reminder(text, remind_time): return f"Reminder set for (placeholder)"
        def check_due_reminders(): return []
        def add_note(title, content): return f"Added note: {title} (placeholder)"
        def find_note(query): return []

    # Import system utilities
    logger.info("Importing system utilities")
    system_utils_funcs = safe_import("Functions.system_utils", [
        "get_system_info",
        "get_battery_info",
        "take_screenshot",
        "lock_screen",
        "shutdown_system",
        "restart_system",
        "cancel_shutdown"
    ])
    
    if system_utils_funcs:
        logger.info("Successfully imported system utilities")
        get_system_info = system_utils_funcs.get("get_system_info")
        get_battery_info = system_utils_funcs.get("get_battery_info")
        take_screenshot = system_utils_funcs.get("take_screenshot")
        lock_screen = system_utils_funcs.get("lock_screen")
        shutdown_system = system_utils_funcs.get("shutdown_system")
        restart_system = system_utils_funcs.get("restart_system")
        cancel_shutdown = system_utils_funcs.get("cancel_shutdown")
    else:
        logger.error("Failed to import system utilities")
        # Define fallback functions
        def get_system_info(): return {"os": "Unknown", "os_version": "N/A", "processor": "N/A", "cpu_usage": 0, "memory_percent": 0}
        def get_battery_info(): return {"error": "Battery info not available"}
        def take_screenshot(): return "Screenshot functionality not available"
        def lock_screen(): return "Lock screen functionality not available"
        def shutdown_system(delay=0): return "Shutdown functionality not available"
        def restart_system(delay=0): return "Restart functionality not available"
        def cancel_shutdown(): return "Cancel shutdown functionality not available"

    # Import entertainment
    logger.info("Importing entertainment")
    entertainment_funcs = safe_import("Functions.entertainment", [
        "MusicPlayer",
        "get_random_quote",
        "get_riddle",
        "tell_joke",
        "play_rock_paper_scissors"
    ])
    
    if entertainment_funcs:
        logger.info("Successfully imported entertainment")
        MusicPlayer = entertainment_funcs.get("MusicPlayer")
        get_random_quote = entertainment_funcs.get("get_random_quote")
        get_riddle = entertainment_funcs.get("get_riddle")
        tell_joke = entertainment_funcs.get("tell_joke")
        play_rock_paper_scissors = entertainment_funcs.get("play_rock_paper_scissors")
    else:
        logger.error("Failed to import entertainment")
        # Define fallback class and functions
        class MusicPlayer:
            def __init__(self, music_folder="music"):
                self.playing = False
                self.current_track = None
            def play(self, track_name=None): return "Music player functionality not available"
            def pause(self): return "Music player functionality not available"
            def resume(self): return "Music player functionality not available"
            def stop(self): return "Music player functionality not available"
            def set_volume(self, volume): return "Music player functionality not available"
        
        def get_random_quote(): return {"content": "Quote functionality not available", "author": "N/A"}
        def get_riddle(): return {"question": "Riddle functionality not available", "answer": "N/A"}
        def tell_joke(): return {"setup": "Joke functionality not available", "punchline": "N/A"}
        def play_rock_paper_scissors(player_choice): return {"result": "lose", "message": "Game functionality not available", "player": player_choice, "computer": "none"}

    # Import language tools
    logger.info("Importing language tools")
    language_tools_funcs = safe_import("Functions.language_tools", [
        "translate_text",
        "detect_language",
        "text_to_speech",
        "get_language_name",
        "correct_spelling"
    ])
    
    if language_tools_funcs:
        logger.info("Successfully imported language tools")
        translate_text = language_tools_funcs.get("translate_text")
        detect_language = language_tools_funcs.get("detect_language")
        text_to_speech = language_tools_funcs.get("text_to_speech")
        get_language_name = language_tools_funcs.get("get_language_name")
        correct_spelling = language_tools_funcs.get("correct_spelling")
    else:
        logger.error("Failed to import language tools")
        # Define fallback functions
        def translate_text(text, target_language="en"): return {"translated_text": "Translation not available", "original_text": text, "source_language": "unknown", "target_language": target_language}
        def detect_language(text): return {"language": "unknown", "confidence": 0.0}
        def text_to_speech(text, language="en", save_file=False, filename=None): return "Text-to-speech not available"
        def get_language_name(language_code): return f"Unknown ({language_code})"
        def correct_spelling(text): return text

    # Verify all imports were successful or fallbacks are in place
    logger.info("All modules initialized successfully")

except Exception as e:
    # Global error handler
    if logging.getLogger("Functions").hasHandlers():
        logger.critical(f"Critical error during module imports: {str(e)}")
    else:
        print(f"Critical error during module imports: {str(e)}")
    
    # Define essential fallback functions in case of critical failure
    def get_critical_error(): return f"Voice assistant modules failed to load: {str(e)}" 