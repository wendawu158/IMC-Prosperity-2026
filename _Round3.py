from typing import Any
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
        self.hydrogel_packs()
        # self.velvetfruit_extract()

        return self.orders, 0, jsonpickle.encode(self.future_trader_data)

    def hydrogel_packs(self):
        """
        Trading algorithm specifically for hydrogel_packs

        HYDROGEL_PACK is a product that experiences some level of drift, but nothing crazy
        Their true price starts at around 10000, but beyond that it is a mystery
        However, we have determined that there is a market making bot that has consistent order sizes
        We can use that to determine fair price

        Strategy
        Undercut other market makers by 1 unit, offering at just above and below their bid/ask
        Balance market making based on position
        Always take bids/asks that cross the fair price

        Notes
        Appears to be entirely random drift unfortunately
        """

        # HYDROGEL_PACK
        HYDROGEL_PACK = "HYDROGEL_PACK"

        orders: List[Order] = []
        bids: Dict[int, int] = self.state.order_depths[HYDROGEL_PACK].buy_orders
        asks: Dict[int, int] = self.state.order_depths[HYDROGEL_PACK].sell_orders

        effective_position: int = self.state.position.get(HYDROGEL_PACK, 0)

        if (
            bids[sorted(bids.keys())[-1]] > 10 or
            (bids[sorted(bids.keys())[-1]] == 10 and bids[sorted(bids.keys())[-1]] >= 20)
        ):
            bid_wall = sorted(bids.keys())[-1]
        else:
            bid_wall = sorted(bids.keys())[-2]

        if (
            asks[sorted(asks.keys())[0]] < -10 or
            (asks[sorted(asks.keys())[0]] == -10 and asks[sorted(asks.keys())[1]] <= -20)
        ):
            ask_wall = sorted(asks.keys())[0]
        else:
            ask_wall = sorted(asks.keys())[1]

        past_price = self.past_trader_data.get(HYDROGEL_PACK, {}).get("past_price", 10000)
        price_estimate = (ask_wall + bid_wall) // 2
        self.future_trader_data[HYDROGEL_PACK] = {"past_price": price_estimate}

        """
        Taking immediately profitable trades
        """

        for bid in bids.keys():
            if bid > price_estimate:
                orders.append(Order(HYDROGEL_PACK,
                                    bid,
                                    -1 * bids[bid]))
                effective_position += -1 * bids[bid]

        for ask in asks.keys():
            if ask < price_estimate:
                orders.append(Order(HYDROGEL_PACK,
                                    ask,
                                    -1 * asks[ask]))
                effective_position += -1 * asks[ask]

        """
        Finding the best prices to market make at
        """

        best_mm_bid = bid_wall + 1
        best_mm_ask = ask_wall - 1

        """
        Market Making
        """
        bid_number = 0
        ask_number = 0

        weighting = (price_estimate - past_price) * 20

        if effective_position > 60:
            bid_number = int((150 - effective_position) / 2) - weighting
        else:
            bid_number = 60 - weighting

        if effective_position < -100:
            ask_number = int((-150 - effective_position) / 2) - weighting
        else:
            ask_number = -60 - weighting

        if best_mm_bid != -1:
            orders.append(Order(HYDROGEL_PACK,
                                best_mm_bid,
                                bid_number)
                          )

        if best_mm_ask != -1:
            orders.append(Order(HYDROGEL_PACK,
                                best_mm_ask,
                                ask_number)
                          )

        self.orders[HYDROGEL_PACK] = orders

    def velvetfruit_extract(self):
        """
        Guess what
        Same algo
        boom
        """

        # VELVETFRUIT_EXTRACT
        VELVETFRUIT_EXTRACT = "VELVETFRUIT_EXTRACT"

        orders: List[Order] = []
        bids: Dict[int, int] = self.state.order_depths[VELVETFRUIT_EXTRACT].buy_orders
        asks: Dict[int, int] = self.state.order_depths[VELVETFRUIT_EXTRACT].sell_orders

        effective_position: int = self.state.position.get(VELVETFRUIT_EXTRACT, 0)

        if bids[sorted(bids.keys())[0]] >= 15:
            bid_wall = sorted(bids.keys())[0]
        elif bids[sorted(bids.keys())[1]] >= 15:
            bid_wall = sorted(bids.keys())[1]
        else:
            bid_wall = sorted(bids.keys())[2]

        if asks[sorted(asks.keys())[-1]] <= -15:
            ask_wall = sorted(asks.keys())[-1]
        elif asks[sorted(asks.keys())[-2]] <= -15:
            ask_wall = sorted(asks.keys())[-2]
        else:
            ask_wall = sorted(asks.keys())[-3]

        past_price = self.past_trader_data.get(VELVETFRUIT_EXTRACT, {}).get("past_price", 5250)
        price_estimate = (ask_wall + bid_wall) // 2
        self.future_trader_data[VELVETFRUIT_EXTRACT] = {"past_price": price_estimate}

        """
        Taking immediately profitable trades
        """

        for bid in bids.keys():
            if bid > price_estimate:
                orders.append(Order(VELVETFRUIT_EXTRACT,
                                    bid,
                                    -1 * bids[bid]))
                effective_position += -1 * bids[bid]

        for ask in asks.keys():
            if ask < price_estimate:
                orders.append(Order(VELVETFRUIT_EXTRACT,
                                    ask,
                                    -1 * asks[ask]))
                effective_position += -1 * asks[ask]

        """
        Finding the best prices to market make at
        """

        best_mm_bid = bid_wall + 1
        best_mm_ask = ask_wall - 1

        """
        Market Making
        """
        bid_number = 0
        ask_number = 0

        weighting = (price_estimate - past_price) * 5

        if effective_position > 40:
            bid_number = int((160 - effective_position) / 4) - weighting
        else:
            bid_number = 40 - weighting

        if effective_position < -40:
            ask_number = int((-160 - effective_position) / 4) - weighting
        else:
            ask_number = -40 - weighting

        if best_mm_bid != -1:
            orders.append(Order(VELVETFRUIT_EXTRACT,
                                best_mm_bid,
                                bid_number)
                          )

        if best_mm_ask != -1:
            orders.append(Order(VELVETFRUIT_EXTRACT,
                                best_mm_ask,
                                ask_number)
                          )

        self.orders[VELVETFRUIT_EXTRACT] = orders