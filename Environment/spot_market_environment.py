import matplotlib.pyplot as plt
import numpy as np     
from dataclasses import dataclass
from typing import List
from operator import itemgetter
import random as rnd

import Buyer.buyer as buyer
import Seller.seller as seller


@dataclass
class MarketEnvironment:
    name: str
    buyers = []
    sellers = []
    demand = []
    supply = []

    def add_buyer(self, buyer):
        self.buyers.append(buyer)

    def add_seller(self, seller):
        self.sellers.append(seller)

    def reset(self, name):
        self.buyers = []
        self.sellers = []
        self.demand = []
        self.supply = []
        self.name = name

    def build_buyer(self, name, units = 3, low = 10, high = 200):
        """
        Returns a sorted list of reservation values between 
        low and high from a Uniform distribution.
        units = number of reservation values to be generated.
        """
        new_buyer = buyer.ZI_Buyer(name, [0])
        new_buyer.reservation_values = \
            new_buyer.values.build_reservation_values(units, low, high)
        self.add_buyer(new_buyer)

    def build_seller(self, name, units = 3, low = 10, high = 200):
        """
        Returns a sorted list of unit_costs between 
        low and high from a Uniform distribution.
        units = number of unit_costs to be generated.
        """
        new_seller = seller.Seller(name, [0])
        new_seller.unit_costs = new_seller.costs.build_unit_costs(units, low, high)
        self.add_seller(new_seller)
            
    def make_demand(self):
        temp_demand = []
        for buyer in self.buyers:
            name = buyer.name
            values = buyer.values.reservation_values
            buyer_demand = [(name, value) for value in values]
            temp_demand.extend(buyer_demand)
        self.demand = sorted(temp_demand, key=itemgetter(1), reverse=True)

    def make_supply(self):
        temp_supply = []
        for seller in self.sellers:
            name = seller.name
            costs = seller.costs.unit_costs
            seller_supply = [(name, cost) for cost in costs]
            temp_supply.extend(seller_supply)
        self.supply = sorted(temp_supply, key=itemgetter(1))
    
    def show_participants(self):
        print ("Market Participants")
        print ("-------------------")
        print ("BUYERS")
        print ("------")
        for buyer in self.buyers:
            print (f"buyer {buyer.name} has values {buyer.values.reservation_values}")
        print("--------")
        print ("SELLERS")
        print ("-------")
        for seller in self.sellers:
            print (f"seller {seller.name} has costs {seller.costs.unit_costs}")
        print ("")

    def list_supply_demand(self):
        dem = self.demand
        sup = self.supply
        k = len(dem) - len(sup)
        if k > 0:
            for index in range(0, k):
                sup.append(('env', 999))
        elif k < 0:
            for index in range(0, -k):
                dem.append(('env', 0))
            
        print ("Unit     ID    Cost | Value     ID")
        print ("----------------------------------")
        big_tab = " "*15
        small_tab = " "*3
        k = 1
        first_crossing = True
        for d_unit, s_unit in zip(dem, sup):
            if s_unit[1] > d_unit[1] and first_crossing:
                print ("----------------------------------")
                first_crossing = False
            print(f"  {k:^2} {small_tab} {s_unit[0]:^3}    {s_unit[1]:^3} |", end = "")
            print(f"  {d_unit[1]:^3}      {d_unit[0]:^3}")
        k += 1
        print()

    def plot_supply_demand(self):
        """
        First define supply and demand curves
        """
        # For now prices = []
        prices = []
        dem = self.demand
        sup = self.supply
        
        # make units
        dunits = [units for units in range(0, len(dem)+2)]
        sunits = [units for units in range(0, len(sup)+1)]
        munits = munits = max(len(dunits), len(sunits))
        
        # make demand values
        max_value = dem[0][1] + 1
        demand_values = [max_value]         
        for id, value in dem:               
            demand_values.append(value)     
        demand_values.append(0)             

        # make supply costs
        supply_costs = [0]                 
        for id, cost in sup:               
            supply_costs.append(cost)     

        """
        Set up plot
        """
        plt.figure(figsize=(6, 4))  # Set plot dimensions
        ax = plt.subplot(111)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(True)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(True)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        plt.yticks(fontsize=14)
        plt.xticks(fontsize=14)

        """
        Made a bunch of small changes here
        """
        plt.step(dunits, demand_values, label='Demand')
        plt.step(sunits, supply_costs, label='Supply')

        if len(prices) > 0:
            prices.insert(0, prices[0])  # needed to get line segment for the first price
            punits = [unit for unit in range(len(prices))]
            plt.step(punits, prices, label='Prices')

        ax = plt.gca()
        plt.legend(loc='upper center', frameon=False)
        plt.title('Supply and Demand')
        plt.xlabel('units')
        plt.ylabel('currrency')

        # Save figure in the working directory
        # plt.savefig(self.name+'supply_demand.jpg')

        plt.xlim(0, munits)
        plt.ylim(0, max(demand_values + supply_costs))
        plt.show()

    def calc_equilibrium(self):
        """ Calculate Competitive Equilibrium information:
            eq_price_high
            eq_price_low
            eq_units
            max_surplus
        """

        self.max_surplus = 0
        self.eq_units = 0
        last_accepted_value = 0
        last_accepted_cost = 0
        first_rejected_value = 0
        first_rejected_cost = 999999999  # big number > max cost ever

        for buy_unit, sell_unit in zip(self.demand, self.supply):
            buyid, value = buy_unit
            sellid, cost = sell_unit
            if value >= cost:
                self.eq_units += 1
                self.max_surplus += value - cost
                last_accepted_value = value
                last_accepted_cost = cost
            else:
                first_rejected_value = value
                first_rejected_cost = cost
                break
        
        #  Now caluclate equilibrium price range
        if self.eq_units > 1:
            self.eq_price_high = min(last_accepted_value, first_rejected_cost)
            self.eq_price_low = max(last_accepted_cost, first_rejected_value)
        else:
            print("No Equilibrium")


    def show_equilibrium(self):
        #  Print out market equilibrium numbers
        print()
        print(f"When {self.name} is in equilibrium we have:")
        print(f"equilibrium price    = {self.eq_price_low} - {self.eq_price_high}")
        print(f"equilibrium quantity = {self.eq_units}")
        print(f"maximum surplus      = {self.max_surplus}")
        print()

    def get_equilibrium(self):
        return self.eq_units, self.eq_price_low, self.eq_price_high, self.max_surplus


if __name__ == "__main__":
    env = MarketEnvironment("Orange Market")
    env.build_buyer("buyer 1", 3, 10, 200)
    env.build_buyer("buyer 2", 3, 10, 200)
    env.build_buyer("buyer 3", 3, 10, 200)
    env.build_buyer("buyer 4", 3, 10, 200)
    env.build_seller("seller 1", 3, 10, 200)
    env.build_seller("seller 2", 3, 10, 200)
    env.build_seller("seller 3", 3, 10, 200)
    env.build_seller("seller 4", 3, 10, 200)
    env.show_participants()
    env.make_demand()
    env.make_supply()
    env.plot_supply_demand()
    env.show_participants()
    env.calc_equilibrium()
    env.show_equilibrium()