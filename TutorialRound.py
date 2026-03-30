from datamodel import *


class Trader:

    def bid(self):
        pass

    def run(self, state: TradingState):
        # True price for Emeralds
        EMERALD_PRICE = 10000

        # Output variables initialising
        orders = dict()
        output_trader_data = ""

        input_trader_data = state.traderData
        order_depths = state.order_depths
        own_trades = state.own_trades
        market_trades = state.market_trades
        position = state.position


        return orders, 0, output_trader_data
