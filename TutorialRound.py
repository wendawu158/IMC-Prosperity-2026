from datamodel import *


class Trader:

    def bid(self):
        pass

    def run(self, state: TradingState):
        """
        Overarching algorithm
        """

        # Capture to a variable
        self.state = state

        # Output variables initialising
        self.orders: Dict[Symbol, List[Order]] = dict()
        self.traderData = ""

        self.emerald()

        return self.orders, 0, self.traderData

    def emerald(self):
        """
        Trading algorithm specifically for Emeralds
        """

        # Emeralds
        EMERALDS = "EMERALDS"

        # True price for Emeralds
        EMERALDS_PRICE = 10000

        # The order book without us
        EMERALDS_STABLE_ASK = 10008
        EMERALDS_STABLE_BID = 9992

        # Useful information from the TradingState
        self.orders[EMERALDS] = list()
        bids_emerald = self.state.order_depths[EMERALDS].buy_orders
        asks_emerald = self.state.order_depths[EMERALDS].sell_orders
        try:
            position_emerald = self.state.position[EMERALDS]
        except KeyError:
            position_emerald = 0

        # Check for immediately profitable trades
        # We also want to take fair trades, so that the bots can't take them and must trade with us
        if len(bids_emerald.keys()) != 0:
            for bid in bids_emerald.keys():
                if bid >= EMERALDS_PRICE:
                    self.orders[EMERALDS].append(
                        Order(EMERALDS, bid, -1 * bids_emerald[bid])
                    )   # Here we are placing a sell to any bid above the fair price

        if len(asks_emerald.keys()) != 0:
            for ask in asks_emerald.keys():
                if ask <= EMERALDS_PRICE:
                    self.orders[EMERALDS].append(
                        Order(EMERALDS, ask, -1 * asks_emerald[ask])
                    )   # Here we are placing a buy to any ask below the fair price










