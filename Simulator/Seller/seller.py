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
            return self.name, "ask", rnd.uniform(self.costs.current, standing_ask)
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

class Kaplan_Seller:
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
        
    def ask(self, standing_bid, standing_ask, num_round, total_rounds):
        try:
            next_token = self.costs.unit_costs[self.costs.current_unit + 1]
        except IndexError:
            next_token = self.costs.current

        if self.costs.current == None:
            return None
        if standing_ask:
            if standing_bid:
                least = max(standing_bid, next_token + 1)
                if least < standing_ask:
                    if standing_bid >= 999 and ((standing_ask - self.costs.current)/self.costs.current) > 0.02 and (standing_ask - standing_bid) < (0.1 * standing_bid):
                        return self.name, "ask", max(standing_bid, least)
                    elif standing_bid >= 0:
                        return self.name, "ask", max(standing_bid, least)
                    elif (1 - (num_round / total_rounds)) <= 0.2:
                        return self.name, "ask", max(standing_bid, least)
                    else:
                        return None
                else:
                    return None
            else:
                least = next_token + 1
                if least < standing_ask:
                    if standing_bid >= 999 and ((standing_ask - self.costs.current)/self.costs.current) > 0.02 and (standing_ask - standing_bid) < (0.1 * standing_bid):
                        return self.name, "ask", max(standing_bid, least)
                    elif standing_bid >= 0:
                        return self.name, "ask", max(standing_bid, least)
                    elif (1 - (num_round / total_rounds)) <= 0.2:
                        return self.name, "ask", max(standing_bid, least)
                    else:
                        return None
                else:
                    return None
        else:
            return self.name, "ask", 1
        
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

class Ringuette_Seller:
    """
    A Buyer who can bid in a Double Auction Spot Market.
    Modeled after Ringuette's bidding strategy in Rust et al. (1994)
    """
    def __init__(self, name, unit_costs):
        self.name = name
        self.type = 'S'
        self.costs = UnitCosts(name, unit_costs)
        self.prices = []
        self.contracts = []

    def __repr__(self):
        return f"{self.type}--{self.name} {self.costs.unit_costs} current unit = {self.costs.current_unit}"
        
    def ask(self, standing_bid, standing_ask, num_round, total_rounds):
        try:
            next_token = self.costs.unit_costs[self.costs.current_unit + 1]
        except IndexError:
            next_token = self.costs.current
        
        if (1 - (num_round / total_rounds)) <= 0.2:
            skeleton = Skeleton_Seller(self.name, self.costs.unit_costs)
            skeleton.ask(standing_bid, standing_ask, num_round, total_rounds)
        else:
            span = (self.costs.unit_costs[-1] - self.costs.unit_costs[0] + 10)
            if standing_ask > (total_rounds/4):
                return self.name, "ask", standing_ask - 1
            else:
                if standing_bid:
                    if (standing_ask - standing_bid) > (span/5) and next_token < (standing_bid - (span/5)):
                        return self.name, "ask", standing_bid - 1 - (0.05 * rnd.uniform(0,1) * span)
                    else:
                        return None
                else:
                    return None

    def contract(self, price, your_contract):
        """
        Buyer becomes informed about contract prices from Double Auction.
        Buyer must be registered with Double Auction to get price information.
        If your_contract == True buyer learns they have a contract at price.
        If your_contract == True buyer updates their current_unit.
        """
        self.prices.append(price)
        if your_contract:
            self.contracts.append(price)
            self.costs.current_unit += 1

class PS_Seller:
    """
    A Buyer who can bid in a Double Auction Spot Market.
    Modeled after the 'Persistent Shout' bidding strategy in Priest & Tol (2003)
    """
    def __init__(self, name, unit_costs):
        self.name = name
        self.type = 'S'
        self.costs = UnitCosts(name, unit_costs)
        self.prices = []
        self.contracts = []

    def __repr__(self):
        return f"{self.type}--{self.name} {self.costs.unit_costs} current unit = {self.costs.current_unit}"
    
    def ask(self, standing_bid, standing_ask, num_round, total_rounds):
        r_1 = rnd.uniform(0,0.2)
        r_2 = rnd.uniform(0,0.2)
        gamma = 0.3
        beta = 0.05

        if standing_ask > standing_bid:
            delta = r_1 * standing_ask + r_2
            target = standing_bid - delta
            
            potential_ask = gamma * self.costs.current + (1 - gamma) * beta * (target - self.costs.current)
            if potential_ask >= self.costs.current:
                return self.name, "ask", potential_ask
            else:
                return None
        elif standing_ask <= standing_bid:
            delta = r_1 * standing_bid + r_2
            target = standing_ask + delta

            potential_ask = gamma * self.costs.current + (1 - gamma) * beta * (target - self.costs.current)
            if potential_ask >= self.costs.current:
                return self.name, "ask", potential_ask
            else:
                return None

    def contract(self, price, your_contract):
        """
        Buyer becomes informed about contract prices from Double Auction.
        Buyer must be registered with Double Auction to get price information.
        If your_contract == True buyer learns they have a contract at price.
        If your_contract == True buyer updates their current_unit.
        """
        self.prices.append(price)
        if your_contract:
            self.contracts.append(price)
            self.costs.current_unit += 1

class Skeleton_Seller:
    def __init__(self, name, unit_costs):
        self.name = name
        self.type = 'S'
        self.costs = UnitCosts(name, unit_costs)
        self.prices = []
        self.contracts = []

    def __repr__(self):
        return f"{self.type}--{self.name} {self.costs.unit_costs} current unit = {self.costs.current_unit}"
    
    def ask(self, standing_bid, standing_ask, num_round, total_rounds):
        try:
            next_token = self.costs.unit_costs[self.costs.current_unit + 1]
        except IndexError:
            next_token = self.costs.current

        if self.costs.current == None:
            return None

        alpha = 0.25 + 0.1 * rnd.uniform(0,1)
        if standing_ask:
            if standing_bid:
                most = max(standing_bid, next_token + 1)
                if most >= standing_ask:
                    return None
                else:
                    return self.name, "ask", (1 - alpha) * (standing_ask - 1) + alpha * most
            else:
                most = next_token + 1
                if most >= standing_bid:
                    return None
                else:
                    return self.name, "ask", (1 - alpha) * (standing_ask - 1) + alpha * most
        else:
            if standing_bid:
                most = max(standing_bid, self.costs.unit_costs[0] + 1)
                return self.name, "ask", most + (alpha * (self.costs.unit_costs[-1] - self.costs.unit_costs[0]))
            else:
                most = self.costs.unit_costs[0] + 1
                return self.name, "ask", most + (alpha * (self.costs.unit_costs[-1] - self.costs.unit_costs[0]))

    def contract(self, price, your_contract):
        """
        Buyer becomes informed about contract prices from Double Auction.
        Buyer must be registered with Double Auction to get price information.
        If your_contract == True buyer learns they have a contract at price.
        If your_contract == True buyer updates their current_unit.
        """
        self.prices.append(price)
        if your_contract:
            self.contracts.append(price)
            self.costs.current_unit += 1

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

                   