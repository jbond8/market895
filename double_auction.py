import matplotlib.pyplot as plt
import numpy as np     
from dataclasses import dataclass
from typing import List
from operator import itemgetter
import random as rnd

import Simulator.Buyer.buyer as buyer
import Simulator.Seller.seller as seller

@dataclass
class LimitOrderBook:
    """ 
    maintains the limit-order-book
    book = {seq_number: offer_info}
         offer_info = {'type': 'bid' | 'ask',
                       'id': 'name',
                       'amount': bid | ask | None
                       'action': 'reject', 'standing', 'contract', 'start'}
    standing_bid = current standing bid
    standing_ask = current standing ask
    sequence_number = order of offers in book   
    """
    owner: str

    def __post_init__(self):
        self.initialize()
        
    def initialize(self):
        self.book = {} 
        self.sequence_number = 1
        
    def add (self, offer_info):
        self.book[self.sequence_number] = offer_info
        self.sequence_number += 1

    def set_standing(self, starting):
        """
        Initialize the standing bid and ask, and bid_id and ask_id,
        using the starting dictioary.  This is done at the start and
        after every contract.
        """
        self.standing = {}
        self.standing['bid'] = starting['bid']
        self.standing['bid_id'] = starting['bid_id']
        self.standing['ask'] = starting['ask']
        self.standing['ask_id'] = starting['ask_id']

    def start_new_contract(self, starting):
        """
        Called to initialize the book and standing bid nd ask, 
        before offers are made for a new contract
        """        
        starting_bid_info = {'type': 'bid', 'id': starting['bid_id'], 
                             'amount': starting['bid'], 'action': 'start'}
        self.add(starting_bid_info)
        starting_ask_info = {'type': 'ask', 'id': starting['ask_id'], 
                             'amount': starting['ask'], 'action': 'start'}
        self.add(starting_ask_info)
        self.set_standing(starting)

    def print_book(self):
        """ print the order book"""
        print(f" Order Book for {self.owner}")
        for seq in range(1, self.sequence_number):
            offer_info = self.book[seq]
            type = offer_info['type']
            id = offer_info['id']
            amount = offer_info['amount']
            action = offer_info['action']
            pt = f"{seq} {action} {type} {amount}:{id}"
            print(pt)

class DoubleAuction:
    """
    Implements a double auction
    """
    def __init__(self, name):
        self.name = name
        self.participants = []
        self.book = LimitOrderBook(name)
        self.contracts = []
        self.starting = {'bid': 0, 'bid_id': self.name,
                    'ask':999, 'ask_id': self.name}
        self.book.start_new_contract(self.starting)

    def register(self, trader):
        """ make a random ask between the current unit cost and the standing_ask"""
        self.participants.append(trader)

    def check_name(self, name):
        for participant in self.participants:
            if participant.name == name:
                return True
        return False

    def get_trader(self, name):
        for participant in self.participants:
            if participant.name == name:
                return participant
        return None  

    def order(self, order):
        """
        An order is a tupple = (name, type, amount), where
        name is the name of the trader, 
        type is 'bid' or 'ask', and 
        amount is an integer amount of money for the type
        """        
        name, type, amount = order
        order_info = {}
        order_info["id"] = name  
        order_info["type"] = type  
        order_info["amount"] = amount 
        
        # Check Order
        if not self.check_name(name):
            order_info["action"] = "rejected"
            self.book.add(order_info)
            return "Error: invalid name"
        trader = self.get_trader(name)

        if type == 'bid' and trader.type == "S":
            order_info["action"] = "rejected"
            self.book.add(order_info)
            return "Error: seller cannon make bid"
        
        if type == 'ask' and trader.type == "B":
            order_info["action"] = "rejected"
            self.book.add(order_info)
            return "Error: buyer cannon make ask"
        
        # Process order
        standing_bid = self.book.standing['bid']
        standing_bid_id = self.book.standing['bid_id']
        standing_ask = self.book.standing['ask']
        standing_ask_id = self.book.standing['ask_id']
        
        if type == "bid":
            if amount >= standing_ask:
                order_info["action"] = "contract"
                self.book.add(order_info)
                price = standing_ask
                buyer = name
                seller = standing_ask_id
                self.contract(price, buyer, seller)
                return "contract"
            
            if amount > standing_bid:
                order_info["action"] = "standing"
                self.book.add(order_info)
                self.book.standing['bid'] = amount
                self.book.standing['bid_id'] = name
                return "standing"
            
            order_info["action"] = "rejected"
            self.book.add(order_info)
            return "rejected"
        
        if type == "ask":
            if amount <= standing_bid:
                order_info["action"] = "contract"
                self.book.add(order_info)
                price = standing_bid
                seller = name
                buyer = standing_bid_id
                self.contract(price, buyer, seller)
                return "contract"
            
            if amount < standing_ask:
                order_info["action"] = "standing"
                self.book.add(order_info)
                self.book.standing['ask'] = amount
                self.book.standing['ask_id'] = name
                return "standing"
            
            order_info["action"] = "rejected"
            self.book.add(order_info)
            return "rejected"
                
    def contract(self, price, buyer, seller):
        """
        Called when a contract occurs.
        contract = (price, buyer, seller)
        contract is appended to self.contracts
        """
        self.contracts.append((price, buyer, seller))
        #print(self.contracts)
        for participant in self.participants:
            if participant.name == buyer or participant.name == seller:
                participant.contract(price, True)
            else:
                participant.contract(price, False)
        self.book.start_new_contract(self.starting)