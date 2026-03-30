from datamodel import *


class Trader:

    def bid(self):
        pass

    def run(self, state: TradingState):
        """
        Overarching algorithm
        """

        # Output variables initialising
        self.orders = dict()
        self.output_trader_data = []

        self.emerald(state)

        return self.orders, 0, self.output_trader_data

    def emerald(self, state: TradingState):
        """
        Trading algorithm specifically for Emeralds
        """

        # True price for Emeralds
        EMERALD_PRICE = 10000



