import os
import psutil
import platform
import subprocess
import datetime
import pyautogui
import time
from typing import Dict, Tuple, List, Any

def get_system_info() -> Dict[str, Any]:
    """Get system information including OS, CPU, memory and disk usage"""
    try:
        system_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_total": round(psutil.virtual_memory().total / (1024 ** 3), 2),  # GB
            "memory_available": round(psutil.virtual_memory().available / (1024 ** 3), 2),  # GB
            "memory_percent": psutil.virtual_memory().percent,
            "disk_total": round(psutil.disk_usage('/').total / (1024 ** 3), 2),  # GB
            "disk_free": round(psutil.disk_usage('/').free / (1024 ** 3), 2),  # GB
            "disk_percent": psutil.disk_usage('/').percent,
            "boot_time": datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }
        return system_info
    except Exception as e:
        return {"error": str(e)}

def get_battery_info() -> Dict[str, Any]:
    """Get battery information if available"""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "time_left": str(datetime.timedelta(seconds=battery.secsleft)) if battery.secsleft > 0 else "Unknown"
            }
        else:
            return {"error": "No battery detected"}
    except Exception as e:
        return {"error": str(e)}

def get_running_processes(limit: int = 10) -> List[Dict[str, Any]]:
    """Get information about running processes"""
    try:
        processes = []
        for proc in sorted(psutil.process_iter(['pid', 'name', 'username', 'memory_percent']), 
                          key=lambda x: x.info['memory_percent'], reverse=True)[:limit]:
            try:
                process_info = proc.info
                process_info['cpu_percent'] = proc.cpu_percent(interval=0.1)
                processes.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes
    except Exception as e:
        return [{"error": str(e)}]

def take_screenshot(filename: str = None) -> str:
    """Take a screenshot and save it to a file"""
    try:
        if not filename:
            now = datetime.datetime.now()
            filename = f"screenshot_{now.strftime('%Y%m%d_%H%M%S')}.png"
        
        if not os.path.isdir("screenshots"):
            os.makedirs("screenshots")
        
        filepath = os.path.join("screenshots", filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        return f"Screenshot saved to {filepath}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

def shutdown_system(delay: int = 0) -> str:
    """Shutdown the system after a specified delay in seconds"""
    try:
        if platform.system() == "Windows":
            os.system(f"shutdown /s /t {delay}")
        elif platform.system() == "Linux" or platform.system() == "Darwin":
            os.system(f"shutdown -h +{delay//60}")
        return f"System will shutdown in {delay} seconds"
    except Exception as e:
        return f"Error shutting down: {str(e)}"

def restart_system(delay: int = 0) -> str:
    """Restart the system after a specified delay in seconds"""
    try:
        if platform.system() == "Windows":
            os.system(f"shutdown /r /t {delay}")
        elif platform.system() == "Linux" or platform.system() == "Darwin":
            os.system(f"shutdown -r +{delay//60}")
        return f"System will restart in {delay} seconds"
    except Exception as e:
        return f"Error restarting: {str(e)}"

def cancel_shutdown() -> str:
    """Cancel a scheduled shutdown"""
    try:
        if platform.system() == "Windows":
            os.system("shutdown /a")
        elif platform.system() == "Linux" or platform.system() == "Darwin":
            os.system("shutdown -c")
        return "Scheduled shutdown has been cancelled"
    except Exception as e:
        return f"Error cancelling shutdown: {str(e)}"

def lock_screen() -> str:
    """Lock the computer screen"""
    try:
        if platform.system() == "Windows":
            subprocess.call('rundll32.exe user32.dll,LockWorkStation')
        elif platform.system() == "Darwin":  # macOS
            subprocess.call('pmset displaysleepnow', shell=True)
        elif platform.system() == "Linux":
            subprocess.call('gnome-screensaver-command --lock', shell=True)
        return "Screen locked"
    except Exception as e:
        return f"Error locking screen: {str(e)}" 