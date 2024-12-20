import matplotlib.pyplot as plt
import numpy as np     
from dataclasses import dataclass
from typing import List
from operator import itemgetter
import random as rnd

@dataclass
class ReservationValues:
    owners_name: str
    owners_type = "Buyer"
    current_unit = 0
    reservation_values: List[int]

    def __post_init__(self):
        """
        Checks: if reservation_values list is non-empty and are 
                non-negative integers
        Sorts:  seservation_values in descending order to enforce
                decreasing marginal utility
        """ 
        assert len(self.reservation_values) > 0, f"For {self.owners_name} no reservation values were given"
        assert self.check_values(), f"For {self.owners_name} At least one value is not an integer, or is negative"
        self.reservation_values.sort(reverse=True)

    def check_values(self):
        """ 
        Returns True if all reservation values are integers
                     and non_negative.
        """
        for value in self.reservation_values:
            if type(value) != int: return False
            if value < 0: return False
        return True

    def build_reservation_values(self, units, low = 10, high = 200):
        """
        Returns a sorted list of reservation values between 
        low and high from a Uniform distribution.
        units = number of reservation values to be generated.
        """
        assert units > 0, f"For {self.owners_name} units must be positive"
        values = [rnd.randint(low, high) for _ in range(units)]
        self.reservation_values = sorted(values, reverse=True) # List of values
         
    @property
    def current(self):
        """
        Returns the current reservation value, 
        based on current_unit.  Returns None if
        current_unit is out of range.
        """
        try:
            return self.reservation_values[self.current_unit]
        except IndexError:
            return None

class ZI_Buyer:
    """ 
    A Buyer who can bid in a Double Auction Spot Market. 
    """

    def __init__(self, name, reservation_values):
        self.name = name
        self.type = 'B'
        self.values = ReservationValues(name, reservation_values)
        self.prices = []
        self.contracts = []

    def __repr__(self):
        return f"{self.type}--{self.name} {self.values.reservation_values} current unit = {self.values.current_unit}"
    
    def bid(self, standing_bid, standing_ask, num_round, total_rounds):
        """ make a random bid between the standing_bid and current reservation value
            bid = (name, "bid", amount)"""
        
        #print(f"standing_bid = {standing_bid}, current_value = {self.values.current}")
        if self.values.current != None and standing_bid < self.values.current:
            return self.name, "bid", rnd.uniform(standing_bid, self.values.current)
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
            self.values.current_unit += 1

class Kaplan_Buyer:
    """
    A Buyer who can bid in a Double Auction Spot Market.
    Modeled after Kaplan's bidding strategy in Rust et al. (1994)
    """
    def __init__(self, name, reservation_values):
        self.name = name
        self.type = 'B'
        self.values = ReservationValues(name, reservation_values)
        self.prices = []
        self.contracts = []

    def __repr__(self):
        return f"{self.type}--{self.name} {self.values.reservation_values} current unit = {self.values.current_unit}"
        
    def bid(self, standing_bid, standing_ask, num_round, total_rounds):
        try:
            next_token = self.values.reservation_values[self.values.current_unit + 1]
        except IndexError:
            next_token = self.values.current
        
        if self.values.current == None:
            return None
        if standing_bid:
            if standing_ask:
                most = min(standing_ask, next_token - 1)
                if most > standing_bid:
                    if standing_ask <= 999 and ((self.values.current - standing_bid)/self.values.current) > 0.02 and (standing_ask - standing_bid) < (0.1 * standing_ask):
                        return self.name, "bid", min(standing_ask, most)
                    elif standing_ask <= 0:
                        return self.name, "bid", min(standing_ask, most)
                    elif (1 - (num_round / total_rounds)) <= 0.1:
                        return self.name, "bid", min(standing_ask, most)
                    else:
                        return None
                else:
                    return None
            else:
                most = next_token - 1
                if most > standing_bid:
                    if standing_ask <= 999 and ((self.values.current - standing_bid)/self.values.current) > 0.02 and (standing_ask - standing_bid) < (0.1 * standing_ask):
                        return self.name, "bid", min(standing_ask, most)
                    elif standing_ask <= 0:
                        return self.name, "bid", min(standing_ask, most)
                    elif (1 - (num_round / total_rounds)) <= 0.1:
                        return self.name, "bid", min(standing_ask, most)
                    else:
                        return None
                else:
                    return None
        else:
            return self.name, "bid", 1

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
            self.values.current_unit += 1
                   
class Ringuette_Buyer:
    """
    A Buyer who can bid in a Double Auction Spot Market.
    Modeled after Ringuette's bidding strategy in Rust et al. (1994)
    """
    def __init__(self, name, reservation_values):
        self.name = name
        self.type = 'B'
        self.values = ReservationValues(name, reservation_values)
        self.prices = []
        self.contracts = []

    def __repr__(self):
        return f"{self.type}--{self.name} {self.values.reservation_values} current unit = {self.values.current_unit}"
    
    def bid(self, standing_bid, standing_ask, num_round, total_rounds):
        try:
            next_token = self.values.reservation_values[self.values.current_unit + 1]
        except IndexError:
            next_token = self.values.current

        if (1 - (num_round / total_rounds)) <= 0.1:
            skeleton = Skeleton_Buyer(self.name, self.values.reservation_values)
            skeleton.bid(standing_bid, standing_ask, num_round, total_rounds)
        else:
            span = (self.values.reservation_values[0] - self.values.reservation_values[-1] + 10)
            if standing_bid < (total_rounds/4):
                return self.name, "bid", standing_bid + 1
            elif standing_bid > (total_rounds/4):
                if standing_ask:
                    if (standing_bid - standing_ask) > (span/5) and (next_token) > (standing_ask + (span/5)):
                        return self.name, "bid", standing_ask + 1 + (0.05 * rnd.uniform(0,1) * span)
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
            self.values.current_unit += 1

class PS_Buyer:
    """
    A Buyer who can bid in a Double Auction Spot Market.
    Modeled after the 'Persistent Shout' bidding strategy in Priest & Tol (2003)
    """
    def __init__(self, name, reservation_values):
        self.name = name
        self.type = 'B'
        self.values = ReservationValues(name, reservation_values)
        self.prices = []
        self.contracts = []

    def __repr__(self):
        return f"{self.type}--{self.name} {self.values.reservation_values} current unit = {self.values.current_unit}"
    
    def bid(self, standing_bid, standing_ask, num_round, total_rounds):
        try:
            next_token = self.values.reservation_values[self.values.current_unit + 1]
        except IndexError:
            next_token = self.values.current
        
        if self.values.current == None:
            return None

        r_1 = rnd.uniform(0,0.2)
        r_2 = rnd.uniform(0,0.2)
        gamma = 0.5
        beta = 0.1

        if standing_ask > standing_bid:
            delta = (r_1 * standing_bid) + r_2
            target = standing_bid + delta
            potential_bid = gamma * self.values.current + (1 - gamma) * beta * (target - self.values.current)
            if potential_bid <= self.values.current:
                return self.name, "bid", potential_bid
            else:
                return None
        elif standing_ask <= standing_bid:
            delta = (r_1 * standing_ask) + r_2
            target = standing_ask - delta
            potential_bid = gamma * self.values.current + (1 - gamma) * beta * (target - self.values.current)
            if potential_bid <= self.values.current:
                return self.name, "bid", potential_bid
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
            self.values.current_unit += 1

class Skeleton_Buyer:
    def __init__(self, name, reservation_values):
        self.name = name
        self.type = 'B'
        self.values = ReservationValues(name, reservation_values)
        self.prices = []
        self.contracts = []

    def __repr__(self):
        return f"{self.type}--{self.name} {self.values.reservation_values} current unit = {self.values.current_unit}"
    
    def bid(self, standing_bid, standing_ask, num_round, total_rounds):
        try:
            next_token = self.values.reservation_values[self.values.current_unit + 1]
        except IndexError:
            next_token = self.values.current

        if self.values.current == None:
            return None

        alpha = 0.25 + 0.1 * rnd.uniform(0,1)
        if standing_bid:
            if standing_ask:
                most = min(standing_ask, next_token - 1)
                if most <= standing_bid:
                    return None
                else:
                    return self.name, "bid", (1 - alpha) * (standing_bid + 1) + alpha * most
            else:
                most = next_token - 1
                if most <= standing_bid:
                    return None
                else:
                    return self.name, "bid", (1 - alpha) * (standing_bid + 1) + alpha * most
        else:
            if standing_ask:
                most = min(standing_ask, self.values.reservation_values[-1] - 1)
                return self.name, "bid", most - (alpha * (self.values.reservation_values[0] - self.values.reservation_values[-1]))
            else:
                most = self.values.reservation_values[-1] - 1
                return self.name, "bid", most - (alpha * (self.values.reservation_values[0] - self.values.reservation_values[-1]))

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
            self.values.current_unit += 1

if __name__ == "__main__":
    print()
    print("Testing ReservationValues class")

    values = ReservationValues('Buyer 1',[100, 50, 10])
    print(values.reservation_values)

    values.build_reservation_values(10)
    print(values.reservation_values)

    val = ReservationValues('Buyer 2',[0])
    val.build_reservation_values(10)
    print(val.reservation_values)

    print()
    print("Testing Buyer class")
    buyer_1 = ZI_Buyer("Buyer 1", [100, 50, 10])
    print(buyer_1)
    buyer_1.contract(70, False)
    bid = buyer_1.bid(60)
    buyer_1.contract(60, True)
    print(f"Buyer 1 sees prices {buyer_1.prices}")
    print(f"Buyer 1 has contracts {buyer_1.contracts}")
