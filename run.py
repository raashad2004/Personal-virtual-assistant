#!/usr/bin/env python3
"""
Voice Assistant Launcher

This script checks for dependencies and prerequisites before
launching the main application.
"""

import os
import sys
import platform
import subprocess
import importlib.util
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import time

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configure logging with enhanced features
def setup_logging():
    # Create logger
    logger = logging.getLogger("Launcher")
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
    log_file = os.path.join(logs_dir, f"launcher_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=30  # Keep logs for a month
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.INFO)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

def clean_log_directory():
    """Clean up old log files at startup"""
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        logger.info(f"Created logs directory: {logs_dir}")
        return

    # Don't attempt cleanup if logs are stored in backup
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup_logs')
    if os.path.exists(backup_dir):
        return

    try:
        # Remove old log files
        current_date = datetime.now().strftime('%Y%m%d')
        log_count = 0
        
        for file in os.listdir(logs_dir):
            if file.endswith('.log'):
                # Keep only current day's logs
                if current_date not in file:
                    file_path = os.path.join(logs_dir, file)
                    os.remove(file_path)
                    log_count += 1
        
        if log_count > 0:
            logger.info(f"Cleaned up {log_count} old log files")
    except Exception as e:
        logger.error(f"Error cleaning log directory: {e}")

# Clean old logs at startup before performing other operations
clean_log_directory()

logger.info("=" * 50)
logger.info("             Voice Assistant Launcher")
logger.info("=" * 50)
logger.info("Starting launcher checks")

# Add current directory to path to ensure modules can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add Functions directory to path
functions_dir = os.path.join(current_dir, 'Functions')
if functions_dir not in sys.path:
    sys.path.insert(0, functions_dir)

def check_python_version():
    """Check if the Python version is compatible (3.8+)."""
    logger.info(f"Checking Python version: {platform.python_version()}")
    major, minor, _ = platform.python_version_tuple()
    
    if int(major) < 3 or (int(major) == 3 and int(minor) < 8):
        logger.error(f"Python version {platform.python_version()} is not supported. Please use Python 3.8+")
        print(f"Your Python version ({platform.python_version()}) is not supported.")
        print("This application requires Python 3.8 or higher.")
        return False
    
    # Handle Python 3.12+ with special instructions
    if int(major) == 3 and int(minor) >= 12:
        logger.warning(f"Python {platform.python_version()} detected - additional compatibility measures enabled")
        print(f"Note: You're using Python {platform.python_version()}.")
        print("Some packages may require special handling with this Python version.")
        
        # Patch for pkgutil.ImpImporter issue in Python 3.12+
        try:
            import pkgutil
            if not hasattr(pkgutil, 'ImpImporter'):
                import types
                logger.info("Applying pkgutil.ImpImporter patch for Python 3.12+")
                # Create a dummy ImpImporter to satisfy older packages
                pkgutil.ImpImporter = types.SimpleNamespace
        except Exception as e:
            logger.error(f"Failed to apply Python 3.12+ compatibility patch: {e}")
    
    logger.info(f"Python version check passed: {platform.python_version()}")
    return True

def check_module_exists(module_name):
    """Check if a module can be imported."""
    # Handle version requirements (like setuptools>=68.0.0)
    if '>=' in module_name or '<=' in module_name or '==' in module_name:
        # Extract base module name before version specification
        base_module = module_name.split('>=')[0].split('<=')[0].split('==')[0].strip()
        spec = importlib.util.find_spec(base_module)
        
        if spec:
            # For modules with version requirements, we need to check the version
            try:
                mod = importlib.import_module(base_module)
                if hasattr(mod, '__version__'):
                    current_version = mod.__version__
                    # This is a simplified check - in a real application you would
                    # use packaging.version to properly compare versions
                    logger.info(f"Found {base_module} version {current_version}")
                return True
            except Exception as e:
                logger.error(f"Error checking {base_module} version: {e}")
                return False
    else:
        # Standard import check
        spec = importlib.util.find_spec(module_name)
    
    return spec is not None

def check_requirements():
    """Check for required packages and offer to install missing ones."""
    required_packages = [
        "python-decouple",
        "pyttsx3", 
        "SpeechRecognition",
        "pygame",
        "Pillow",
        "requests"
    ]
    
    optional_packages = [
        "psutil",
        "googletrans",
        "pyautogui",
        "gtts",
        "python-dotenv"
    ]
    
    # Compatibility patches for Python 3.12+
    major, minor, _ = platform.python_version_tuple()
    if int(major) == 3 and int(minor) >= 12:
        logger.info("Applying Python 3.12+ specific package requirements")
        # Use the fork for Python 3.12
        if "pywhatkit" in required_packages:
            required_packages.remove("pywhatkit")
            required_packages.append("pywhatkit-fork")
        elif "pywhatkit" in optional_packages:
            optional_packages.remove("pywhatkit")
            optional_packages.append("pywhatkit-fork")
        
        # Make sure setuptools is up to date
        optional_packages.append("setuptools>=68.0.0")
    
    missing_required = []
    missing_optional = []
    
    logger.info("Checking required packages...")
    for package in required_packages:
        module_name = package.lower().replace('-', '_')
        if not check_module_exists(module_name):
            missing_required.append(package)
    
    logger.info("Checking optional packages...")
    for package in optional_packages:
        module_name = package.lower().replace('-', '_')
        if not check_module_exists(module_name):
            missing_optional.append(package)
    
    if missing_required:
        logger.warning(f"Missing required packages: {', '.join(missing_required)}")
        print(f"Missing required packages: {', '.join(missing_required)}")
        install = input("Do you want to install these packages now? (y/n): ").lower() == 'y'
        
        if install:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_required)
                logger.info("Successfully installed required packages")
                print("Required packages installed successfully.")
            except Exception as e:
                logger.error(f"Error installing packages: {e}")
                print(f"Error installing packages: {e}")
                return False
        else:
            logger.warning("User declined to install required packages")
            print("Required packages are needed for the application to function properly.")
            return False
    
    if missing_optional:
        logger.info(f"Missing optional packages: {', '.join(missing_optional)}")
        print(f"Some optional packages are missing: {', '.join(missing_optional)}")
        print("These are not required, but some features may be limited.")
        install = input("Do you want to install these optional packages? (y/n): ").lower() == 'y'
        
        if install:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_optional)
                logger.info("Successfully installed optional packages")
                print("Optional packages installed successfully.")
            except Exception as e:
                logger.error(f"Error installing optional packages: {e}")
                print(f"Error installing optional packages: {e}")
    
    return True

def check_platform():
    """Check operating system compatibility."""
    system = platform.system()
    logger.info(f"Detected operating system: {system}")
    
    if system == "Windows":
        # Check Windows version
        version = platform.version()
        logger.info(f"Windows version: {version}")
        print(f"Running on Windows {version}")
    
    elif system == "Darwin":  # macOS
        logger.info("Running on macOS")
        print("Running on macOS.")
        print("Note: Some Windows-specific features may not work correctly.")
    
    elif system == "Linux":
        logger.info(f"Running on Linux: {platform.platform()}")
        print(f"Running on Linux: {platform.platform()}")
        print("Note: Some Windows-specific features may not work correctly.")
    
    else:
        logger.warning(f"Unsupported platform: {system}")
        print(f"Unsupported platform: {system}")
        print("This application is primarily designed for Windows.")
        print("Some features may not work as expected.")
    
    return True

def check_microphone():
    """Check if a microphone is available."""
    logger.info("Checking microphone availability...")
    
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                logger.info("Microphone initialized successfully")
                print("Microphone check: PASSED")
                return True
        except Exception as e:
            logger.error(f"Microphone error: {e}")
            print("Microphone check: FAILED")
            print(f"Error: {e}")
            print("Please check your microphone connection and settings.")
            print("The application will still run, but voice commands won't work.")
            return False
            
    except ImportError as e:
        logger.error(f"Failed to import speech_recognition: {e}")
        print("Could not check microphone due to missing speech_recognition package.")
        return False

def check_directories():
    """Check if required directories exist and create them if they don't."""
    required_dirs = ["data", "audio", "screenshots", "music", "assets", "Functions"]
    
    logger.info("Checking required directories...")
    for directory in required_dirs:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                print(f"Error creating directory {directory}: {e}")
                return False
    
    # Check for essential data files
    data_files = {
        "data/todos.json": "{}",
        "data/notes.json": "{}",
        "data/reminders.json": "[]"
    }
    
    for file_path, default_content in data_files.items():
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w') as f:
                    f.write(default_content)
                logger.info(f"Created data file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to create file {file_path}: {e}")
                print(f"Error creating file {file_path}: {e}")
    
    # Check for .env file
    if not os.path.exists(".env"):
        logger.warning(".env file not found")
        print("Warning: .env file not found.")
        print("Some features requiring API keys may not work.")
        print("Consider creating a .env file with your API keys.")
    
    return True

def check_modules():
    """Check if the required module files exist."""
    required_modules = [
        "main.py",
        "Functions/init.py",
        "Functions/online_ops.py",
        "Functions/task_manager.py",
        "Functions/system_utils.py", 
        "Functions/entertainment.py",
        "Functions/language_tools.py"
    ]
    
    logger.info("Checking required module files...")
    missing_modules = []
    
    for module in required_modules:
        if not os.path.exists(module):
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Missing required module files: {', '.join(missing_modules)}")
        print(f"Missing required module files: {', '.join(missing_modules)}")
        print("The application may not function correctly.")
        return False
    
    return True

def main():
    """Main function to check prerequisites and run the application."""
    print("=" * 50)
    print("Voice Assistant Launcher".center(50))
    print("=" * 50)
    
    logger.info("Starting launcher checks")
    
    # Run checks
    checks = [
        ("Python Version", check_python_version),
        ("Required Directories", check_directories),
        ("Module Files", check_modules),
        ("System Platform", check_platform),
        ("Required Packages", check_requirements),
        ("Microphone", check_microphone)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            logger.error(f"Error during {name} check: {e}")
            print(f"Error during {name} check: {e}")
            all_passed = False
    
    if not all_passed:
        logger.warning("Some checks failed. Application may not function correctly.")
        print("\nWarning: Some checks failed. The application may not function correctly.")
        proceed = input("Do you want to proceed anyway? (y/n): ").lower() == 'y'
        if not proceed:
            logger.info("User chose not to proceed after failed checks")
            print("Exiting.")
            return
    
    # Run the main application
    print("\nLaunching Voice Assistant...")
    logger.info("All checks completed, launching main application")
    
    try:
        # Initialize environment for loading modules
        if 'main' in sys.modules:
            del sys.modules['main']
        
        # Import and run the main module
        import main
        if hasattr(main, 'main'):
            main.main()
        else:
            # Try to infer how to run the main module
            for attr_name in dir(main):
                attr = getattr(main, attr_name)
                if callable(attr) and attr_name.lower() in ('main', 'run', 'start'):
                    attr()
                    break
            else:
                logger.warning("No main function found in main.py")
                print("No main function found in main.py")
                print("The application may not have started correctly.")
    except Exception as e:
        logger.error(f"Error running main application: {e}")
        print(f"Error running main application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 