import sys
import os
import shutil
import subprocess
from pathlib import Path

def create_windows_executable():
    """
    Create a Windows executable using PyInstaller
    """
    print("Starting Windows Executable Creation Process...")
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller is installed.")
    except ImportError:
        print("PyInstaller is not installed. Installing now...")
        subprocess.call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")
    
    # Create assets directory if it doesn't exist
    if not os.path.exists("assets"):
        os.makedirs("assets")
        print("Created assets directory")
    
    # Try to create an icon if not exists
    icon_path = "assets/icon.ico"
    if not os.path.exists(icon_path):
        try:
            # First try to use our icon creator
            if os.path.exists("create_icon.py"):
                print("Running icon creator script...")
                subprocess.call([sys.executable, "create_icon.py"])
            
            # If still no icon, create a simple placeholder
            if not os.path.exists(icon_path):
                from PIL import Image, ImageDraw
                
                # Create a simple icon
                icon_size = (256, 256)
                icon_bg = (52, 73, 94)  # Dark blue
                icon_fg = (52, 152, 219)  # Light blue
                
                img = Image.new('RGBA', icon_size, icon_bg)
                draw = ImageDraw.Draw(img)
                
                # Draw a simple microphone icon
                center_x, center_y = icon_size[0] // 2, icon_size[1] // 2
                radius = min(center_x, center_y) - 40
                
                # Draw circle
                draw.ellipse((center_x - radius, center_y - radius, 
                            center_x + radius, center_y + radius), 
                            fill=icon_fg)
                
                # Draw microphone stem
                stem_width = radius // 2
                stem_height = radius * 1.5
                
                draw.rectangle((center_x - stem_width // 2, center_y - stem_height // 2,
                            center_x + stem_width // 2, center_y + stem_height // 2),
                            fill=icon_bg)
                
                # Save as ICO file
                img.save(icon_path, format="ICO")
                print(f"Created placeholder icon at {icon_path}")
        except ImportError:
            print("PIL not available, skipping icon creation")
    
    # PyInstaller command
    pyinstaller_command = [
        "pyinstaller",
        "--name=VoiceAssistant",
        "--onefile",
        "--windowed",
        f"--icon={icon_path}",
        "--add-data=assets;assets",
        "--hidden-import=pyttsx3.drivers",
        "--hidden-import=pyttsx3.drivers.sapi5",
        "--hidden-import=pygame",
        "--hidden-import=PIL",
        "--hidden-import=speech_recognition",
        "run.py"  # Use run.py instead of main.py
    ]
    
    # Run PyInstaller
    print("Running PyInstaller...")
    subprocess.call(pyinstaller_command)
    
    # Copy necessary directories and files to the dist folder
    dist_dir = Path("dist/VoiceAssistant")
    if not dist_dir.exists():
        dist_dir = Path("dist")  # Fallback to dist folder directly for onefile mode
    
    # Create required directories in the distribution
    for directory in ["Functions", "data", "music", "audio", "screenshots"]:
        dir_path = dist_dir / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"Created {directory} directory in distribution")
    
    # Copy necessary files to the Functions directory
    function_files_to_copy = [
        ("Functions/__init__.py", "Functions/__init__.py"),
        ("Functions/_init_.py", "Functions/_init_.py"),
        ("Functions/online_ops.py", "Functions/online_ops.py"),
        ("Functions/task_manager.py", "Functions/task_manager.py"),
        ("Functions/system_utils.py", "Functions/system_utils.py"),
        ("Functions/entertainment.py", "Functions/entertainment.py"),
        ("Functions/language_tools.py", "Functions/language_tools.py")
    ]
    
    # Copy files to distribution
    for src, dest in function_files_to_copy:
        src_path = Path(src)
        dest_path = dist_dir / dest
        
        if src_path.exists():
            if not dest_path.parent.exists():
                dest_path.parent.mkdir(parents=True)
            shutil.copy2(src_path, dest_path)
            print(f"Copied {src} to {dest}")
        else:
            print(f"Warning: Source file {src} does not exist, skipping")
    
    # Copy other essential files
    other_files_to_copy = [
        "main.py",
        "utils.py",
        "gui.py",
        "run.py",
        "README.md"
    ]
    
    for file in other_files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir)
            print(f"Copied {file} to distribution")
    
    # Copy .env file (with placeholders instead of real credentials)
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        # Replace actual credentials with placeholders
        env_content = env_content.replace("your_openweather_api_key", "ENTER_YOUR_API_KEY")
        env_content = env_content.replace("your_newsapi_key", "ENTER_YOUR_API_KEY")
        env_content = env_content.replace("your_tmdb_api_key", "ENTER_YOUR_API_KEY")
        env_content = env_content.replace("your_email@gmail.com", "ENTER_YOUR_EMAIL")
        env_content = env_content.replace("your_email_password_or_app_password", "ENTER_YOUR_PASSWORD")
        
        with open(dist_dir / ".env", 'w') as f:
            f.write(env_content)
        print("Created .env file in distribution with placeholders")
    
    # Create a README.txt file with instructions
    readme_content = """
Voice Assistant - Windows Application
====================================

Thank you for using our Voice Assistant!

Setup Instructions:
1. Before running the application, please edit the .env file in this folder to add your API keys and credentials.
2. Make sure your microphone is properly connected and configured on your Windows system.
3. Run VoiceAssistant.exe to start the application.

Usage Tips:
- Click "Start Listening" to begin voice interaction
- Say "help" or "what can you do" to see available commands
- You can add your own music files to the 'music' folder

Troubleshooting:
- If you encounter any issues with dependencies, run the application from the command line to see error messages.
- For microphone issues, ensure your microphone is set as the default recording device in Windows settings.
- API-related features require valid API keys in the .env file.

For more information, visit: https://github.com/your-username/voice-assistant

Enjoy using your Voice Assistant!
"""
    
    with open(dist_dir / "README.txt", 'w') as f:
        f.write(readme_content)
    print("Created README.txt in distribution")
    
    # Create a requirements.txt file in the distribution
    if os.path.exists("requirements.txt"):
        shutil.copy2("requirements.txt", dist_dir / "requirements.txt")
        print("Copied requirements.txt to distribution")
    
    print("\nWindows executable creation completed!")
    print(f"Your executable is located at: {dist_dir.absolute()}")
    print("Don't forget to edit the .env file with your API keys before distributing.")

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        create_windows_executable()
    else:
        print("This script is designed to create Windows executables. Please run on a Windows system.")
        sys.exit(1) 