import matplotlib.pyplot as plt
import numpy as np     
from dataclasses import dataclass
from typing import List
from operator import itemgetter
import random as rnd

@dataclass
class UnitCosts:
    owners_name: str
    current_unit = 0
    unit_costs: List[int]

    def __post_init__(self):
        """
        Check if list is non-empty and unit_costs are non-negative integers
        Sort list in ascending order to enforce increasing marginal cost
        """ 
        assert len(self.unit_costs) > 0, f"For {self.owners_name} no reservation values were given"
        assert self.check_costs(), f"For {self.owners_name} At least one value is not an integer, or is negative"
        self.unit_costs.sort()
    
    def check_costs(self):
        """ Checks to see if reservation values are integers
           and non_negative.
        """
        for cost in self.unit_costs:
            if type(cost) != int: return False
            if cost < 0: return False
        return True
    
    def build_unit_costs(self, units, low = 10, high = 200):
        """
        Returns a sorted list of unit costs between 
        low and high from a Uniform distribution.
        units = number of unit costs to be generated.
        """
        assert units > 0, f"For {self.owners_name} units must be positive"
        costs = [rnd.randint(low, high) for _ in range(0, units)]
        self.unit_costs = sorted(costs)

    @property
    def current(self):
        """
        Returns the current unit_cost, based
        on current_unit.  Returns None if
        current_unit is out of range.
        """
        try:
            return self.unit_costs[self.current_unit]
        except IndexError:
            return None

class ZI_Seller:
    def __init__(self, name, unit_costs):
        self.name = name
        self.type = 'S'
        self.costs = UnitCosts(name, unit_costs)
        self.prices = []
        self.contracts = []

    def __repr__(self):
        return f"{self.type}--{self.name} {self.costs.unit_costs} current unit = {self.costs.current_unit}"

    def ask(self, standing_bid, standing_ask, round, num_rounds):
        """ make a random ask between the current unit cost and the standing_ask
            ask = (name, "ask", amount)"""

        #print(f"current_cost = {self.costs.current}, standing_ask = {standing_ask}")
        if self.costs.current != None and self.costs.current < standing_ask:
            return self.name, "ask", rnd.randint(self.costs.current, standing_ask)
        else:
            return None

    def contract(self, price, your_contract):
        """
        Seller becomes informed about contract prices from Double Auction.
        Seller must be registered with Double Auction to get price information.
        If your_contract == True seller learns they have a contract at price.
        If your_contract == True seller updates their current_unit.
        """
        self.prices.append(price)
        if your_contract:
            self.contracts.append(price)
            self.costs.current_unit += 1

class Kaplan:
    """
    A Buyer who can bid in a Double Auction Spot Market.
    Modeled after Kaplan's bidding strategy in Rust et al. (1994)
    """
    def __init__(self, name, unit_costs):
        self.name = name
        self.type = 'S'
        self.costs = UnitCosts(name, unit_costs)
        self.prices = []
        self.contracts = []

    def __repr__(self):
        return f"{self.type}--{self.name} {self.costs.unit_costs} current unit = {self.costs.current_unit}"
        
    def bid(self, standing_bid, standing_ask, num_round, total_rounds):
        """
        Kaplan's bidding strategy as outline in Rust et al. (1994) p. 73
        """
        if self.costs.current == None:
            return None
        if standing_ask:
            if standing_bid:
                most = max(standing_bid, self.costs.current)
                if most > standing_bid:
                    if standing_ask <= 999 and ((self.values.current - standing_bid)/self.values.current) > 0.02 and (standing_ask - standing_bid) < (0.1 * standing_ask):
                        return self.name, "bid", min(standing_ask, most)
                    elif standing_ask <= 0:
                        return self.name, "bid", min(standing_ask, most)
                    elif (1 - (num_round / total_rounds)) <= 0.8:
                        return self.name, "bid", min(standing_ask, most)
                    else:
                        return None
                else:
                    return None
            else:
                most = self.values.current
                if most > standing_bid:
                    if standing_ask <= 999 and ((self.values.current - standing_bid)/self.values.current) > 0.02 and (standing_ask - standing_bid) < (0.1 * standing_ask):
                        return self.name, "bid", min(standing_ask, most)
                    elif standing_ask <= 0:
                        return self.name, "bid", min(standing_ask, most)
                    elif (1 - (num_round / total_rounds)) <= 0.8:
                        return self.name, "bid", min(standing_ask, most)
                    else:
                        return None
                else:
                    return None
        else:
            return self.name, "bid", 1


if __name__ == "__main__":
    print()
    print("Testing UnitCosts class")

    values = UnitCosts('Seller 1',[100, 50, 10])
    print(values.unit_costs)

    values.build_unit_costs(10)
    print(values.unit_costs)

    val = UnitCosts('Seller 2',[0])
    val.build_unit_costs(10)
    print(val.unit_costs)

    print()
    print("Testing Seller class")
    seller_1 = ZI_Seller("Seller 1", [100, 50, 10])
    print(seller_1)
    seller_1.contract(70, False)
    ask = seller_1.ask(60)
    seller_1.contract(60, True)
    print(f"Seller 1 sees prices {seller_1.prices}")
    print(f"Seller 1 has contracts {seller_1.contracts}")

                   