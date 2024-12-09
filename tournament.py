import scipy.ndimage
import scipy.stats
import market_simulator_v2 as msim
from dataclasses import dataclass
import scipy
import numpy as np
import matplotlib.pyplot as plt

@dataclass
class Tournament:
    def __init__(self, tournament_name, tournament_rounds, sim_period, file_path):
        self.tournament_name = tournament_name
        self.tournament_rounds= tournament_rounds
        self.sim_period = sim_period
        self.file_path = file_path

    def run_tournament(self):
        sims = []
        for sim_num in range(self.tournament_rounds):
            sim = msim.MarketSim(self.tournament_name, f"Market {sim_num}")
            sim.load_config2(self.file_path)
            sim.calc_market()
            sims.append(sim.sim_period_silent(self.sim_period))

        return sims
        
    def eval_tournament(self):
        results = self.run_tournament()
        act_sur = []
        eff = []
        for sim in range(len(results)):
            act_sur.append(results[sim][0])
            eff.append(results[sim][1])

        # Initialize dictionaries to store totals and counts
        totals = {}
        counts = {}

        # Loop through each simulation result
        for _, _, _, _, _, trader_surplus in results:
            for trader, surplus in trader_surplus.items():
                if trader not in totals:
                    totals[trader] = 0
                    counts[trader] = 0
                totals[trader] += surplus
                counts[trader] += 1

        trader_ids = list(totals.keys())
        totals_array = np.array(list(totals.values()))
        counts_array = np.array(list(counts.values()))

        averages_array = scipy.ndimage.mean(totals_array, labels=np.arange(len(totals_array)), index=np.arange(len(totals_array)))
        averages = {trader_ids[i]: averages_array[i] / counts_array[i] for i in range(len(trader_ids))}

        # print averages
        for trader, avg in averages.items():
            print(f"{trader}: Average Surplus = {avg:.2f}")

        print(f"Median Actual Surplus: {scipy.ndimage.median(np.array(act_sur))}")
        print(f"Mean Actual Surplus: {scipy.ndimage.mean(np.array(act_sur))}")
        print(f"Median Efficiency: {scipy.ndimage.median(np.array(eff))}")
        print(f"Mean Efficiency: {scipy.ndimage.mean(np.array(eff))}")

        plt.hist(act_sur, bins=30, edgecolor='k', alpha=0.7)  # bins and aesthetics
        plt.title('Distribution of Actual Surplus')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.show()

        plt.hist(eff, bins=30, edgecolor='k', alpha=0.7)  # bins and aesthetics
        plt.title('Distribution of Effiency')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.show()

if __name__ == "__main__":
    sim = Tournament("tournament_name", 10000, 100)
    sim.eval_tournament()