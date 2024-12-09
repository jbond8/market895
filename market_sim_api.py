import tkinter as tk
from tkinter import filedialog, messagebox
import market_simulator_v2 as sim
import tournament as tourn
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

        # main container
        self.main_frame = tk.Frame(self.top_window)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # config frame
        config_frame = tk.LabelFrame(self.main_frame, text="Load Configuration File")
        config_frame.grid(row=0, column=0, pady=5, sticky="ew")

        self.file_path = None
        self.load_button = tk.Button(config_frame, text="Select File", command=self.load_config_file)
        self.load_button.grid(row=0, column=0, sticky="ew")

        self.message_label = tk.Label(config_frame, text="", width=16)
        self.message_label.grid(row = 0, column = 1, padx=5, pady=5)

        # simulation frame
        sim_frame = tk.LabelFrame(self.main_frame, text="Conduct Simulation")
        sim_frame.grid(row=1, column=0, pady=5, sticky="ew")
        self.run_button = tk.Button(sim_frame, text="Run Simulation", command=self.run_sim)
        self.run_button.grid(row=0, column=0, sticky="ew")

        # tournament frame
        tournament_frame = tk.LabelFrame(self.main_frame, text="Conduct Tournament")
        tournament_frame.grid(row=2, column=0, pady=5, sticky="ew")

        label = tk.Label(tournament_frame, text="Tournament Rounds:")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.tournament_rounds = tk.IntVar(value=0)
        self.rounds_entry = tk.Entry(tournament_frame, textvariable=self.tournament_rounds, width=10)
        self.rounds_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.run_tournament_button = tk.Button(tournament_frame, text="Run Tournament", command=self.run_tournament)
        self.run_tournament_button.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        # quit button
        self.quit_button = tk.Button(self.main_frame, text="Quit", command=self.top_window.quit)
        self.quit_button.grid(row=3, column=0, pady=10, sticky="ew")

    def load_config_file(self):
        """Open a file dialog to select a configuration file."""
        self.sim.reset_market()
        
        self.file_path = filedialog.askopenfilename(title="Select a Config File", filetypes=[("TOML files", "*.toml")])
        print(self.file_path)
        if self.file_path:
            message = self.sim.load_config(self.file_path)
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

    def run_tournament(self):
        """
        """
        rounds = self.tournament_rounds.get()
        print("Loading...")
        sim = tourn.Tournament("tournament_name", rounds, 100, self.file_path)
        sim.eval_tournament()

if __name__ == "__main__":
    root = tk.Tk()
    market_sim = sim.MarketSim()
    sim_app = MktSimGui(root, market_sim)
    root.mainloop()
    root.destroy()
