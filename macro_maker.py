import tkinter as tk
from tkinter import filedialog, messagebox
import json
import time
import threading
import subprocess

# Initialize a global variable to store the recorded actions
recording = []
last_time = None
mouse_listener = None
keyboard_listener = None
stop_flag = False

# Create the main GUI window
def start_recording():
    global recording, last_time, stop_flag
    recording = []
    last_time = time.time()
    stop_flag = False

    def on_click(x, y, button, pressed):
        global last_time
        if stop_flag:
            return False
        if pressed:
            now = time.time()
            delay = round((now - last_time) * 1000)
            recording.append({"type": "wait", "duration": delay, "description": f"Wait {delay}ms"})
            recording.append({"type": "click", "x": x, "y": y, "description": f"Click at {x},{y}"})
            last_time = now

    def on_press(key):
        global last_time
        if stop_flag:
            return False
        now = time.time()
        delay = round((now - last_time) * 1000)
        try:
            key_val = key.char
        except AttributeError:
            key_val = str(key)

        recording.append({"type": "wait", "duration": delay, "description": f"Wait {delay}ms"})
        recording.append({"type": "key_sequence", "keys": key_val, "description": f"Key: {key_val}"})
        last_time = now

    def record():
        global mouse_listener, keyboard_listener
        mouse_listener = mouse.Listener(on_click=on_click)
        keyboard_listener = keyboard.Listener(on_press=on_press)
        mouse_listener.start()
        keyboard_listener.start()
        mouse_listener.join()
        keyboard_listener.join()
        update_listbox()

    threading.Thread(target=record, daemon=True).start()

# Stop recording and show actions
def stop_recording():
    global stop_flag
    stop_flag = True
    try:
        if mouse_listener: mouse_listener.stop()
        if keyboard_listener: keyboard_listener.stop()
    except Exception:
        pass

def update_listbox():
    listbox.delete(0, tk.END)
    for action in recording:
        listbox.insert(tk.END, action["description"])

# Save the macro to a JSON file
def save_macro():
    name = entry.get().strip()
    if not name:
        messagebox.showerror("Error", "Enter a macro name.")
        return

    # Define path to save JSON file
    path = f"macros/{name}.json"
    macro_data = {"name": name, "actions": recording}

    with open(path, "w") as f:
        json.dump(macro_data, f, indent=2)

    messagebox.showinfo("Saved", f"Macro saved to {path}")

# Clear all recorded steps
def clear_macro():
    global recording
    recording = []
    update_listbox()

# Function to call AHK script to run the macro
def run_macro():
    name = entry.get().strip()
    if not name:
        messagebox.showerror("Error", "Enter a macro name.")
        return
    subprocess.run([r'path_to_ahk_script.ahk', name])

# Create main window for the GUI
root = tk.Tk()
root.title("Macro Recorder")
root.geometry("800x500")
root.configure(bg="#0a0a0f")

tk.Label(root, text="Macro Name:", fg="white", bg="#0a0a0f", font=("Segoe UI", 12)).place(x=20, y=20)
entry = tk.Entry(root, width=40, font=("Segoe UI", 12), bg="#1e1e2f", fg="white", insertbackground="white")
entry.place(x=140, y=20)

# Buttons for interaction
tk.Button(root, text="▶ Start Recording", command=start_recording, bg="#6f2dc7", fg="white", font=("Segoe UI", 12)).place(x=20, y=60)
tk.Button(root, text="⏹ Stop", command=stop_recording, bg="#e91e63", fg="white", font=("Segoe UI", 12)).place(x=200, y=60)
tk.Button(root, text="💾 Save", command=save_macro, bg="#28a745", fg="white", font=("Segoe UI", 12)).place(x=280, y=60)
tk.Button(root, text="🧹 Clear", command=clear_macro, bg="#444", fg="white", font=("Segoe UI", 12)).place(x=360, y=60)
tk.Button(root, text="▶ Run Macro", command=run_macro, bg="#ffab00", fg="white", font=("Segoe UI", 12)).place(x=440, y=60)

# Listbox to show recorded actions
listbox = tk.Listbox(root, width=100, height=20, bg="#1e1e2f", fg="white", font=("Consolas", 10))
listbox.place(x=20, y=120)

root.mainloop()
