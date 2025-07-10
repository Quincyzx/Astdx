import os
import json
import requests
import subprocess
import shutil
from datetime import datetime

class MacroUtils:
    """Utility functions for macro operations"""
    
    @staticmethod
    def ensure_macros_directory():
        """Ensure the macros directory exists"""
        if not os.path.exists("macros"):
            os.makedirs("macros")
    
    @staticmethod
    def validate_macro_file(filepath):
        """Validate a macro JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Check required fields
            if 'actions' not in data:
                return False, "Missing 'actions' field"
            
            if not isinstance(data['actions'], list):
                return False, "'actions' must be a list"
            
            # Validate each action
            for i, action in enumerate(data['actions']):
                if not isinstance(action, dict):
                    return False, f"Action {i} is not a dictionary"
                
                if 'type' not in action:
                    return False, f"Action {i} missing 'type' field"
                
                if 'timestamp' not in action:
                    return False, f"Action {i} missing 'timestamp' field"
                
                # Validate action-specific fields
                action_type = action['type']
                if action_type == 'click':
                    if 'x' not in action or 'y' not in action:
                        return False, f"Click action {i} missing coordinates"
                    if 'button' not in action:
                        return False, f"Click action {i} missing button field"
                elif action_type == 'key_press':
                    if 'key' not in action:
                        return False, f"Key press action {i} missing key field"
                elif action_type == 'wait':
                    if 'duration' not in action:
                        return False, f"Wait action {i} missing duration field"
            
            return True, "Valid macro file"
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"Error validating file: {str(e)}"
    
    @staticmethod
    def get_macro_info(filepath):
        """Get information about a macro file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            info = {
                'name': data.get('name', 'Unknown'),
                'created': data.get('created', 'Unknown'),
                'actions_count': len(data.get('actions', [])),
                'total_duration': data.get('total_duration', 0),
                'file_size': os.path.getsize(filepath)
            }
            
            return info
            
        except Exception as e:
            return None
    
    @staticmethod
    def find_autohotkey_executable():
        """Find AutoHotkey executable on the system"""
        ahk_paths = [
            r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
            r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
            r"C:\AutoHotkey\AutoHotkey.exe",
            "autohotkey.exe",
            "ahk.exe"
        ]
        
        for path in ahk_paths:
            if os.path.exists(path):
                return path
            else:
                # Try to find it using shutil.which
                try:
                    found_path = shutil.which(path)
                    if found_path:
                        return found_path
                except:
                    continue
        return None
    
    @staticmethod
    def download_file_from_url(url, local_path, timeout=30):
        """Download a file from URL to local path"""
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            return True, "File downloaded successfully"
            
        except requests.RequestException as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Error downloading file: {str(e)}"
    
    @staticmethod
    def execute_ahk_script(ahk_exe_path, script_path, macro_path, timeout=300):
        """Execute an AutoHotkey script with a macro file"""
        try:
            cmd = [ahk_exe_path, script_path, macro_path]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return True, "Script executed successfully"
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, f"Script execution failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Script execution timed out"
        except Exception as e:
            return False, f"Error executing script: {str(e)}"
    
    @staticmethod
    def clean_filename(filename):
        """Clean a filename to make it safe for filesystem"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        filename = filename.strip('. ')
        
        # Ensure filename is not empty
        if not filename:
            filename = "macro"
        
        return filename
    
    @staticmethod
    def backup_macro(macro_path):
        """Create a backup of a macro file"""
        try:
            backup_dir = "macros/backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            filename = os.path.basename(macro_path)
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            shutil.copy2(macro_path, backup_path)
            return True, backup_path
            
        except Exception as e:
            return False, f"Error creating backup: {str(e)}"
    
    @staticmethod
    def get_system_info():
        """Get system information for debugging"""
        info = {
            'os': os.name,
            'python_version': __import__('sys').version,
            'working_directory': os.getcwd(),
            'autohotkey_found': MacroUtils.find_autohotkey_executable() is not None
        }
        
        return info

class LogManager:
    """Simple logging manager for macro operations"""
    
    def __init__(self, log_file="macro_operations.log"):
        self.log_file = log_file
    
    def log(self, message, level="INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Failed to write to log file: {e}")
    
    def info(self, message):
        self.log(message, "INFO")
    
    def warning(self, message):
        self.log(message, "WARNING")
    
    def error(self, message):
        self.log(message, "ERROR")
    
    def debug(self, message):
        self.log(message, "DEBUG")
