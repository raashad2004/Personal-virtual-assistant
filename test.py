#!/usr/bin/env python3
"""
Voice Assistant Dependency Test

This script checks for common dependency issues and helps with debugging.
"""

import os
import sys
import platform
import time
import importlib.util
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
    logger = logging.getLogger("TestSuite")
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
    log_file = os.path.join(logs_dir, f"test_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=7  # Keep logs for a week
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.INFO)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

# Print header
print("\n" + "=" * 50)
print("         Voice Assistant Dependency Test")
print("=" * 50)
logger.info("Starting dependency test")

# Detect platform
platform_info = f"{platform.system()}-{platform.release()}-{platform.version()}"
print(f"Platform: {platform_info}")
logger.info(f"Platform: {platform_info}")

print("\n" + "=" * 50)

# Test module imports
def test_module_imports():
    modules_to_test = [
        "pyttsx3",
        "speech_recognition",
        "pygame",
        "requests",
        "tkinter",
        "PIL.Image",
        "decouple",
        "dotenv",
        "googletrans",
        "psutil"
    ]
    
    logger.info("Testing module imports")
    print("=" * 50)
    
    results = {}
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            file_path = getattr(module, "__file__", "Unknown location")
            print(f"✓ {module_name} - Successfully imported from {file_path}")
            logger.info(f"Module {module_name} successfully imported from {file_path}")
            results[module_name] = {"status": "success", "path": file_path}
        except ImportError as e:
            print(f"✗ {module_name} - Import error: {str(e)}")
            logger.warning(f"Failed to import {module_name}: {str(e)}")
            results[module_name] = {"status": "error", "message": str(e)}
    
    return results

# Test directories
def test_directories():
    directories_to_test = [
        "data",
        "audio",
        "screenshots",
        "music",
        "assets",
        "Functions"
    ]
    
    logger.info("Testing directories")
    print("\n" + "=" * 50)
    print("               Testing Directories")
    print("=" * 50)
    
    results = {}
    
    for directory in directories_to_test:
        if os.path.exists(directory):
            if os.access(directory, os.W_OK):
                print(f"✓ {directory} - Exists and is writable")
                logger.info(f"Directory {directory} exists and is writable")
                results[directory] = {"status": "success"}
            else:
                print(f"✗ {directory} - Exists but is not writable")
                logger.warning(f"Directory {directory} exists but is not writable")
                results[directory] = {"status": "warning", "message": "Not writable"}
        else:
            print(f"✗ {directory} - Does not exist")
            logger.warning(f"Directory {directory} does not exist")
            results[directory] = {"status": "error", "message": "Does not exist"}
            try:
                os.makedirs(directory)
                print(f"  Created {directory} directory")
                logger.info(f"Created directory {directory}")
                results[directory]["status"] = "created"
            except Exception as e:
                print(f"  Failed to create directory: {str(e)}")
                logger.error(f"Failed to create directory {directory}: {str(e)}")
    
    return results

# Test audio components
def test_audio():
    logger.info("Testing audio components")
    print("\n" + "=" * 50)
    print("                  Testing Audio")
    print("=" * 50)
    
    results = {}
    
    # Test pygame audio
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.quit()
        print("✓ Pygame audio initialized successfully")
        logger.info("Pygame audio initialized successfully")
        results["pygame"] = {"status": "success"}
    except Exception as e:
        print(f"✗ pygame audio error: {str(e)}")
        logger.warning(f"Pygame audio error: {str(e)}")
        results["pygame"] = {"status": "error", "message": str(e)}
    
    # Test speech recognition
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        print("✓ Speech recognition initialized successfully")
        logger.info("Speech recognition initialized successfully")
        results["speech_recognition"] = {"status": "success"}
    except Exception as e:
        print(f"✗ Speech recognition error: {str(e)}")
        logger.warning(f"Speech recognition error: {str(e)}")
        results["speech_recognition"] = {"status": "error", "message": str(e)}
    
    return results

# Test network connectivity to required services
def test_network():
    logger.info("Testing network connectivity")
    print("\n" + "=" * 50)
    print("           Testing Network Connectivity")
    print("=" * 50)
    
    services_to_test = [
        {"name": "Google (Search, Speech Recognition)", "url": "https://www.google.com"},
        {"name": "OpenWeatherMap API", "url": "https://api.openweathermap.org"},
        {"name": "NewsAPI", "url": "https://newsapi.org"},
        {"name": "TMDB (Movie Database)", "url": "https://api.themoviedb.org/3/movie/popular"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/w/api.php"}
    ]
    
    results = {}
    
    try:
        import requests
        for service in services_to_test:
            try:
                response = requests.get(service["url"], timeout=5)
                if response.status_code < 400:
                    print(f"✓ {service['name']} - Connected successfully")
                    logger.info(f"Connected successfully to {service['name']}")
                    results[service["name"]] = {"status": "success", "code": response.status_code}
                else:
                    print(f"✗ {service['name']} - Connection failed: HTTP {response.status_code}")
                    logger.warning(f"Connection to {service['name']} failed: HTTP {response.status_code}")
                    results[service["name"]] = {"status": "error", "code": response.status_code}
            except Exception as e:
                print(f"✗ {service['name']} - Connection failed: {str(e)}")
                logger.warning(f"Connection to {service['name']} failed: {str(e)}")
                results[service["name"]] = {"status": "error", "message": str(e)}
    except ImportError:
        print("✗ Requests module not available, skipping network tests")
        logger.warning("Requests module not available, skipping network tests")
        results["status"] = "skipped"
    
    return results

# Run all tests
def run_tests():
    logger.info("Running all tests")
    results = {}
    
    # Test module imports
    results["modules"] = test_module_imports()
    
    # Test directories
    results["directories"] = test_directories()
    
    # Test audio
    results["audio"] = test_audio()
    
    # Test network connectivity
    results["network"] = test_network()
    
    # Print summary
    print("\n" + "=" * 50)
    print("                  Test Complete")
    print("=" * 50)
    print("If any tests failed, please install the missing dependencies or troubleshoot the issues.")
    print("For help, run: pip install -r requirements.txt")
    
    logger.info("Test complete")
    return results

if __name__ == "__main__":
    results = run_tests() 