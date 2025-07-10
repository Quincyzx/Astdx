import tkinter as tk
from tkinter import messagebox
import subprocess
import os

class MacroRunnerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Macro Runner")
        self.root.geometry("800x600")
        
        # Load macros from GitHub or local
        self.macros = self.load_macros()
        
        # Set up GUI components
        self.create_widgets()

    def create_widgets(self):
        # Label and Listbox for selecting a macro
        tk.Label(self.root, text="Select Macro to Run", font=("Arial", 16)).pack(pady=20)
        self.macro_listbox = tk.Listbox(self.root, height=15, width=50, font=("Arial", 12))
        self.macro_listbox.pack(pady=20)
        
        for macro in self.macros:
            self.macro_listbox.insert(tk.END, macro["name"])

        # Buttons for controlling the macro
        tk.Button(self.root, text="Run Macro", command=self.run_macro, font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Exit", command=self.root.quit, font=("Arial", 12)).pack(pady=10)

    def load_macros(self):
        # For simplicity, assume macros are stored in a local directory or can be fetched from GitHub
        macros_dir = "macros/"
        macros = []
        
        for filename in os.listdir(macros_dir):
            if filename.endswith(".json"):
                with open(os.path.join(macros_dir, filename), "r") as file:
                    macro = json.load(file)
                    macros.append(macro)
        
        return macros

    def run_macro(self):
        # Get selected macro name
        selected_macro = self.macro_listbox.get(tk.ACTIVE)
        if not selected_macro:
            messagebox.showerror("Error", "Please select a macro to run!")
            return

        # Run the macro using AHK
        macro_file = os.path.join("macros", selected_macro + ".json")
        subprocess.run([r'path_to_ahk_script.ahk', macro_file])  # Call AHK to run the macro

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MacroRunnerApp()
    app.run()
