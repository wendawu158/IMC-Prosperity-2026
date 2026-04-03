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

    # Finished
    def emerald(self):
        """
        Trading algorithm specifically for Emeralds
        """

        # Emeralds
        EMERALDS = "EMERALDS"

        # True price for Emeralds
        EMERALDS_TRUE_PRICE = 10000

        # The order book without us
        EMERALDS_STABLE_ASK = 10008
        EMERALDS_STABLE_BID = 9992

        # Useful information from the TradingState
        self.orders[EMERALDS] = list()
        bids_emerald = self.state.order_depths[EMERALDS].buy_orders
        asks_emerald = self.state.order_depths[EMERALDS].sell_orders

        # Market making
        best_ask = EMERALDS_STABLE_ASK
        best_bid = EMERALDS_STABLE_BID

        position_emerald = 0

        # How many emeralds are we holding?
        try:
            position_emerald = self.state.position[EMERALDS]
        except KeyError:
            pass

        # Check for immediately profitable trades
        if len(bids_emerald.keys()) != 0:
            for bid in bids_emerald.keys():
                if bid > EMERALDS_TRUE_PRICE:
                    self.orders[EMERALDS].append(
                        Order(EMERALDS, bid, -1 * bids_emerald[bid])
                    )   # Here we are placing a sell to any bid above the fair price
                if bid > best_bid:
                    best_bid = bid

        if len(asks_emerald.keys()) != 0:
            for ask in asks_emerald.keys():
                if ask < EMERALDS_TRUE_PRICE:
                    self.orders[EMERALDS].append(
                        Order(EMERALDS, ask, -1 * asks_emerald[ask])
                    )   # Here we are placing a buy to any ask below the fair price
                if ask < best_ask:
                    best_ask = ask

        # Undercutting the competition, but still need to be above the true price
        if best_ask > EMERALDS_TRUE_PRICE:
            best_ask -= 1
        else:
            best_ask = EMERALDS_TRUE_PRICE

        if best_bid < EMERALDS_TRUE_PRICE:
            best_bid += 1
        else:
            best_bid = EMERALDS_TRUE_PRICE

        self.orders[EMERALDS].append(
            Order(EMERALDS, best_bid, 40)
        )
        self.orders[EMERALDS].append(
            Order(EMERALDS, best_ask, -40)
        )

        # Rebalance our inventory, if we are out of balance
        if position_emerald > 20 and bids_emerald.get(EMERALDS_TRUE_PRICE, 0) > 0:

            self.orders[EMERALDS].append(
                Order(EMERALDS, EMERALDS_TRUE_PRICE,
                      -1 * bids_emerald.get(EMERALDS_TRUE_PRICE)
                      )  # We don't wanna over correct
            )

        elif position_emerald < 20 and asks_emerald.get(EMERALDS_TRUE_PRICE, 0) > 0:

            self.orders[EMERALDS].append(
                Order(EMERALDS, EMERALDS_TRUE_PRICE,
                      -1 * asks_emerald.get(EMERALDS_TRUE_PRICE)
                      )  # We don't wanna over correct
            )

    def tomato(self):
        """
        Trading algorithm specifically for tomatoes
        """

        # Tomatoes
        TOMATOES = "TOMATOES"

        # Market making
        best_ask = sorted(self.state.order_depths[TOMATOES].sell_orders.keys())[0]
        best_bid = sorted(self.state.order_depths[TOMATOES].buy_orders.keys())[-1]














