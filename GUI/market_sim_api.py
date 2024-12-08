import tkinter as tk
from tkinter import filedialog, messagebox
from Simulator import market_simulator_v2 as sim
from pathlib import Path
import os

class MktSimGui:
    def __init__(self, top_window, simulator):
        self.top_window = top_window
        self.top_window.title("Spot Market Simulator")
        self.simulator = simulator
        self.config = {}
        self.data_file = ""
        self.sim = sim.MarketSim("orange market")

        # Create UI components
        self.load_button = tk.Button(self.top_window, text="Load Config File", width=16, 
                                     command=self.load_config_file)
        self.load_button.grid(row = 0, column = 0, padx=5, pady=10)

        self.message_label = tk.Label(self.top_window, text="", width=16)
        self.message_label.grid(row = 0, column = 1, padx=5, pady=5)

        self.instruct_label = tk.Label(self.top_window, text="Enter Data File Name:")
        self.instruct_label.grid(row = 1, column = 0, padx=5, pady=5)

        self.entry_text = tk.StringVar()
        self.entry = tk.Entry(root, width=15, textvariable=self.entry_text)
        self.entry.grid(row = 2, column = 0, padx=5, pady=5)

        self.open_button = tk.Button(self.top_window, text="Open Data File", command=self.open_data_file)
        self.open_button.grid(row = 2, column = 1, padx=5, pady=5)

        self.data_text = tk.Text(self.top_window, width=32, height=5)
        self.data_text.grid(row = 3, column = 0, columnspan=2, padx=5, pady=5)

        self.run_button = tk.Button(self.top_window, text="Run Simulation", width=16, command=self.run_sim)
        self.run_button.grid(row = 4, column = 0, padx=5, pady=5)

        self.quit_button = tk.Button(self.top_window, text="Quit", width=16, command=self.top_window.quit)
        self.quit_button.grid(row = 5, column = 0, padx=5, pady=5)

    def load_config_file(self):
        """Open a file dialog to select a configuration file."""
        file_path = filedialog.askopenfilename(title="Select a Config File", filetypes=[("TOML files", "*.toml")])
        print(file_path)
        if file_path:
            message = self.sim.load_config(file_path)
        self.message_label.config(text=message)

    def open_data_file(self):
        """Open a file dialog to select a configuration file."""
        dir_path=os.path.dirname(os.path.realpath(__file__))
        name = self.entry_text.get()
        file_path = f"{dir_path}\\{name}.toml"
        if file_path:
            if Path(file_path).is_file():
                messagebox.showinfo("Result", "This file already exists.")
            else:
                self.data_file = file_path
                print(self.data_file)
                self.data_text.insert("1.0",self.data_file)

    def run_sim(self):
        """Runs one period Simulation"""
        self.sim.calc_market()
        self.sim.show_market()
        self.sim.sim_period(100)
                
if __name__ == "__main__":
    root = tk.Tk()
    market_sim = sim.MarketSim()
    sim_app = MktSimGui(root, market_sim)
    root.mainloop()
    root.destroy()
