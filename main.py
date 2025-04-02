"""
Voice Assistant

A voice-controlled personal assistant with multiple functionalities.
"""

import sys
import platform
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configure logging with enhanced features
def setup_logging():
    # Create logger
    logger = logging.getLogger("VoiceAssistant")
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatters
    standard_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    detailed_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    
    # Console handler (for terminal output)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(standard_formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler with daily rotation
    log_file = os.path.join(logs_dir, f"assistant_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=30  # Keep logs for a month
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.INFO)
    
    # Debug log (separate file for detailed debugging)
    debug_log_file = os.path.join(logs_dir, f"debug_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    debug_handler = TimedRotatingFileHandler(
        debug_log_file,
        when='midnight',
        interval=1,
        backupCount=7  # Keep debug logs for a week
    )
    debug_handler.setFormatter(detailed_formatter)
    debug_handler.setLevel(logging.DEBUG)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(debug_handler)
    
    # Clean up old log files that might not be handled by the rotation system
    try:
        cleanup_old_logs()
    except Exception as e:
        print(f"Error cleaning up old logs: {e}")
    
    return logger

def cleanup_old_logs():
    """Remove old log files beyond retention period"""
    if not os.path.exists(logs_dir):
        return
        
    # Retention periods in days
    retention = {
        "assistant_": 30,
        "debug_": 7,
        "modules_": 14,
        "launcher_": 30,
        "test_": 7
    }
    
    now = datetime.datetime.now()
    log_files = os.listdir(logs_dir)
    
    for log_file in log_files:
        try:
            # Skip non-log files
            if not log_file.endswith('.log'):
                continue
                
            # Check against retention policies
            for prefix, days in retention.items():
                if log_file.startswith(prefix):
                    # Extract date from filename (format: prefix_YYYYMMDD.log)
                    try:
                        date_str = log_file[len(prefix):len(prefix)+8]
                        file_date = datetime.datetime.strptime(date_str, '%Y%m%d')
                        age = (now - file_date).days
                        
                        # Delete if older than retention period
                        if age > days:
                            os.remove(os.path.join(logs_dir, log_file))
                            print(f"Removed old log file: {log_file}")
                    except (ValueError, IndexError):
                        # If date parsing fails, skip this file
                        continue
        except Exception as e:
            print(f"Error processing log file {log_file}: {e}")
            continue
            
    # Check for assistant launch logs in root directory
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for file in os.listdir(current_dir):
            if file.endswith('.log'):
                # Delete any stray log files in root directory
                if file.startswith('assistant_launch_') or file == 'assistant.log':
                    try:
                        os.remove(os.path.join(current_dir, file))
                        print(f"Removed stray log file: {file}")
                    except Exception as e:
                        print(f"Error removing log file {file}: {e}")
    except Exception as e:
        print(f"Error checking for stray log files: {e}")

# Initialize logger
logger = setup_logging()
logger.info("=== Voice Assistant Started ===")
logger.info(f"Log directory: {logs_dir}")

# Apply compatibility patches for Python 3.12+
logger.info(f"Python version: {platform.python_version()}")
major, minor, _ = platform.python_version_tuple()

if int(major) == 3 and int(minor) >= 12:
    logger.info("Applying Python 3.12+ compatibility patches")
    
    # Patch for pkgutil.ImpImporter issue in Python 3.12
    try:
        import pkgutil
        if not hasattr(pkgutil, 'ImpImporter'):
            import types
            logger.info("Adding pkgutil.ImpImporter compatibility shim")
            pkgutil.ImpImporter = types.SimpleNamespace
    except Exception as e:
        logger.error(f"Failed to apply pkgutil patch: {e}")
    
    # Add other Python 3.12 specific patches here as needed

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add Functions directory to path
functions_dir = os.path.join(current_dir, 'Functions')
if functions_dir not in sys.path:
    sys.path.insert(0, functions_dir)

# Continue with regular imports
import requests
import time
import json
import threading
import tkinter as tk
from tkinter import messagebox
import pygame
from datetime import datetime, timedelta
from random import choice
from pprint import pprint

# Try to import utility module with error handling
try:
    from utils import opening_text
except ImportError:
    # Create a fallback if utils.py is missing
    opening_text = [
        "I'm on it, sir.",
        "I'm working on it.",
        "Let me do that for you.",
        "Just a second.",
        "Processing your request."
    ]
    print("Warning: utils.py not found, using fallback messages")

# Try to import GUI module with error handling
try:
    from gui import create_gui
except ImportError:
    # Create a simple fallback GUI function if gui.py is missing
    def create_gui(start_listening_callback, stop_listening_callback):
        root = tk.Tk()
        root.title("Voice Assistant")
        root.geometry("800x600")
        
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_area = tk.Text(frame, state=tk.DISABLED)
        text_area.pack(fill=tk.BOTH, expand=True)
        
        buttons_frame = tk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        start_button = tk.Button(buttons_frame, text="Start Listening", command=start_listening_callback)
        start_button.pack(side=tk.LEFT, padx=5)
        
        stop_button = tk.Button(buttons_frame, text="Stop Listening", command=stop_listening_callback)
        stop_button.pack(side=tk.LEFT, padx=5)
        
        status_label = tk.Label(frame, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create a simple app class to mimic the expected interface
        class SimpleApp:
            def __init__(self):
                self.text_area = text_area
                self.status_label = status_label
            
            def add_message(self, message, sender):
                self.text_area.config(state=tk.NORMAL)
                self.text_area.insert(tk.END, f"\n{sender.capitalize()}: {message}")
                self.text_area.config(state=tk.DISABLED)
                self.text_area.see(tk.END)
            
            def update_status(self, status):
                self.status_label.config(text=status)
        
        app = SimpleApp()
        return root, app
    
    print("Warning: gui.py not found, using simple fallback GUI")

# Import voice and speech modules
try:
    import pyttsx3
    import speech_recognition as sr
except ImportError as e:
    print(f"Error importing speech modules: {e}")
    print("Please install required packages: pip install pyttsx3 SpeechRecognition PyAudio")
    sys.exit(1)

# Import environment configuration
try:
    from decouple import config
except ImportError:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        def config(key, default=None):
            return os.environ.get(key, default)
    except ImportError:
        print("Neither python-decouple nor python-dotenv is installed. Please install one of them.")
        # Create a minimal fallback config function
        def config(key, default=None):
            return default
        print("Using fallback configuration with default values")

# Import optional visualization modules 
try:
    import pyautogui
    import psutil
    import platform
    from googletrans import Translator
    from gtts import gTTS
except ImportError as e:
    print(f"Warning: Some optional modules couldn't be imported: {e}")
    print("Some functionality may be limited.")

# Import the application modules with error handling
try:
    # Import online operations with fallback handling
    try:
        from Functions.online_ops import (
            get_ip_address as find_my_ip,
            fetch_latest_news as get_latest_news,
            get_advice as get_random_advice,
            get_joke as get_random_joke,
            fetch_trending_movies as get_trending_movies,
            get_weather as get_weather_report,
            play_video_on_youtube as play_on_youtube,
            google_search as search_on_google,
            search_wikipedia as search_on_wikipedia,
            send_email,
            send_whatsapp_msg as send_whatsapp_message
        )
    except ImportError as e:
        print(f"Warning: Online operation modules couldn't be imported: {e}")
        # Create placeholders for missing functions
        find_my_ip = lambda: "Could not import IP address function"
        get_latest_news = lambda: ["News functionality not available"]
        get_random_advice = lambda: "Advice functionality not available"
        get_random_joke = lambda: "Joke functionality not available"
        get_trending_movies = lambda: ["Movie functionality not available"]
        get_weather_report = lambda city: {"condition": "unavailable", "temperature": "N/A", "feels_like": "N/A"}
        play_on_youtube = lambda video: print(f"Would play {video} on YouTube if module was available")
        search_on_google = lambda query: print(f"Would search for {query} on Google if module was available")
        search_on_wikipedia = lambda topic: f"Wikipedia functionality not available"
        send_email = lambda to, subject, content: False
        send_whatsapp_message = lambda number, text: print(f"Would send WhatsApp message if module was available")
    
    # Import file system operations with fallback handling
    try:
        # Try the import with the underscore syntax first (original)
        try:
            from Functions._init_ import (
                launch_notepad as open_notepad,
                launch_calculator as open_calculator,
                launch_discord as open_discord,
                open_command_prompt as open_cmd,
                activate_camera as open_camera
            )
        except ImportError:
            # If that fails, try with regular naming convention
            from Functions.init import (
                launch_notepad as open_notepad,
                launch_calculator as open_calculator,
                launch_discord as open_discord,
                open_command_prompt as open_cmd,
                activate_camera as open_camera
            )
    except ImportError as e:
        print(f"Warning: File system operation modules couldn't be imported: {e}")
        # Create placeholder functions
        open_notepad = lambda: print("Notepad functionality not available")
        open_calculator = lambda: print("Calculator functionality not available")
        open_discord = lambda: print("Discord functionality not available")
        open_cmd = lambda: print("Command prompt functionality not available")
        open_camera = lambda: print("Camera functionality not available")
    
    # Import the task manager modules with fallback handling
    try:
        from Functions.task_manager import add_todo, complete_todo, list_todos, add_reminder, check_due_reminders, add_note, find_note
    except ImportError as e:
        print(f"Warning: Task manager modules couldn't be imported: {e}")
        # Create placeholder functions
        add_todo = lambda task, priority="medium": f"Added task: {task} (placeholder)"
        complete_todo = lambda task_id: f"Marked task {task_id} as completed (placeholder)"
        list_todos = lambda show_completed=False: "No tasks found (placeholder)"
        add_reminder = lambda text, remind_time: f"Reminder set for (placeholder)"
        check_due_reminders = lambda: []
        add_note = lambda title, content: f"Added note: {title} (placeholder)"
        find_note = lambda query: []
    
    # Import system utility modules with fallback handling
    try:
        from Functions.system_utils import (
            get_system_info, get_battery_info, take_screenshot,
            lock_screen, shutdown_system, restart_system, cancel_shutdown
        )
    except ImportError as e:
        print(f"Warning: System utility modules couldn't be imported: {e}")
        # Create placeholder functions
        get_system_info = lambda: {"os": "Unknown", "os_version": "N/A", "processor": "N/A", "cpu_usage": 0, "memory_percent": 0}
        get_battery_info = lambda: {"error": "Battery info not available"}
        take_screenshot = lambda: "Screenshot functionality not available"
        lock_screen = lambda: "Lock screen functionality not available"
        shutdown_system = lambda delay=0: "Shutdown functionality not available"
        restart_system = lambda delay=0: "Restart functionality not available"
        cancel_shutdown = lambda: "Cancel shutdown functionality not available"
    
    # Import entertainment modules with fallback handling
    try:
        from Functions.entertainment import (
            MusicPlayer, get_random_quote, get_riddle, tell_joke, play_rock_paper_scissors
        )
    except ImportError as e:
        print(f"Warning: Entertainment modules couldn't be imported: {e}")
        # Create placeholder classes and functions
        class MusicPlayer:
            def __init__(self, music_folder="music"):
                self.playing = False
                self.current_track = None
            def play(self, track_name=None):
                return "Music player functionality not available"
            def pause(self):
                return "Music player functionality not available"
            def resume(self):
                return "Music player functionality not available"
            def stop(self):
                return "Music player functionality not available"
            def set_volume(self, volume):
                return "Music player functionality not available"
        
        get_random_quote = lambda: {"content": "Quote functionality not available", "author": "N/A"}
        get_riddle = lambda: {"question": "Riddle functionality not available", "answer": "N/A"}
        tell_joke = lambda: {"setup": "Joke functionality not available", "punchline": "N/A"}
        play_rock_paper_scissors = lambda player_choice: {"result": "lose", "message": "Game functionality not available", "player": player_choice, "computer": "none"}
    
    # Import language tools modules with fallback handling
    try:
        from Functions.language_tools import (
            translate_text, detect_language, text_to_speech, get_language_name, correct_spelling
        )
    except ImportError as e:
        print(f"Warning: Language tool modules couldn't be imported: {e}")
        # Create placeholder functions
        translate_text = lambda text, target_language="en": {"translated_text": "Translation not available", "original_text": text, "source_language": "unknown", "target_language": target_language}
        detect_language = lambda text: {"language": "unknown", "confidence": 0.0}
        text_to_speech = lambda text, language="en", save_file=False, filename=None: "Text-to-speech not available"
        get_language_name = lambda language_code: f"Unknown ({language_code})"
        correct_spelling = lambda text: text

except Exception as e:
    print(f"Critical error during initialization: {e}")
    sys.exit(1)

# Load environment variables with fallback values
try:
    USERNAME = config('USER', 'User')
    BOTNAME = config('BOTNAME', 'Assistant')
    SPEECH_RATE = int(config('SPEECH_RATE', '190'))
    SPEECH_VOLUME = float(config('SPEECH_VOLUME', '1.0'))
    VOICE_INDEX = int(config('VOICE_INDEX', '1'))
    USE_GUI = config('GUI_MODE', 'True').lower() in ('true', 'yes', '1', 't')
except Exception as e:
    logger.error(f"Error loading config: {str(e)}")
    USERNAME = "User"
    BOTNAME = "Assistant"
    SPEECH_RATE = 190
    SPEECH_VOLUME = 1.0
    VOICE_INDEX = 1
    USE_GUI = True

# Initialize global variables
engine = None
gui_app = None
gui_root = None
music_player = None
recognizer = None
listening_thread = None
is_running = True
listening_event = threading.Event()

def initialize_tts():
    """Initialize the text-to-speech engine"""
    global engine
    try:
        engine = pyttsx3.init('sapi5')

        # Set Rate
        engine.setProperty('rate', SPEECH_RATE)

        # Set Volume
        engine.setProperty('volume', SPEECH_VOLUME)

        # Set Voice (Female)
        voices = engine.getProperty('voices')
        if len(voices) > VOICE_INDEX:
            engine.setProperty('voice', voices[VOICE_INDEX].id)
        else:
            logger.warning(f"Voice index {VOICE_INDEX} not available, using default voice")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing TTS: {str(e)}")
        return False

def initialize_speech_recognition():
    """Initialize the speech recognition"""
    global recognizer
    try:
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        recognizer.energy_threshold = 4000  # Adjust this value based on your environment
        
        # Test if microphone is available
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            logger.error(f"Error accessing microphone: {str(e)}")
            print("Error: Could not access microphone. Please ensure your microphone is properly connected.")
            print("The application will continue, but voice recognition will not be available.")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error initializing speech recognition: {str(e)}")
        return False

def initialize_music_player():
    """Initialize the music player"""
    global music_player
    try:
        music_player = MusicPlayer()
        return True
    except Exception as e:
        logger.error(f"Error initializing music player: {str(e)}")
        return False

def initialize_system():
    """Initialize all system components"""
    success = True
    
    # Create necessary directories
    for directory in ["data", "audio", "screenshots", "music", "assets"]:
        dir_path = os.path.join(current_dir, directory)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                logger.info(f"Created directory: {dir_path}")
            except Exception as e:
                logger.error(f"Error creating directory {dir_path}: {str(e)}")
                success = False
    
    # Initialize components
    if not initialize_tts():
        success = False
    
    if not initialize_speech_recognition():
        success = False
    
    if not initialize_music_player():
        success = False
    
    return success

def speak(text):
    """Used to speak whatever text is passed to it"""
    try:
        # Update GUI if available
        if gui_app:
            gui_app.add_message(text, "assistant")
        
        # Log the response
        logger.info(f"Assistant: {text}")
        
        # Speak the text
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logger.error(f"Error in speak function: {str(e)}")

def greet_user():
    """Greets the user according to the time"""
    try:
        hour = datetime.now().hour
        greeting = ""
    
        if (hour >= 6) and (hour < 12):
            greeting = f"Good Morning {USERNAME}"
        elif (hour >= 12) and (hour < 16):
            greeting = f"Good afternoon {USERNAME}"
        elif (hour >= 16) and (hour < 19):
            greeting = f"Good Evening {USERNAME}"
        else:
            greeting = f"Hello {USERNAME}"

        speak(greeting)
        speak(f"I am {BOTNAME}. How may I assist you today?")
    except Exception as e:
        logger.error(f"Error greeting user: {str(e)}")
        speak(f"Hello {USERNAME}, I am {BOTNAME}. How may I assist you today?")

def take_user_input():
    """Takes user input, recognizes it using Speech Recognition module and converts it into text"""
    try:
        if gui_app:
            gui_app.update_status("Listening...")
        
        with sr.Microphone() as source:
            logger.info('Listening....')
            recognizer.pause_threshold = 1
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

        if gui_app:
            gui_app.update_status("Recognizing...")
        
        logger.info('Recognizing...')
        query = recognizer.recognize_google(audio, language='en-in')
        
        # Log the user's input
        logger.info(f"User said: {query}")
        
        # Update GUI if available
        if gui_app:
            gui_app.add_message(query, "user")
            gui_app.update_status("Ready")
        
        if not ('exit' in query.lower() or 'stop' in query.lower()):
            speak(choice(opening_text))
        else:
            hour = datetime.now().hour
            if hour >= 21 or hour < 6:
                speak("Good night sir, take care!")
            else:
                speak('Have a good day sir!')
            if gui_app:
                gui_app.update_status("Exiting...")
            sys.exit()
    except sr.UnknownValueError:
        if gui_app:
            gui_app.update_status("Ready")
        speak('Sorry, I could not understand. Could you please say that again?')
        query = ""
    except sr.RequestError:
        if gui_app:
            gui_app.update_status("Network Error")
        speak('Network error. Please check your connection.')
        query = ""
    except Exception as e:
        logger.error(f"Error in speech recognition: {str(e)}")
        if gui_app:
            gui_app.update_status("Error")
        speak('Sorry, I encountered an error. Please try again.')
        query = ""
    
    return query.lower() if query else ""

def check_reminders():
    """Check for due reminders and notify the user"""
    try:
        due_reminders = check_due_reminders()
        if due_reminders:
            speak(f"You have {len(due_reminders)} reminder{'s' if len(due_reminders) > 1 else ''} due.")
            for reminder in due_reminders:
                speak(f"Reminder: {reminder.get('text')}")
    except Exception as e:
        logger.error(f"Error checking reminders: {str(e)}")

def handle_command(query):
    """Process and respond to user commands"""
    try:
        # Basic commands
        if 'hello' in query or 'hi' in query:
            speak(f"Hello {USERNAME}, how can I help you?")
        
        # System commands
        elif 'open notepad' in query:
            speak("Opening Notepad")
            open_notepad()

        elif 'open discord' in query:
            speak("Opening Discord")
            open_discord()

        elif 'open command prompt' in query or 'open cmd' in query:
            speak("Opening Command Prompt")
            open_cmd()

        elif 'open camera' in query:
            speak("Opening Camera")
            open_camera()

        elif 'open calculator' in query:
            speak("Opening Calculator")
            open_calculator()

        elif 'take screenshot' in query:
            speak("Taking a screenshot")
            result = take_screenshot()
            speak(result)
        
        elif 'system info' in query or 'system information' in query:
            speak("Here's your system information")
            system_info = get_system_info()
            speak(f"You are running {system_info.get('os')} {system_info.get('os_version')} on a {system_info.get('processor')} processor")
            speak(f"Your CPU usage is at {system_info.get('cpu_usage')}% with {system_info.get('memory_percent')}% memory usage")
            for key, value in system_info.items():
                print(f"{key}: {value}")
        
        elif 'battery' in query:
            battery_info = get_battery_info()
            if "error" in battery_info:
                speak("Sorry, I couldn't retrieve battery information")
            else:
                speak(f"Your battery is at {battery_info.get('percent')}%")
                if battery_info.get('power_plugged'):
                    speak("Your device is plugged in and charging")
                else:
                    speak(f"You have approximately {battery_info.get('time_left')} of battery life remaining")
        
        elif 'lock' in query and ('computer' in query or 'screen' in query or 'system' in query):
            speak("Locking your screen")
            lock_screen()
        
        elif ('shutdown' in query or 'turn off' in query) and 'computer' in query:
            speak("Are you sure you want to shutdown your computer?")
            confirmation = take_user_input()
            if 'yes' in confirmation or 'yeah' in confirmation:
                speak("Shutting down your computer in 10 seconds")
                shutdown_system(10)
            else:
                speak("Shutdown canceled")
        
        elif ('restart' in query or 'reboot' in query) and 'computer' in query:
            speak("Are you sure you want to restart your computer?")
            confirmation = take_user_input()
            if 'yes' in confirmation or 'yeah' in confirmation:
                speak("Restarting your computer in 10 seconds")
                restart_system(10)
            else:
                speak("Restart canceled")
        
        elif 'cancel shutdown' in query or 'cancel restart' in query:
            speak("Canceling scheduled shutdown or restart")
            cancel_shutdown()
        
        # Online operations
        elif 'ip address' in query:
            ip_address = find_my_ip()
            speak(f'Your IP Address is {ip_address}.\n For your convenience, I am printing it on the screen sir.')
            print(f'Your IP Address is {ip_address}')

        elif 'wikipedia' in query:
            speak('What do you want to search on Wikipedia, sir?')
            search_query = take_user_input()
            if search_query:  # Check if search_query is not empty
                results = search_on_wikipedia(search_query)
                speak(f"According to Wikipedia, {results}")
                speak("For your convenience, I am printing it on the screen sir.")
                print(results)
            else:
                speak("I didn't catch your search query. Please try again.")

        elif 'youtube' in query:
            speak('What do you want to play on Youtube, sir?')
            video = take_user_input()
            if video:  # Check if video is not empty
                speak(f"Playing {video} on YouTube")
                play_on_youtube(video)
            else:
                speak("I didn't catch what you want to play. Please try again.")

        elif 'search on google' in query or 'google' in query:
            speak('What do you want to search on Google, sir?')
            search_query = take_user_input()
            if search_query:  # Check if search_query is not empty
                speak(f"Searching for {search_query} on Google")
                search_on_google(search_query)
            else:
                speak("I didn't catch your search query. Please try again.")
        
        elif 'send whatsapp message' in query or 'whatsapp' in query:
            speak('On what number should I send the message sir? Please enter in the console: ')
            number = input("Enter the number: ")
            speak("What is the message sir?")
            message = take_user_input()
            if message:  # Check if message is not empty
                send_whatsapp_message(number, message)
                speak("I've sent the message sir.")
            else:
                speak("I didn't catch your message. Please try again.")

        elif 'send an email' in query or 'send email' in query:
            speak("On what email address do I send sir? Please enter in the console: ")
            receiver_address = input("Enter email address: ")
            speak("What should be the subject sir?")
            subject = take_user_input().capitalize()
            speak("What is the message sir?")
            message = take_user_input().capitalize()
            if message:  # Check if message is not empty
                if send_email(receiver_address, subject, message):
                    speak("I've sent the email sir.")
                else:
                    speak("Something went wrong while I was sending the mail. Please check the error logs sir.")
            else:
                speak("I didn't catch your message. Please try again.")

        elif 'joke' in query:
            speak(f"Hope you like this one sir")
            joke = get_random_joke()
            speak(joke)
            speak("For your convenience, I am printing it on the screen sir.")
            pprint(joke)

        elif 'advice' in query:
            speak(f"Here's an advice for you, sir")
            advice = get_random_advice()
            speak(advice)
            speak("For your convenience, I am printing it on the screen sir.")
            pprint(advice)

        elif 'trending movies' in query or 'movie' in query:
            movies = get_trending_movies()
            speak(f"Some of the trending movies are: {', '.join(movies[:3])}")
            speak("For your convenience, I am printing it on the screen sir.")
            print(*movies, sep='\n')

        elif 'news' in query:
            speak(f"I'm reading out the latest news headlines, sir")
            news = get_latest_news()
            speak(', '.join(news[:3]))
            speak("For your convenience, I am printing it on the screen sir.")
            print(*news, sep='\n')

        elif 'weather' in query:
            ip_address = find_my_ip()
            city = requests.get(f"https://ipapi.co/{ip_address}/city/").text
            speak(f"Getting weather report for your city {city}")
            weather_data = get_weather_report(city)
            weather = weather_data.get("condition", "unknown")
            temperature = weather_data.get("temperature", "unknown")
            feels_like = weather_data.get("feels_like", "unknown")
            speak(f"The current temperature is {temperature}, but it feels like {feels_like}")
            speak(f"Also, the weather report talks about {weather}")
            speak("For your convenience, I am printing it on the screen sir.")
            print(f"Description: {weather}\nTemperature: {temperature}\nFeels like: {feels_like}")
        
        # Task management
        elif 'add task' in query or 'add to do' in query:
            speak("What task would you like to add?")
            task = take_user_input()
            if task:  # Check if task is not empty
                speak("What priority? High, medium, or low?")
                priority = take_user_input().lower()
                if not priority or priority not in ["high", "medium", "low"]:
                    priority = "medium"
                result = add_todo(task, priority)
                speak(result)
            else:
                speak("I didn't catch the task. Please try again.")
        
        elif 'complete task' in query or 'mark task as done' in query:
            speak("What is the task ID?")
            try:
                task_id = int(take_user_input())
                result = complete_todo(task_id)
                speak(result)
            except ValueError:
                speak("I need a task number to mark as complete.")
        
        elif 'list tasks' in query or 'show tasks' in query or 'show to do list' in query:
            tasks = list_todos(show_completed='completed' in query)
            speak("Here are your tasks:")
            speak(tasks)
            print(tasks)
        
        elif 'set reminder' in query or 'remind me' in query:
            speak("What would you like me to remind you about?")
            reminder_text = take_user_input()
            if reminder_text:  # Check if reminder_text is not empty
                speak("When should I remind you? Please provide date and time (YYYY-MM-DD HH:MM)")
                reminder_time = input("Enter date and time (YYYY-MM-DD HH:MM): ")
                result = add_reminder(reminder_text, reminder_time)
                speak(result)
            else:
                speak("I didn't catch what to remind you about. Please try again.")
        
        elif 'take note' in query or 'make note' in query:
            speak("What's the title of your note?")
            title = take_user_input()
            if title:  # Check if title is not empty
                speak("What's the content of your note?")
                content = take_user_input()
                if content:  # Check if content is not empty
                    result = add_note(title, content)
                    speak(result)
                else:
                    speak("I didn't catch the content. Please try again.")
            else:
                speak("I didn't catch the title. Please try again.")
        
        elif 'find note' in query:
            speak("What are you looking for in your notes?")
            search_term = take_user_input()
            if search_term:  # Check if search_term is not empty
                notes = find_note(search_term)
                if notes:
                    speak(f"I found {len(notes)} notes matching '{search_term}'")
                    for note in notes:
                        speak(f"Title: {note.get('title')}")
                        speak(f"Content: {note.get('content')}")
                        print(f"Title: {note.get('title')}")
                        print(f"Content: {note.get('content')}")
                        print("-" * 30)
                else:
                    speak(f"No notes found containing '{search_term}'")
            else:
                speak("I didn't catch what to search for. Please try again.")
        
        # Entertainment
        elif 'play music' in query or 'play song' in query:
            if 'play music' in query and query != 'play music':
                song = query.replace('play music', '').strip()
            elif 'play song' in query and query != 'play song':
                song = query.replace('play song', '').strip()
            else:
                speak("What song would you like to play?")
                song = take_user_input()
            
            if song:  # Check if song is not empty
                result = music_player.play(song)
                speak(result)
            else:
                speak("Playing a random song")
                result = music_player.play()
                speak(result)
        
        elif 'pause music' in query or 'pause song' in query:
            result = music_player.pause()
            speak(result)
        
        elif 'resume music' in query or 'resume song' in query:
            result = music_player.resume()
            speak(result)
        
        elif 'stop music' in query or 'stop song' in query:
            result = music_player.stop()
            speak(result)
        
        elif 'quote' in query or 'inspiration' in query:
            quote = get_random_quote()
            speak(f"{quote.get('content')} - {quote.get('author')}")
            print(f"{quote.get('content')} - {quote.get('author')}")
        
        elif 'riddle' in query:
            riddle = get_riddle()
            speak(f"Here's a riddle for you: {riddle.get('question')}")
            print(f"Riddle: {riddle.get('question')}")
            time.sleep(10)  # Give the user time to think
            speak(f"The answer is: {riddle.get('answer')}")
            print(f"Answer: {riddle.get('answer')}")
        
        elif 'tell me a joke' in query:
            joke_data = tell_joke()
            speak(joke_data.get('setup'))
            time.sleep(1.5)  # Pause for comedic effect
            speak(joke_data.get('punchline'))
            print(f"{joke_data.get('setup')}\n{joke_data.get('punchline')}")
        
        elif 'rock paper scissors' in query:
            speak("Let's play rock, paper, scissors. What's your choice?")
            choice = take_user_input()
            if choice:  # Check if choice is not empty
                result = play_rock_paper_scissors(choice)
                speak(result.get('message'))
                print(f"You chose: {result.get('player')}")
                print(f"I chose: {result.get('computer')}")
                print(f"Result: {result.get('message')}")
            else:
                speak("I didn't catch your choice. Please try again.")
        
        # Language tools
        elif 'translate' in query:
            speak("What would you like me to translate?")
            text_to_translate = take_user_input()
            if text_to_translate:  # Check if text_to_translate is not empty
                speak("To what language? For example, say 'spanish', 'french', etc.")
                target_language = take_user_input().lower()
                if target_language:  # Check if target_language is not empty
                    language_codes = {
                        'spanish': 'es', 'french': 'fr', 'german': 'de', 
                        'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 
                        'japanese': 'ja', 'korean': 'ko', 'chinese': 'zh-cn',
                        'arabic': 'ar', 'hindi': 'hi'
                    }
                    language_code = language_codes.get(target_language, target_language)
                    translation = translate_text(text_to_translate, language_code)
                    
                    if "error" in translation:
                        speak(f"Sorry, I encountered an error: {translation.get('error')}")
                    else:
                        source_lang = get_language_name(translation.get('source_language', 'unknown'))
                        target_lang = get_language_name(translation.get('target_language', 'unknown'))
                        speak(f"The text in {source_lang} translates to {target_lang} as: {translation.get('translated_text')}")
                        print(f"Original ({source_lang}): {translation.get('original_text')}")
                        print(f"Translation ({target_lang}): {translation.get('translated_text')}")
                else:
                    speak("I didn't catch the target language. Please try again.")
            else:
                speak("I didn't catch what to translate. Please try again.")
        
        elif 'what language is' in query:
            text = query.replace('what language is', '').strip()
            if not text:
                speak("What text would you like me to identify the language of?")
                text = take_user_input()
            
            if text:  # Check if text is not empty
                detection = detect_language(text)
                if "error" in detection:
                    speak(f"Sorry, I encountered an error: {detection.get('error')}")
                else:
                    language = get_language_name(detection.get('language', 'unknown'))
                    confidence = detection.get('confidence', 0) * 100
                    speak(f"That appears to be {language} with {confidence:.0f}% confidence.")
            else:
                speak("I didn't catch the text. Please try again.")
        
        elif 'speak this' in query or 'say this' in query:
            if 'speak this' in query:
                text = query.replace('speak this', '').strip()
            else:
                text = query.replace('say this', '').strip()
            
            if not text:
                speak("What would you like me to say?")
                text = take_user_input()
            
            if text:  # Check if text is not empty
                text_to_speech(text)
            else:
                speak("I didn't catch what to say. Please try again.")
        
        elif 'time' in query:
            current_time = datetime.now().strftime('%I:%M %p')
            speak(f"The current time is {current_time}")
        
        elif 'date' in query:
            current_date = datetime.now().strftime('%B %d, %Y')
            speak(f"Today is {current_date}")
        
        elif 'thank you' in query or 'thanks' in query:
            speak("You're welcome! Is there anything else I can help you with?")
        
        elif 'who are you' in query or 'what can you do' in query:
            speak(f"I am {BOTNAME}, your personal voice assistant. I can help you with various tasks like:")
            speak("Opening applications, searching the web, playing music, setting reminders, taking notes")
            speak("Getting information like weather, news, movies, and more")
            speak("I can also translate text, play games, tell jokes, and perform system operations")
            speak("Just ask me what you need!")
        
        else:
            speak("I'm not sure how to respond to that. Could you try a different command?")
    
    except Exception as e:
        logger.error(f"Error handling command '{query}': {str(e)}")
        speak("Sorry, I encountered an error while processing your request. Please try again.")

def listening_loop():
    """Main listening loop that runs in a separate thread"""
    global is_running, listening_event
    
    while is_running:
        if listening_event.is_set():
            query = take_user_input()
            if query:
                handle_command(query)
            
            # Check for reminders periodically
            check_reminders()
        
        # Sleep a short while to prevent CPU overuse
        time.sleep(0.1)

def start_listening_callback():
    """Callback for starting the listening process from GUI"""
    listening_event.set()
    if gui_app:
        gui_app.update_status("Listening active")

def stop_listening_callback():
    """Callback for stopping the listening process from GUI"""
    listening_event.clear()
    if gui_app:
        gui_app.update_status("Listening paused")

def exit_handler():
    """Handle graceful shutdown of the application"""
    global is_running
    is_running = False
    
    # Cleanup resources
    if music_player and music_player.playing:
        music_player.stop()
    
    logger.info("Application shutting down")

def launch_gui():
    """Launch the GUI interface"""
    global gui_root, gui_app
    
    gui_root, gui_app = create_gui(start_listening_callback, stop_listening_callback)
    
    # Set up GUI close event handler
    gui_root.protocol("WM_DELETE_WINDOW", exit_handler)
    
    # Start the main listening thread
    global listening_thread
    listening_thread = threading.Thread(target=listening_loop, daemon=True)
    listening_thread.start()
    
    # Welcome message
    speak(f"Welcome to {BOTNAME}. I'm ready to assist you.")
    
    # Start GUI main loop
    gui_root.mainloop()

def run_terminal_mode():
    """Run the assistant in terminal mode without GUI"""
    greet_user()
    
    global listening_thread
    # Set listening event initially active
    listening_event.set()
    
    # Start the listening thread
    listening_thread = threading.Thread(target=listening_loop, daemon=True)
    listening_thread.start()
    
    try:
        # Keep the main thread alive
        while is_running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        exit_handler()

# Main function to run the voice assistant
def main():
    """Main function to run the voice assistant"""
    logger.info("Starting Voice Assistant")
    
    try:
        if not initialize_system():
            print("Error initializing system. Check logs for details.")
            return
        
        # Launch GUI if enabled, otherwise run in terminal mode
        if USE_GUI:
            launch_gui()
        else:
            run_terminal_mode()
            
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

# Run the main function when this script is executed
if __name__ == "__main__":
    main()