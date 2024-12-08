import matplotlib.pyplot as plt
import numpy as np     
from dataclasses import dataclass
from tkinter import messagebox
from typing import List
from operator import itemgetter
import random as rnd
import toml

import Buyer.buyer as buyer
import Seller.seller as seller
import Institution.double_auction as institution
import Environment.spot_market_environment as environment

class MarketSim():
    """ run market Simulations """
    def __init__(self, sim_name = "temp_sim_name", 
                       market_name  ="temp_market_name"):
        self.sim_name = sim_name
        self.market_name = market_name
        self.trader_list = []
        self.env = environment.MarketEnvironment(self.market_name)
        self.da = institution.DoubleAuction(self.market_name)
    
    def build_a_buyer(self, name, num_units, low_v, high_v):
        self.env.build_buyer(name, num_units, low_v, high_v)

    def build_a_seller(self, name, num_units, low_c, high_c):
        self.env.build_seller(name, num_units, low_c, high_c)

    def reset_market(self):
        self.env.reset(self.market_name)

    def build_example_market(self):
        """Parameters can be read from config file"""
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
        self.env.make_demand()
        self.env.make_supply()
        self.env.calc_equilibrium()

    def show_market(self):
        self.env.show_participants()
        self.env.plot_supply_demand()
        self.env.show_equilibrium()

    def load_config(self, file_path):
        """Load configuration from the specified TOML file."""
        try:
            self.reset_market
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
                self.build_a_buyer(name, units, min_value, max_value)
            for k in range(self.num_sellers):
                seller_id = f"S{str(k+1)}"
                print(self.config[seller_id])
                name = self.config[seller_id]['name']
                units = self.config[buyer_id]['num_units']
                min_value = self.config[seller_id]['min_value']
                max_value = self.config[seller_id]['max_value']
                self.build_a_seller(name, units, min_value, max_value)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config file: {e}")
        return message


    def calc_efficiency(self, trader_list, max_surplus):
        """
        Calculates efficiency from actual da trades
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
        Simulates a period of trading lasting num_rounds
        """
       
        # Register buyers and sellers
        for buyer in self.env.buyers:
            self.da.register(buyer)
        for seller in self.env.sellers:
            self.da.register(seller)

        # run simulation
        traders = []
        traders.extend(self.env.buyers)
        traders.extend(self.env.sellers)

        for round in range(0, num_rounds):
            trader = rnd.choice(traders)
            standing_bid = self.da.book.standing['bid']
            standing_ask = self.da.book.standing['ask']
            if trader.type == "B": 
                bid = trader.bid(standing_bid)
                #print(f"standing bid = {standing_bid}, bid = {bid}")
                if bid != None: self.da.order(bid)
            if trader.type == "S": 
                ask = trader.ask(standing_ask)
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
              
if __name__ == "__main__":
    sim = MarketSim()
    sim.build_example_market()
    sim.show_market()
    sim.sim_period(100)   