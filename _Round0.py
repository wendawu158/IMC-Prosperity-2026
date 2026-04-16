from typing import Any

import jsonpickle
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
        self.past_trader_data: Dict[str, Dict[str, Any]] = {}

        if state.traderData != "":
            self.past_trader_data = jsonpickle.decode(self.state.traderData)

        # Output variables initialising
        self.orders: Dict[Symbol, List[Order]] = dict()
        self.future_trader_data = {}

        # The trading logic
        self.emerald()
        self.tomato()

        return self.orders, 0, jsonpickle.encode(self.future_trader_data)

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

        # The number of emeralds that we hold
        position_emerald = 0

        # How many emeralds are we holding?
        try:
            position_emerald = self.state.position[EMERALDS]
        except KeyError:
            pass

        # Check for immediately profitable bids
        if len(bids_emerald.keys()) != 0:

            # Checking all the bids
            for bid in bids_emerald.keys():

                # Is there a bid better than the stable price of the EMERALDS?
                if bid > EMERALDS_TRUE_PRICE:
                    self.orders[EMERALDS].append(
                        Order(EMERALDS, bid, -1 * bids_emerald[bid])
                    )  # Here we are placing a sell to any bid above the fair price

                # Figuring out the best bid
                if bid > best_bid:
                    best_bid = bid

        # Check for immediately profitable asks
        if len(asks_emerald.keys()) != 0:

            # Checking all the asks
            for ask in asks_emerald.keys():

                # Is there an ask better than the stable price of the EMERALDS?
                if ask < EMERALDS_TRUE_PRICE:
                    self.orders[EMERALDS].append(
                        Order(EMERALDS, ask, -1 * asks_emerald[ask])
                    )  # Here we are placing a buy to any ask below the fair price

                # Figuring out the best ask
                if ask < best_ask:
                    best_ask = ask

        # Undercutting the competition, but still need to be above the true price
        # Minimum price change is one unit of currency, hence the +/- 1
        if best_ask > EMERALDS_TRUE_PRICE:
            best_ask -= 1
        else:
            best_ask = EMERALDS_TRUE_PRICE

        if best_bid < EMERALDS_TRUE_PRICE:
            best_bid += 1
        else:
            best_bid = EMERALDS_TRUE_PRICE

        # Adding our normal orders
        # We aim to make profit on these trades
        self.orders[EMERALDS].append(
            Order(EMERALDS, best_bid, 40)
        )
        self.orders[EMERALDS].append(
            Order(EMERALDS, best_ask, -40)
        )

        # Rebalance our inventory, if we are out of balance
        # This is to prevent us from getting into situations where we are unable to place profitable trades
        # Basically, we buy up any trades at the true price to rebalance our position
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

    # Finished
    def tomato(self):
        """
        Trading algorithm specifically for tomatoes

        TOMATOES are a product that drift over time
        They don't appear to have any significant pattern. The midprice seems to either go up by one, down by one, or not at all
        However, sometimes we can see traders taking exit liquidity

        Strategy
        Undercut other market makers by 1 unit, offering at just above and below their bid/ask
        Use people taking exit liquidity to rebalance position
        Never take bids/asks below/above previous midpoint
        """

        # Tomatoes
        TOMATOES = "TOMATOES"

        # Previous data
        past_data = self.past_trader_data.get(TOMATOES, {})

        # Useful information from the TradingState
        self.orders[TOMATOES] = list()
        bids_tomatoes = self.state.order_depths[TOMATOES].buy_orders
        asks_tomatoes = self.state.order_depths[TOMATOES].sell_orders

        # Previous best non-outlier bid and ask for tomatoes
        previous_best_stable_ask = past_data.get("previous best stable ask", -1)
        previous_best_stable_bid = past_data.get("previous best stable bid", -1)
        previous_best_stable_midpoint = (previous_best_stable_ask + previous_best_stable_bid)/2

        # Taking immediately profitable trades
        for bid in bids_tomatoes.keys():
            if bid > previous_best_stable_midpoint:
                self.orders[TOMATOES].append(Order(TOMATOES,
                                                   bid,
                                                   -1 * bids_tomatoes[bid])
                                             )

        for ask in asks_tomatoes.keys():
            if ask < previous_best_stable_midpoint:
                self.orders[TOMATOES].append(Order(TOMATOES,
                                                   ask,
                                                   -1 * asks_tomatoes[ask])
                                             )

        """
        Different types of best (they may not necessarily be different values)
        Best represents the best on the orderbook
        Best fair represents the best on the orderbook that is profitable, when compared to the previous prices
        Best stable represents the true movement of the price, compared to previous stable prices, it should be either
        one unit up, one unit down, or no movement.
        """

        best_ask = sorted(self.state.order_depths[TOMATOES].sell_orders.keys())[0]
        best_bid = sorted(self.state.order_depths[TOMATOES].buy_orders.keys())[-1]

        best_stable_ask = best_ask
        best_stable_bid = best_bid

        if abs(best_stable_ask - previous_best_stable_ask) > 1:
            best_stable_ask = sorted(asks_tomatoes.keys())[1]
            if abs(best_stable_ask - previous_best_stable_ask) > 1:
                best_stable_ask = sorted(asks_tomatoes.keys())[2]
                if best_stable_ask > previous_best_stable_ask + 1:
                    best_stable_ask = previous_best_stable_ask + 1
                elif best_stable_ask < previous_best_stable_ask - 1:
                    best_stable_ask = previous_best_stable_ask - 1

        if abs(best_stable_bid - previous_best_stable_bid) > 1:
            best_stable_bid = sorted(bids_tomatoes.keys())[-2]
            if abs(best_stable_bid - previous_best_stable_bid) > 1:
                best_stable_bid = sorted(bids_tomatoes.keys())[-3]
                if best_stable_bid > previous_best_stable_bid + 1:
                    best_stable_bid = previous_best_stable_bid + 1
                elif best_stable_bid < previous_best_stable_bid - 1:
                    best_stable_bid = previous_best_stable_bid - 1

        self.future_trader_data[TOMATOES] = {"previous best stable ask": best_stable_ask,
                                             "previous best stable bid": best_stable_bid}

        # Market making
        best_fair_mm_ask = best_ask - 1
        best_fair_mm_bid = best_bid + 1

        for price in sorted(asks_tomatoes.keys()):
            if best_fair_mm_ask < previous_best_stable_midpoint:
                best_fair_mm_ask = price - 1
                break

        for price in sorted(bids_tomatoes.keys()):
            if best_fair_mm_bid > previous_best_stable_midpoint:
                best_fair_mm_bid = price + 1
                break

        self.orders[TOMATOES].append(
            Order(TOMATOES, best_fair_mm_bid, 40)
        )
        self.orders[TOMATOES].append(
            Order(TOMATOES, best_fair_mm_ask, -40)
        )

        # The number of tomatoes that we hold
        position_tomatoes = 0

        # How many tomatoes are we holding?
        try:
            position_tomatoes = self.state.position[TOMATOES]
        except KeyError:
            pass

        # Rebalance our inventory, if we are out of balance
        # This is to prevent us from getting into situations where we are unable to place profitable trades
        # Basically, we buy up any trades at the true price to rebalance our position
        if position_tomatoes > 20 and bids_tomatoes.get(previous_best_stable_midpoint, 0) > 0:
            self.orders[TOMATOES].append(
                Order(TOMATOES, previous_best_stable_midpoint,
                      -1 * bids_tomatoes.get(previous_best_stable_midpoint)
                      )  # We don't wanna over correct
            )

        elif position_tomatoes < 20 and asks_tomatoes.get(previous_best_stable_midpoint, 0) > 0:
            self.orders[TOMATOES].append(
                Order(TOMATOES, previous_best_stable_midpoint,
                      -1 * asks_tomatoes.get(previous_best_stable_midpoint)
                      )  # We don't wanna over correct
            )













