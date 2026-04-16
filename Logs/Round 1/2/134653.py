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
        self.past_trader_data: Dict[Symbol, Dict[str, Any]] = {}

        if state.traderData != "":
            self.past_trader_data = jsonpickle.decode(self.state.traderData)

        # Output variables initialising
        self.orders: Dict[Symbol, List[Order]] = dict()
        self.future_trader_data: Dict[Symbol, Dict[str, Any]] = dict()

        # The trading logic
        self.ash_coated_osmium()

        return self.orders, 0, jsonpickle.encode(self.future_trader_data)

    # Finished
    def ash_coated_osmium(self):
        """
        Trading algorithm specifically for tomatoes

        ASH_COATED_OSMIUMS are a product that remain stable over time
        Their true price stays around 10000
        However, sometimes we can see traders taking exit liquidity

        Strategy
        Undercut other market makers by 1 unit, offering at just above and below their bid/ask
        Use people taking exit liquidity to rebalance position
        Never take bids/asks below/above 10000

        Notes
        This is similar to the EMERALDS in the tutorial, but with some extra drift
        """
        # Ash Coated Osmium
        ASH_COATED_OSMIUM = "ASH_COATED_OSMIUM"

        # True price for Ash Coated Osmium
        ASH_COATED_OSMIUM_TRUE_PRICE = 10000

        # Useful information from the TradingState
        self.orders[ASH_COATED_OSMIUM] = list()
        bids_ash_coated_osmium = self.state.order_depths[ASH_COATED_OSMIUM].buy_orders
        asks_ash_coated_osmium = self.state.order_depths[ASH_COATED_OSMIUM].sell_orders
        past_trader_data = self.past_trader_data.get("ASH_COATED_OSMIUM", {})
        future_trader_data = {"past_best_bid": 0,
                              "past_best_ask": 0}

        # Market making
        if bids_ash_coated_osmium != {}:
            best_ask = sorted(bids_ash_coated_osmium.keys())[0]
        else:
            best_ask = past_trader_data["past_best_ask"]

        if asks_ash_coated_osmium != {}:
            best_bid = sorted(asks_ash_coated_osmium.keys())[-1]
        else:
            best_bid = past_trader_data["past_best_bid"]

        # The number of emeralds that we hold
        position_ash_coated_osmium = self.state.position.get(ASH_COATED_OSMIUM, 0)

        # Check for immediately profitable bids
        if len(bids_ash_coated_osmium.keys()) != 0:

            # Checking all the bids
            for bid in bids_ash_coated_osmium.keys():

                # Is there a bid better than the stable price of the EMERALDS?
                if bid > ASH_COATED_OSMIUM_TRUE_PRICE:
                    self.orders[ASH_COATED_OSMIUM].append(
                        Order(ASH_COATED_OSMIUM, bid, -1 * bids_ash_coated_osmium[bid])
                    )  # Here we are placing a sell to any bid above the fair price

                # Figuring out the best bid
                if bid > best_bid:
                    best_bid = bid

        # Check for immediately profitable asks
        if len(asks_ash_coated_osmium.keys()) != 0:

            # Checking all the asks
            for ask in asks_ash_coated_osmium.keys():

                # Is there an ask better than the stable price of the EMERALDS?
                if ask < ASH_COATED_OSMIUM_TRUE_PRICE:
                    self.orders[ASH_COATED_OSMIUM].append(
                        Order(ASH_COATED_OSMIUM, ask, -1 * asks_ash_coated_osmium[ask])
                    )  # Here we are placing a buy to any ask below the fair price
                # Figuring out the best ask that we should market make with
                elif ask < best_ask:
                    best_ask = ask

        future_trader_data["past_best_bid"] = best_bid
        future_trader_data["past_best_ask"] = best_ask
        self.future_trader_data[ASH_COATED_OSMIUM] = future_trader_data

        # Adding our normal orders
        # We aim to make profit on these trades
        self.orders[ASH_COATED_OSMIUM].append(
            Order(ASH_COATED_OSMIUM, best_bid + 1, 40)
        )
        self.orders[ASH_COATED_OSMIUM].append(
            Order(ASH_COATED_OSMIUM, best_ask - 1, -40)
        )

        # Rebalance our inventory, if we are out of balance
        # This is to prevent us from getting into situations where we are unable to place profitable trades
        # Basically, we buy up any trades at the true price to rebalance our position
        if position_ash_coated_osmium > 40 or position_ash_coated_osmium < 40:
            self.orders[ASH_COATED_OSMIUM].append(
                Order(ASH_COATED_OSMIUM, ASH_COATED_OSMIUM_TRUE_PRICE,
                      int(-1 * position_ash_coated_osmium / 10)
                      )  # We don't wanna over correct
            )