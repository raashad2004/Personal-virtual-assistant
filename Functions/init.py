import os
import subprocess as sp
import platform
import sys

app_paths = {
    "notepad": r"C:\\Program Files\\Notepad++\\notepad++.exe",
    "discord": r"C:\\Users\\ashut\\AppData\\Local\\Discord\\app-1.0.9003\\Discord.exe",
    "calculator": r"C:\\Windows\\System32\\calc.exe"
}

# Update paths based on OS
def update_app_paths():
    global app_paths
    
    system = platform.system()
    
    if system == "Windows":
        # Check if Notepad++ exists, otherwise use default Notepad
        if not os.path.exists(app_paths["notepad"]):
            app_paths["notepad"] = r"C:\\Windows\\System32\\notepad.exe"
        
        # Try to find Discord in standard locations
        discord_paths = [
            r"C:\\Users\\%s\\AppData\\Local\\Discord\\app-*\\Discord.exe" % os.getenv("USERNAME"),
            r"C:\\Users\\%s\\AppData\\Roaming\\Discord\\*\\Discord.exe" % os.getenv("USERNAME")
        ]
        
        for path_pattern in discord_paths:
            import glob
            matches = glob.glob(path_pattern)
            if matches:
                app_paths["discord"] = matches[0]
                break
    
    elif system == "Darwin":  # macOS
        app_paths = {
            "notepad": "TextEdit",
            "discord": "Discord",
            "calculator": "Calculator"
        }
    
    elif system == "Linux":
        app_paths = {
            "notepad": "gedit",
            "discord": "discord",
            "calculator": "gnome-calculator"
        }

# Update paths on module import
update_app_paths()

def launch_notepad():
    """Launch notepad or a text editor"""
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(app_paths["notepad"])
        elif system == "Darwin":  # macOS
            sp.run(["open", "-a", app_paths["notepad"]])
        else:  # Linux
            sp.Popen([app_paths["notepad"]])
        return True
    except Exception as e:
        print(f"Error launching notepad: {str(e)}")
        return False

def launch_discord():
    """Launch Discord application"""
    try:
        system = platform.system()
        if system == "Windows":
            if os.path.exists(app_paths["discord"]):
                os.startfile(app_paths["discord"])
            else:
                print("Discord application not found")
        elif system == "Darwin":  # macOS
            sp.run(["open", "-a", app_paths["discord"]])
        else:  # Linux
            sp.Popen([app_paths["discord"]])
        return True
    except Exception as e:
        print(f"Error launching Discord: {str(e)}")
        return False

def open_command_prompt():
    """Open command prompt or terminal"""
    try:
        system = platform.system()
        if system == "Windows":
            os.system("start cmd")
        elif system == "Darwin":  # macOS
            sp.run(["open", "-a", "Terminal"])
        else:  # Linux
            sp.Popen(["gnome-terminal"])
        return True
    except Exception as e:
        print(f"Error opening command prompt: {str(e)}")
        return False

def activate_camera():
    """Activate camera application"""
    try:
        system = platform.system()
        if system == "Windows":
            sp.run("start microsoft.windows.camera:", shell=True)
        elif system == "Darwin":  # macOS
            sp.run(["open", "-a", "Photo Booth"])
        else:  # Linux
            sp.Popen(["cheese"])
        return True
    except Exception as e:
        print(f"Error activating camera: {str(e)}")
        return False

def launch_calculator():
    """Launch calculator application"""
    try:
        system = platform.system()
        if system == "Windows":
            sp.Popen(app_paths["calculator"])
        elif system == "Darwin":  # macOS
            sp.run(["open", "-a", app_paths["calculator"]])
        else:  # Linux
            sp.Popen([app_paths["calculator"]])
        return True
    except Exception as e:
        print(f"Error launching calculator: {str(e)}")
        return False 