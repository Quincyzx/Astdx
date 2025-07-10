import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import json
import os
import time
import threading
from pynput import mouse, keyboard
from datetime import datetime

class MacroMaker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Macro Maker - ASTDX")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Initialize variables
        self.actions = []
        self.recording = False
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Create macros directory if it doesn't exist
        if not os.path.exists("macros"):
            os.makedirs("macros")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Macro Maker", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Record button
        self.record_button = tk.Button(
            control_frame, 
            text="Start Recording", 
            command=self.toggle_recording,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=10
        )
        self.record_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.clear_button = tk.Button(
            control_frame,
            text="Clear Actions",
            command=self.clear_actions,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=10
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save button
        self.save_button = tk.Button(
            control_frame,
            text="Save Macro",
            command=self.save_macro,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=10
        )
        self.save_button.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Ready to record", font=("Arial", 10))
        self.status_label.pack(pady=(0, 10))
        
        # Actions display
        actions_label = tk.Label(main_frame, text="Recorded Actions:", font=("Arial", 12, "bold"))
        actions_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.actions_display = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            width=70,
            font=("Courier", 9),
            state=tk.DISABLED
        )
        self.actions_display.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = (
            "Instructions:\n"
            "1. Click 'Start Recording' to begin recording mouse clicks and keyboard input\n"
            "2. Perform your desired actions\n"
            "3. Click 'Stop Recording' when finished\n"
            "4. Click 'Save Macro' to save your recorded actions\n"
            "5. Use 'Clear Actions' to reset the current recording"
        )
        
        instructions_label = tk.Label(
            main_frame,
            text=instructions,
            font=("Arial", 8),
            justify=tk.LEFT,
            wraplength=550
        )
        instructions_label.pack(pady=(10, 0))
        
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.recording = True
        self.start_time = time.time()
        self.actions = []
        
        # Update UI
        self.record_button.config(text="Stop Recording", bg="#f44336")
        self.status_label.config(text="Recording... (Press ESC to stop)", fg="red")
        self.clear_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        
        # Clear actions display
        self.actions_display.config(state=tk.NORMAL)
        self.actions_display.delete(1.0, tk.END)
        self.actions_display.config(state=tk.DISABLED)
        
        # Start listeners
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        # Add initial wait action
        self.add_action({
            "type": "wait",
            "duration": 1.0,
            "timestamp": time.time() - self.start_time
        })
        
    def stop_recording(self):
        self.recording = False
        
        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Update UI
        self.record_button.config(text="Start Recording", bg="#4CAF50")
        self.status_label.config(text="Recording stopped", fg="black")
        self.clear_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        
        self.update_actions_display()
        
    def on_click(self, x, y, button, pressed):
        if not self.recording:
            return
            
        if pressed:  # Only record on press, not release
            current_time = time.time()
            action = {
                "type": "click",
                "x": x,
                "y": y,
                "button": button.name,
                "timestamp": current_time - self.start_time
            }
            self.add_action(action)
            
    def on_key_press(self, key):
        if not self.recording:
            return
            
        # Stop recording on ESC
        if key == keyboard.Key.esc:
            self.stop_recording()
            return
            
        current_time = time.time()
        
        try:
            # Handle special keys
            if hasattr(key, 'name'):
                key_name = key.name
            else:
                key_name = key.char
        except AttributeError:
            key_name = str(key)
            
        action = {
            "type": "key_press",
            "key": key_name,
            "timestamp": current_time - self.start_time
        }
        self.add_action(action)
        
    def on_key_release(self, key):
        # We don't record key releases for simplicity
        pass
        
    def add_action(self, action):
        self.actions.append(action)
        self.update_actions_display()
        
    def update_actions_display(self):
        self.actions_display.config(state=tk.NORMAL)
        self.actions_display.delete(1.0, tk.END)
        
        for i, action in enumerate(self.actions):
            if action["type"] == "click":
                text = f"{i+1}. Click {action['button']} at ({action['x']}, {action['y']}) [+{action['timestamp']:.2f}s]\n"
            elif action["type"] == "key_press":
                text = f"{i+1}. Press key '{action['key']}' [+{action['timestamp']:.2f}s]\n"
            elif action["type"] == "wait":
                text = f"{i+1}. Wait {action['duration']}s [+{action['timestamp']:.2f}s]\n"
            else:
                text = f"{i+1}. Unknown action [+{action['timestamp']:.2f}s]\n"
                
            self.actions_display.insert(tk.END, text)
            
        self.actions_display.config(state=tk.DISABLED)
        
    def clear_actions(self):
        self.actions = []
        self.actions_display.config(state=tk.NORMAL)
        self.actions_display.delete(1.0, tk.END)
        self.actions_display.config(state=tk.DISABLED)
        self.status_label.config(text="Actions cleared")
        
    def save_macro(self):
        if not self.actions:
            messagebox.showwarning("No Actions", "No actions recorded to save.")
            return
            
        # Get macro name from user
        macro_name = tk.simpledialog.askstring("Save Macro", "Enter macro name:")
        if not macro_name:
            return
            
        # Clean filename
        macro_name = "".join(c for c in macro_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{macro_name}.json"
        filepath = os.path.join("macros", filename)
        
        # Create macro data
        macro_data = {
            "name": macro_name,
            "created": datetime.now().isoformat(),
            "actions": self.actions,
            "total_duration": max(action["timestamp"] for action in self.actions) if self.actions else 0
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(macro_data, f, indent=2)
            
            messagebox.showinfo("Success", f"Macro saved as {filename}")
            self.status_label.config(text=f"Macro saved: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save macro: {str(e)}")
            
    def run(self):
        self.root.mainloop()

# Import tkinter.simpledialog
import tkinter.simpledialog

if __name__ == "__main__":
    app = MacroMaker()
    app.run()
