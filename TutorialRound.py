from datamodel import *


class Trader:

    def bid(self):
        pass

    def run(self, state: TradingState):
        """
        Overarching algorithm
        """

        # Output variables initialising
        self.orders: Dict[Symbol, List[Order]] = dict()
        self.output_trader_data: List[str] = [""]

        self.emerald(state)

        return self.orders, 0, "".join(self.output_trader_data)

    def emerald(self, state: TradingState):
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
        orders_emerald = self.orders[EMERALDS]  # Note that this is a reference, not a copy
        bids_emerald = state.order_depths[EMERALDS].buy_orders
        asks_emerald = state.order_depths[EMERALDS].sell_orders
        position_emerald = state.position[EMERALDS]

        # Check for immediately profitable trades
        if len(bids_emerald.keys()) != 0:
            for bid in bids_emerald.keys():
                if bid > EMERALDS_PRICE:
                    orders_emerald.append(
                        Order(EMERALDS, bid, -1 * bids_emerald[bid])
                    )   # Here we are placing a sell to any bid above the fair price

        if len(asks_emerald.keys()) != 0:
            for ask in asks_emerald.keys():
                if ask < EMERALDS_PRICE:
                    orders_emerald.append(
                        Order(EMERALDS, ask, -1 * asks_emerald[ask])
                    )   # Here we are placing a buy to any ask below the fair price






