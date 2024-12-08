import scipy.ndimage
import scipy.stats
import Simulator.market_simulator as msim
from dataclasses import dataclass
import scipy
import numpy as np
import matplotlib.pyplot as plt

@dataclass
class Tournament:
    def __init__(self, tournament_name, tournament_rounds, sim_period):
        self.tournament_name = tournament_name
        self.tournament_rounds= tournament_rounds
        self.sim_period = sim_period

    def run_tournament(self):
        sims = []
        for sim_num in range(self.tournament_rounds):
            sim = msim.MarketSim(self.tournament_name, f"Market {sim_num}")
            sim.build_market()
            sims.append(sim.sim_period_silent(self.sim_period))

        return sims
        
    def eval_tournament(self):
        results = self.run_tournament()
        act_sur = []
        eff = []
        for sim in range(len(results)):
            act_sur.append(results[sim][0])
            eff.append(results[sim][1])
        
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