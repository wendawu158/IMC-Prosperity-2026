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
        # self.ash_coated_osmium()
        self.intarian_pepper_root()

        return self.orders, 0, jsonpickle.encode(self.future_trader_data)

    # Finished
    def ash_coated_osmium(self):
        """
        Trading algorithm specifically for ash_coated_osmium

        ASH_COATED_OSMIUMS are a product that remain stable over time
        Their true price stays around 10000
        However, sometimes we can see traders taking exit liquidity

        Strategy
        Undercut other market makers by 1 unit, offering at just above and below their bid/ask
        Balance market making based on position
        Always take bids/asks that cross the shm

        Notes
        This is similar to the EMERALDS in the tutorial, but with some extra drift
        """

        # Ash Coated Osmium
        ASH_COATED_OSMIUM = "ASH_COATED_OSMIUM"

        # Useful information from tradingstate
        orders: List[Order] = []
        bids: Dict[int, int] = self.state.order_depths[ASH_COATED_OSMIUM].buy_orders
        asks: Dict[int, int] = self.state.order_depths[ASH_COATED_OSMIUM].sell_orders
        past_trader_data: Dict[str, float | List[float]] = self.past_trader_data.get(ASH_COATED_OSMIUM,
                                                                                     {})
        future_trader_data: Dict[str, float | List[float]] = {"past_midpoints": [],
                                                              "past_mm_bid": 0,
                                                              "past_mm_ask": 0}
        effective_position: int = self.state.position.get(ASH_COATED_OSMIUM, 0)

        """
        Here we are estimating the current price
        Basically, any order that crosses the midpoint should be profitable
        Therefore, we will take it immediately
        """

        midpoints: List[float] = past_trader_data.get("past_midpoints",
                                                      [10000, 10000, 10000, 10000, 10000]
                                                      ).copy()

        if bids != {} and asks != {}:
            midpoints.pop(0)
            midpoints.append((sorted(bids.keys())[0] + sorted(asks.keys())[-1]) / 2)
        else:
            future_trader_data["past_midpoint"] = midpoints.count(midpoints[0]) / 2

        price_estimate = sum(midpoints) / 5

        """
        Taking immediately profitable trades across the price estimate
        """

        for bid in bids.keys():
            if bid > price_estimate:
                orders.append(Order(ASH_COATED_OSMIUM,
                                    bid,
                                    -1 * bids[bid]))
                effective_position += -1 * bids[bid]

        for ask in asks.keys():
            if ask < price_estimate:
                orders.append(Order(ASH_COATED_OSMIUM,
                                    ask,
                                    -1 * asks[ask]))
                effective_position += -1 * asks[ask]

        """
        Finding the best prices to market make at
        """

        best_mm_bid = -1
        best_mm_ask = -1

        for bid in sorted(bids.keys(), reverse=True):
            if bid + 1 < price_estimate:
                best_mm_bid = bid + 1

        for ask in sorted(bids.keys()):
            if ask - 1 > price_estimate:
                best_mm_ask = ask - 1

        if best_mm_bid == -1:
            best_mm_bid = past_trader_data.get("past_mm_bid", 9990)

        if best_mm_ask == -1:
            best_mm_ask = past_trader_data.get("past_mm_ask", 10010)

        """
        Market Making
        """
        bid_number = 0
        ask_number = 0

        if effective_position > 40:
            bid_number = int((80 - effective_position) / 2)
        else:
            bid_number = 20

        if effective_position < -40:
            ask_number = int((-80 - effective_position) / 2)
        else:
            ask_number = -20

        orders.append(Order(ASH_COATED_OSMIUM,
                            best_mm_bid,
                            bid_number)
                      )

        orders.append(Order(ASH_COATED_OSMIUM,
                            best_mm_ask,
                            ask_number)
                      )

        self.orders[ASH_COATED_OSMIUM] = orders

    def intarian_pepper_root(self):
        """
        Trading algorithm specifically for intarian_pepper_root

        intarian_pepper_roots are a product that steadily climb in price over time
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
        ASH_COATED_OSMIUM = "INTARIAN_PEPPER_ROOT"

        # Useful information from tradingstate
        orders: List[Order] = []
        bids: Dict[int, int] = self.state.order_depths[ASH_COATED_OSMIUM].buy_orders
        asks: Dict[int, int] = self.state.order_depths[ASH_COATED_OSMIUM].sell_orders
        past_trader_data: Dict[str, float | List[float]] = self.past_trader_data.get(ASH_COATED_OSMIUM,
                                                                                     {})
        future_trader_data: Dict[str, float | List[float]] = {"past_midpoints": [],
                                                              "past_mm_bid": 0,
                                                              "past_mm_ask": 0}
        effective_position: int = self.state.position.get(ASH_COATED_OSMIUM, 0)

        """
        Here we are estimating the current price
        Basically, any order that crosses the midpoint should be profitable
        Therefore, we will take it immediately
        """

        midpoints: List[float] = past_trader_data.get("past_midpoints",
                                                      [10000, 10000, 10000, 10000, 10000]
                                                      ).copy()

        if bids != {} and asks != {}:
            midpoints.pop(0)
            midpoints.append((sorted(bids.keys())[0] + sorted(asks.keys())[-1]) / 2)
        else:
            future_trader_data["past_midpoint"] = midpoints.count(midpoints[0]) / 2

        price_estimate = sum(midpoints) / 5

        """
        Taking immediately profitable trades across the price estimate
        """

        for bid in bids.keys():
            if bid > price_estimate:
                orders.append(Order(ASH_COATED_OSMIUM,
                                    bid,
                                    -1 * bids[bid]))
                effective_position += -1 * bids[bid]

        for ask in asks.keys():
            if ask < price_estimate:
                orders.append(Order(ASH_COATED_OSMIUM,
                                    ask,
                                    -1 * asks[ask]))
                effective_position += -1 * asks[ask]

        """
        Finding the best prices to market make at
        """

        best_mm_bid = -1
        best_mm_ask = -1

        for bid in sorted(bids.keys(), reverse=True):
            if bid + 1 < price_estimate:
                best_mm_bid = bid + 1

        for ask in sorted(bids.keys()):
            if ask - 1 > price_estimate:
                best_mm_ask = ask - 1

        if best_mm_bid == -1:
            best_mm_bid = past_trader_data.get("past_mm_bid", 9990)

        if best_mm_ask == -1:
            best_mm_ask = past_trader_data.get("past_mm_ask", 10010)

        """
        Market Making
        """
        bid_number = 0
        ask_number = 0

        if effective_position > 40:
            bid_number = int((80 - effective_position) / 2)
        else:
            bid_number = 20

        if effective_position < -40:
            ask_number = int((-80 - effective_position) / 2)
        else:
            ask_number = -20

        orders.append(Order(ASH_COATED_OSMIUM,
                            best_mm_bid,
                            bid_number)
                      )

        orders.append(Order(ASH_COATED_OSMIUM,
                            best_mm_ask,
                            ask_number)
                      )

        self.orders[ASH_COATED_OSMIUM] = orders

