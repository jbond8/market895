import matplotlib.pyplot as plt
import numpy as np     
from dataclasses import dataclass
from tkinter import messagebox
from typing import List
from operator import itemgetter
import random as rnd
import toml

import double_auction as institution
import spot_market_environment as environment

class MarketSim():
    """
    Runs Market Simulations
    """
    def __init__(self, sim_name = "temp_sim_name", 
                       market_name  ="temp_market_name"):
        self.sim_name = sim_name
        self.market_name = market_name
        self.trader_list = []
        self.env = environment.MarketEnvironment(self.market_name)
        self.da = institution.DoubleAuction(self.market_name)
    
    def build_a_buyer(self, name, trader_type, num_units, low_v, high_v):
        """
        Carries inputs provided to environment module to build a buyer.
        args:
            name, name of buyer.
            trader_type, type of bidding strategy.
            num_units, number of reservation values to be generated.
            low_v, lowest possible valuation.
            high_v, highest possible valuation
        """
        self.env.build_buyer(name, trader_type, num_units, low_v, high_v)

    def build_a_seller(self, name, trader_type, num_units, low_c, high_c):
        """
        Carries inputs provided to environment module to build a seller.
        args:
            name, name of seller.
            trader_type, type of selling strategy.
            num_units, number of unit cost values to be generated.
            low_c, lowest possible cost.
            high_c, highest possible cost
        """
        self.env.build_seller(name, trader_type, num_units, low_c, high_c)

    def reset_market(self):
        """
        Resets lists of buyers, sellers, demand, and supply.
        """
        self.env.reset(self.market_name)

    def build_example_market(self):
        """
        An example of the parameters that can be read from a config file
        """
        self.env.reset(self.market_name)
        
        # build buyers and sellers
        self.env.build_buyer("buyer 1", 3, 10, 200)
        self.env.build_buyer("buyer 2", 3, 10, 200)
        self.env.build_buyer("buyer 3", 3, 10, 200)
        self.env.build_buyer("buyer 4", 3, 10, 200)
        self.env.build_seller("seller 1", 3, 10, 200)
        self.env.build_seller("seller 2", 3, 10, 200)
        self.env.build_seller("seller 3", 3, 10, 200)
        self.env.build_seller("seller 4", 3, 10, 200)

        # make supply and demand curves
        self.env.make_demand()
        self.env.make_supply()
        self.env.calc_equilibrium()

    def calc_market(self):
        """
        Creates a demand curve, supply curve, and finds the resulting equilibrium price and quantity of the two curves.
        """
        self.env.make_demand()
        self.env.make_supply()
        self.env.calc_equilibrium()

    def show_market(self):
        """
        Neatly prints out the participants in the simulation, plots the supply and demand curves, and neatly prints out the equilibrium price and quantity, and maximum surplus.
        """
        self.env.show_participants()
        self.env.plot_supply_demand()
        self.env.show_equilibrium()

    def load_config(self, file_path):
        """
        Loads configuration from the specified TOML file.
        args:
            file_path, path to TOML file.
        returns:
            message, message within TOML file.
        """
        try:
            self.da.contracts = []
            self.env.reset(self.market_name)

            self.config = toml.load(file_path)
            
            # Update the UI with the loaded configuration
            print()
            message = self.config['message']
            self.num_buyers = self.config['num_buyers']
            self.num_sellers = self.config['num_sellers']
            for k in range(self.num_buyers):
                buyer_id = f"B{str(k+1)}"
                print(self.config[buyer_id])
                name = self.config[buyer_id]['name']
                units = self.config[buyer_id]['num_units']
                min_value = self.config[buyer_id]['min_value']
                max_value = self.config[buyer_id]['max_value']
                trader_type = self.config[buyer_id]['trader_type']
                self.build_a_buyer(name, trader_type, units, min_value, max_value)
            for k in range(self.num_sellers):
                seller_id = f"S{str(k+1)}"
                print(self.config[seller_id])
                name = self.config[seller_id]['name']
                units = self.config[buyer_id]['num_units']
                min_value = self.config[seller_id]['min_value']
                max_value = self.config[seller_id]['max_value']
                trader_type = self.config[seller_id]['trader_type']
                self.build_a_seller(name, trader_type, units, min_value, max_value)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config file: {e}")
        return message
    
    def load_config2(self, file_path):
        """
        Loads configuration from the specified TOML file without print statements.
        args:
            file_path, path to TOML file.
        """
        self.da.contracts = []
        self.env.reset(self.market_name)

        self.config = toml.load(file_path)
        
        # Update the UI with the loaded configuration
        self.num_buyers = self.config['num_buyers']
        self.num_sellers = self.config['num_sellers']
        for k in range(self.num_buyers):
            buyer_id = f"B{str(k+1)}"
            name = self.config[buyer_id]['name']
            units = self.config[buyer_id]['num_units']
            min_value = self.config[buyer_id]['min_value']
            max_value = self.config[buyer_id]['max_value']
            trader_type = self.config[buyer_id]['trader_type']
            self.build_a_buyer(name, trader_type, units, min_value, max_value)
        for k in range(self.num_sellers):
            seller_id = f"S{str(k+1)}"
            name = self.config[seller_id]['name']
            units = self.config[buyer_id]['num_units']
            min_value = self.config[seller_id]['min_value']
            max_value = self.config[seller_id]['max_value']
            trader_type = self.config[seller_id]['trader_type']
            self.build_a_seller(name, trader_type, units, min_value, max_value)

    def calc_efficiency(self, trader_list, max_surplus):
        """
        Calculates efficiency from actual Double Auction trades
        args:
            trader_list, list of traders (both buyers and sellers).
            max_surplus, maximum amount of surplus.
        returns:
            actual_surplus, actual surplus for the simulation
            efficiency, how much of maximum surplus was captured by actual surplus
        """
          
        buyer_surplus = 0
        seller_surplus = 0
        actual_surplus = 0
        efficiency = 0

        for trader in trader_list:
            trader_surplus = 0
            unit = 0
            if trader.type == "B":
                res = trader.values.reservation_values
            else:
                res = trader.costs.unit_costs
            for contract in self.da.contracts:
                price, buyer_name, seller_name = contract
                if trader.type == "B":
                    if trader.name == buyer_name:
                        surplus = res[unit] - price
                        unit = unit + 1
                        trader_surplus = trader_surplus + surplus
                        buyer_surplus = buyer_surplus + surplus
                else:
                    if trader.name == seller_name:
                        surplus = price - res[unit]
                        unit = unit + 1
                        trader_surplus = trader_surplus + surplus
                        seller_surplus = seller_surplus + surplus
                                
        actual_surplus = buyer_surplus + seller_surplus
        efficiency = (actual_surplus/max_surplus)*100.0
        return actual_surplus, efficiency
           

    def sim_period(self, num_rounds):
        """
        Simulates a period of trading lasting num_rounds.
        args:
            num_rounds, number of rounds for simulation period.
        """
        # Registers buyers and sellers
        for buyer in self.env.buyers:
            self.da.register(buyer)
        for seller in self.env.sellers:
            self.da.register(seller)

        # Runs simulation
        traders = []
        traders.extend(self.env.buyers)
        traders.extend(self.env.sellers)

        for round in range(0, num_rounds):
            trader = rnd.choice(traders)
            standing_bid = self.da.book.standing['bid']
            standing_ask = self.da.book.standing['ask']
            if trader.type == "B": 
                bid = trader.bid(standing_bid, standing_ask, round, num_rounds)
                #print(f"standing bid = {standing_bid}, bid = {bid}")
                if bid != None: self.da.order(bid)
            if trader.type == "S": 
                ask = trader.ask(standing_bid, standing_ask, round, num_rounds)
                #print(f"standing ask = {standing_ask}, ask = {ask}")
                if ask != None: self.da.order(ask)
        print()
        self.da.book.print_book()
        print()
        print("Contracts")
        for contract in self.da.contracts:
            print(contract)
        print()
        eq_units, eq_price_low, eq_price_high, max_surplus = self.env.get_equilibrium()
        actual_surplus, efficiency = self.calc_efficiency(traders, max_surplus)
        print(f"actual surplus = {actual_surplus}, efficiency = {efficiency}")

    def sim_period_silent(self, num_rounds):
        """
        Simulates a period of trading lasting num_rounds without print statements.
        args:
            num_rounds, number of rounds for simulation period.
        returns:
            actual_surplus, actual surplus for the simulation
            efficiency, how much of maximum surplus was captured by actual surplus
            eq_units, the equiblirum number of units
            eq_price_low, the low equilibrium price
            eq_price_high, the high equilibirum price
            individual_surplus, a dictionary of individual traders and their respective surpluses.
        """
        # Registers buyers and sellers
        for buyer in self.env.buyers:
            self.da.register(buyer)
        for seller in self.env.sellers:
            self.da.register(seller)

        # Runs simulation
        traders = []
        traders.extend(self.env.buyers)
        traders.extend(self.env.sellers)

        for round in range(0, num_rounds):
            trader = rnd.choice(traders)
            standing_bid = self.da.book.standing['bid']
            standing_ask = self.da.book.standing['ask']
            if trader.type == "B": 
                bid = trader.bid(standing_bid, standing_ask, round, num_rounds)
                #print(f"standing bid = {standing_bid}, bid = {bid}")
                if bid != None: self.da.order(bid)
            if trader.type == "S": 
                ask = trader.ask(standing_bid, standing_ask, round, num_rounds)
                #print(f"standing ask = {standing_ask}, ask = {ask}")
                if ask != None: self.da.order(ask)
        
        eq_units, eq_price_low, eq_price_high, max_surplus = self.env.get_equilibrium()
        actual_surplus, efficiency = self.calc_efficiency(traders, max_surplus)
        individual_surplus = self.sim_trader_surplus(traders)
        return actual_surplus, efficiency, eq_units, eq_price_low, eq_price_high, individual_surplus

    def sim_trader_surplus(self, trader_list):
        """
        Calculates and stores individual surpluses for each buyer and seller.
        args:
            trader_list, list of traders (both buyers and sellers).
        returns:
            individual_surplus, a dictionary of individual traders and their respective surpluses.
        """
        # dictionary to store individual surpluses
        individual_surplus = {}

        # loop through all traders
        for trader in trader_list:
            trader_surplus = 0
            unit = 0
            if trader.type == "B":
                res = trader.values.reservation_values
            else:
                res = trader.costs.unit_costs
            
            for contract in self.da.contracts:
                price, buyer_name, seller_name = contract
                if trader.type == "B":
                    if trader.name == buyer_name:
                        surplus = res[unit] - price
                        unit += 1
                        trader_surplus += surplus  # total buyer surplus
                else:
                    if trader.name == seller_name:
                        surplus = price - res[unit]
                        unit += 1
                        trader_surplus += surplus  # total seller surplus

            # store the trader's individual surplus in the dictionary
            individual_surplus[trader.name] = trader_surplus

        # optionally return the dictionary
        return individual_surplus

if __name__ == "__main__":
    sim = MarketSim()
    sim.build_example_market()
    sim.show_market()
    sim.sim_period(100)   