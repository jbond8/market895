import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import market_simulator_v2 as sim
import tournament as tourn
from pathlib import Path
import os
import toml

class MktSimGui:
    def __init__(self, top_window, simulator):
        """
        Sets up the TKinter GUI.
        """
        self.top_window = top_window
        self.top_window.title("Spot Market Simulator")
        self.simulator = simulator
        self.config = {}
        self.data_file = ""
        self.sim = sim.MarketSim("orange market")

        # Main Container
        self.main_frame = tk.Frame(self.top_window)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Radio Button for selection between using a config file and drop-down menu
        self.selection = tk.StringVar(value="config")
        radio_frame = tk.LabelFrame(self.main_frame, text="Radio Button")
        radio_frame.grid(row=1, column=0, pady=5, sticky="ew")

        self.config_radio = ttk.Radiobutton(
            radio_frame,
            text="Load From Configuration File",
            variable=self.selection,
            value="config",
            command=self.toggle_frames,
        )
        self.config_radio.grid(row=0, column=0, sticky="w")

        self.self_select_radio = ttk.Radiobutton(
            radio_frame,
            text="Select Traders Yourself",
            variable=self.selection,
            value="self_select",
            command=self.toggle_frames,
        )
        self.self_select_radio.grid(row=0, column=1, sticky="w")

        # Frames for config file and drop-down menu
        self.config_frame = tk.LabelFrame(self.main_frame, text="Load Configuration File")
        self.trader_frame = tk.LabelFrame(self.main_frame, text="Select Traders")

        # Number of traders entry
        trader_num_label = tk.Label(self.trader_frame, text="Number of Traders:")
        trader_num_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.trader_num = tk.IntVar(value=0)
        self.trader_num.trace("w", lambda *args: self.update_traders())

        self.trader_num_entry = tk.Entry(self.trader_frame, textvariable=self.trader_num, width=10)
        self.trader_num_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Placeholder for trader rows
        self.trader_rows_frame = tk.Frame(self.trader_frame)
        self.trader_rows_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.file_path = None
        self.load_button = tk.Button(self.config_frame, text="Select File", command=self.load_config_file)
        self.load_button.grid(row=0, column=0, sticky="ew")

        self.message_label = tk.Label(self.config_frame, text="", width=16)
        self.message_label.grid(row=0, column=1, padx=5, pady=5)

        # Simulation Frame
        sim_frame = tk.LabelFrame(self.main_frame, text="Conduct Simulation")
        sim_frame.grid(row=4, column=0, pady=5, sticky="ew")
        self.run_button = tk.Button(sim_frame, text="Run Simulation", command=self.run_sim)
        self.run_button.grid(row=0, column=0, sticky="ew")

        # Tournament Frame
        tournament_frame = tk.LabelFrame(self.main_frame, text="Conduct Tournament")
        tournament_frame.grid(row=5, column=0, pady=5, sticky="ew")

        label = tk.Label(tournament_frame, text="Tournament Rounds:")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.tournament_rounds = tk.IntVar(value=0)
        self.rounds_entry = tk.Entry(tournament_frame, textvariable=self.tournament_rounds, width=10)
        self.rounds_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.run_tournament_button = tk.Button(tournament_frame, text="Run Tournament", command=self.run_tournament)
        self.run_tournament_button.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        # Quit Button
        self.quit_button = tk.Button(self.main_frame, text="Quit", command=self.top_window.quit)
        self.quit_button.grid(row=6, column=0, pady=10, sticky="ew")

        self.traders = []

        # Toggle Frames
        self.toggle_frames()

    def toggle_frames(self):
        """
        Toggles between the frames of the config file selection and drop-down menu for trader strategies.
        """
        if self.selection.get() == "config":
            self.config_frame.grid(row=2, column=0, pady=5, sticky="ew")
            self.trader_frame.grid_forget()
        else:
            self.trader_frame.grid(row=2, column=0, pady=5, sticky="ew")
            self.config_frame.grid_forget()

    def update_traders(self):
        """
        Updates the number of traders selected by user-input.
        """
        # Clears existing rows
        for widget in self.trader_rows_frame.winfo_children():
            widget.destroy()
        self.traders.clear()

        # Adds new rows for buyers and sellers
        try:
            for i in range(self.trader_num.get()):
                buyer_label = tk.Label(self.trader_rows_frame, text=f"Buyer {i + 1}")
                buyer_label.grid(row=i, column=0, pady=5, sticky="ew")

                buyer_strat = ttk.Combobox(self.trader_rows_frame)
                buyer_strat["values"] = ["Zero Intelligence", "Kaplan", "Ringuette", "Persistent Shout", "Skeleton"]
                buyer_strat.state(["readonly"])
                buyer_strat.grid(row=i, column=1, pady=5, sticky="ew")
                self.traders.append(("B", f"B{i + 1}", buyer_strat))

                seller_label = tk.Label(self.trader_rows_frame, text=f"Seller {i + 1}")
                seller_label.grid(row=i, column=2, pady=5, sticky="ew")

                seller_strat = ttk.Combobox(self.trader_rows_frame)
                seller_strat["values"] = ["Zero Intelligence", "Kaplan", "Ringuette", "Persistent Shout", "Skeleton"]
                seller_strat.state(["readonly"])
                seller_strat.grid(row=i, column=3, pady=5, sticky="ew")
                self.traders.append(("S", f"S{i + 1}", seller_strat))

            self.save_button = tk.Button(
            self.trader_rows_frame,
            text="Save Config to TOML and Load It",
            command=self.save_to_toml,
        )
            self.save_button.grid(row=self.trader_num.get(), column=0, pady=10, columnspan=4)
        except tk.TclError:
            print("Blank Field")


    def load_config_file(self):
        """
        Opens a file dialog to select a configuration file.
        """
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
        """
        Runs one period Simulation
        """
        self.sim.calc_market()
        self.sim.show_market()
        self.sim.sim_period(100)

    def run_tournament(self):
        """
        Runs a tournament where the number or rounds is determined by user-input.
        """
        rounds = self.tournament_rounds.get()
        print(f"File Path: {self.file_path}")
        print("Loading...")
        sim = tourn.Tournament("tournament_name", rounds, 100, self.file_path)
        sim.eval_tournament()

    def save_to_toml(self):
        """
        Saves trader drop-down menu selection to a .TOML file and promptly opens up a file dialog to select a configuration file.
        """
        # Collects configuration data
        config = {
            "title": "MarketSim Config",
            "message": "File Loaded",
            "num_buyers": self.trader_num.get(),
            "num_sellers": self.trader_num.get(),
        }

        for trader_type, name, combobox in self.traders:
            selected_strategy = combobox.get() or "Not Selected"
            config[name] = {
                "name": name,
                "type": trader_type,
                "num_units": 3,
                "min_value": 200 if trader_type == "B" else 100,
                "max_value": 400 if trader_type == "B" else 300,
                "trader_type": selected_strategy,
            }

        # write to toml file
        with open("custom_config.toml", "w") as toml_file:
            toml.dump(config, toml_file)

        print("Config saved to trader_config.toml")

        self.load_config_file()

if __name__ == "__main__":
    root = tk.Tk()
    market_sim = sim.MarketSim()
    sim_app = MktSimGui(root, market_sim)
    root.mainloop()
    root.destroy()