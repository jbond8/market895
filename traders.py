import Simulator.market_simulator as msim
import Buyer.buyer as buyer

class Kaplan:
    def __init__(self):
        self.values = []
        self.costs = []

    def buyer(self):
        self.values = []
        self.prices = []
        self.contracts = []
    
    def seller(self):
        return
    
if __name__ == "__main__":
    sim = msim.MarketSim("sim_1", "Orange Market")
    sim.build_market()
    