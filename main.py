import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import subprocess
import requests
import threading
from datetime import datetime
import tempfile
import shutil

class MacroRunner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Macro Runner - ASTDX")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # GitHub URL for AHK script
        self.ahk_script_url = "https://raw.githubusercontent.com/Quincyzx/Astdx/main/astdx_macro_runner.ahk"
        
        # Create macros directory if it doesn't exist
        if not os.path.exists("macros"):
            os.makedirs("macros")
        
        # AutoHotkey executable paths (common locations)
        self.ahk_paths = [
            r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
            r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
            r"C:\AutoHotkey\AutoHotkey.exe",
            "autohotkey.exe",  # If in PATH
            "ahk.exe"  # Alternative name
        ]
        
        self.setup_ui()
        self.load_macros()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Macro Runner", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Macro selection frame
        selection_frame = tk.Frame(main_frame)
        selection_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Macro list label
        list_label = tk.Label(selection_frame, text="Available Macros:", font=("Arial", 12, "bold"))
        list_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Macro listbox with scrollbar
        listbox_frame = tk.Frame(selection_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.macro_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10)
        )
        self.macro_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.macro_listbox.yview)
        
        # Bind double-click to run macro
        self.macro_listbox.bind('<Double-1>', lambda e: self.run_selected_macro())
        
        # Macro info frame
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.info_label = tk.Label(
            info_frame,
            text="Select a macro to see details",
            font=("Arial", 9),
            justify=tk.LEFT,
            wraplength=460
        )
        self.info_label.pack(anchor=tk.W)
        
        # Bind selection change to show info
        self.macro_listbox.bind('<<ListboxSelect>>', self.on_macro_select)
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Run button
        self.run_button = tk.Button(
            control_frame,
            text="Run Selected Macro",
            command=self.run_selected_macro,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=10
        )
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        self.refresh_button = tk.Button(
            control_frame,
            text="Refresh List",
            command=self.load_macros,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=10
        )
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Download AHK button
        self.download_button = tk.Button(
            control_frame,
            text="Update AHK Script",
            command=self.download_ahk_script,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=10
        )
        self.download_button.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Ready", font=("Arial", 10))
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Instructions
        instructions = (
            "Instructions:\n"
            "1. Select a macro from the list above\n"
            "2. Click 'Run Selected Macro' or double-click the macro name\n"
            "3. The macro will be executed using AutoHotkey\n"
            "4. Use 'Refresh List' to reload available macros\n"
            "5. Use 'Update AHK Script' to download the latest execution script"
        )
        
        instructions_label = tk.Label(
            main_frame,
            text=instructions,
            font=("Arial", 8),
            justify=tk.LEFT,
            wraplength=460
        )
        instructions_label.pack()
        
    def load_macros(self):
        """Load available macros from the macros directory"""
        self.macro_listbox.delete(0, tk.END)
        self.macros = {}
        
        try:
            macro_files = [f for f in os.listdir("macros") if f.endswith('.json')]
            
            if not macro_files:
                self.macro_listbox.insert(tk.END, "No macros found")
                self.status_label.config(text="No macros found. Use Macro Maker to create some.")
                return
                
            for filename in macro_files:
                filepath = os.path.join("macros", filename)
                try:
                    with open(filepath, 'r') as f:
                        macro_data = json.load(f)
                    
                    macro_name = macro_data.get('name', filename.replace('.json', ''))
                    self.macros[macro_name] = {
                        'file': filename,
                        'data': macro_data
                    }
                    self.macro_listbox.insert(tk.END, macro_name)
                    
                except Exception as e:
                    print(f"Error loading macro {filename}: {e}")
                    continue
                    
            self.status_label.config(text=f"Loaded {len(self.macros)} macros")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load macros: {str(e)}")
            
    def on_macro_select(self, event):
        """Display information about the selected macro"""
        selection = self.macro_listbox.curselection()
        if not selection:
            return
            
        macro_name = self.macro_listbox.get(selection[0])
        if macro_name in self.macros:
            macro_data = self.macros[macro_name]['data']
            
            created = macro_data.get('created', 'Unknown')
            if created != 'Unknown':
                try:
                    created_dt = datetime.fromisoformat(created)
                    created = created_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
                    
            actions_count = len(macro_data.get('actions', []))
            duration = macro_data.get('total_duration', 0)
            
            info_text = (
                f"Macro: {macro_name}\n"
                f"Created: {created}\n"
                f"Actions: {actions_count}\n"
                f"Duration: {duration:.2f} seconds"
            )
            
            self.info_label.config(text=info_text)
            
    def find_autohotkey_executable(self):
        """Find AutoHotkey executable on the system"""
        for path in self.ahk_paths:
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
        
    def download_ahk_script(self):
        """Download the latest AHK script from GitHub"""
        def download_thread():
            try:
                self.progress.start()
                self.status_label.config(text="Downloading AHK script...")
                self.download_button.config(state=tk.DISABLED)
                
                response = requests.get(self.ahk_script_url, timeout=30)
                response.raise_for_status()
                
                with open("astdx_macro_runner.ahk", 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                self.progress.stop()
                self.status_label.config(text="AHK script downloaded successfully")
                messagebox.showinfo("Success", "AHK script downloaded successfully!")
                
            except requests.RequestException as e:
                self.progress.stop()
                self.status_label.config(text="Failed to download AHK script")
                messagebox.showerror("Download Error", f"Failed to download AHK script:\n{str(e)}")
                
            except Exception as e:
                self.progress.stop()
                self.status_label.config(text="Error downloading AHK script")
                messagebox.showerror("Error", f"Error downloading AHK script:\n{str(e)}")
                
            finally:
                self.download_button.config(state=tk.NORMAL)
                self.progress.stop()
                
        threading.Thread(target=download_thread, daemon=True).start()
        
    def run_selected_macro(self):
        """Run the selected macro"""
        selection = self.macro_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a macro to run.")
            return
            
        macro_name = self.macro_listbox.get(selection[0])
        if macro_name not in self.macros:
            messagebox.showerror("Error", "Invalid macro selection.")
            return
            
        def run_thread():
            try:
                self.progress.start()
                self.status_label.config(text="Running macro...")
                self.run_button.config(state=tk.DISABLED)
                
                # Check if AHK script exists, download if not
                ahk_script_path = "astdx_macro_runner.ahk"
                if not os.path.exists(ahk_script_path):
                    self.status_label.config(text="Downloading AHK script...")
                    response = requests.get(self.ahk_script_url, timeout=30)
                    response.raise_for_status()
                    
                    with open(ahk_script_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                
                # Find AutoHotkey executable
                ahk_exe = self.find_autohotkey_executable()
                if not ahk_exe:
                    raise Exception("AutoHotkey executable not found. Please install AutoHotkey.")
                
                # Get macro file path
                macro_file = self.macros[macro_name]['file']
                macro_path = os.path.abspath(os.path.join("macros", macro_file))
                
                # Run the AHK script with the macro file as parameter
                cmd = [ahk_exe, ahk_script_path, macro_path]
                
                self.status_label.config(text="Executing macro...")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.status_label.config(text="Macro executed successfully")
                    messagebox.showinfo("Success", f"Macro '{macro_name}' executed successfully!")
                else:
                    error_msg = result.stderr or result.stdout or "Unknown error"
                    raise Exception(f"AHK execution failed: {error_msg}")
                
            except subprocess.TimeoutExpired:
                self.status_label.config(text="Macro execution timed out")
                messagebox.showerror("Timeout", "Macro execution timed out.")
                
            except requests.RequestException as e:
                self.status_label.config(text="Failed to download AHK script")
                messagebox.showerror("Download Error", f"Failed to download AHK script:\n{str(e)}")
                
            except Exception as e:
                self.status_label.config(text="Error running macro")
                messagebox.showerror("Execution Error", f"Error running macro:\n{str(e)}")
                
            finally:
                self.run_button.config(state=tk.NORMAL)
                self.progress.stop()
                
        threading.Thread(target=run_thread, daemon=True).start()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MacroRunner()
    app.run()
