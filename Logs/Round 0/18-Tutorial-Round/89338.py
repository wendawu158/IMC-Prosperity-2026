import pickle
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
        self.past_trader_data: Dict[str] = {}

        if state.traderData != "":
            self.past_trader_data = pickle.loads(self.state.traderData)

        # Output variables initialising
        self.orders: Dict[Symbol, List[Order]] = dict()
        self.future_trader_data = {}

        # The trading logic
        self.emerald()

        return self.orders, 0, pickle.dumps(self.future_trader_data, protocol=pickle.HIGHEST_PROTOCOL)

    # Finished
    def emerald(self):
        """
        Trading algorithm specifically for Emeralds

        Ticker
        Emeralds are a stable product
        Their true price stays at 10000 exactly
        The bid/ask given by the bot market makers is always 9992/10008
        However, sometimes we can see traders taking exit liquidity at 10000

        Strategy
        Undercut other market makers by 1 unit, offering at just above and below their bid/ask
        Use people taking exit liquidity to rebalance position
        Never take bids/asks below/above 10000
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
        position_emeralds = 0

        # How many emeralds are we holding?
        try:
            position_emeralds = self.state.position[EMERALDS]
        except KeyError:
            pass

        # Check for immediately profitable bids
        if len(bids_emerald.keys()) != 0:

            # Checking all the bids
            for bid in bids_emerald.keys():

                # Is there a bid better than the stable price of the EMERALDS?
                if bid >= EMERALDS_TRUE_PRICE:
                    self.orders[EMERALDS].append(
                        Order(EMERALDS, bid, -1 * bids_emerald[bid])
                    )   # Here we are placing a sell to any bid above the fair price

                # Figuring out the best bid
                if bid > best_bid:
                    best_bid = bid

        # Check for immediately profitable asks
        if len(asks_emerald.keys()) != 0:

            # Checking all the asks
            for ask in asks_emerald.keys():

                # Is there an ask better than the stable price of the EMERALDS?
                if ask <= EMERALDS_TRUE_PRICE:
                    self.orders[EMERALDS].append(
                        Order(EMERALDS, ask, -1 * asks_emerald[ask])
                    )   # Here we are placing a buy to any ask below the fair price

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
        if position_emeralds > 20 and bids_emerald.get(EMERALDS_TRUE_PRICE, 0) > 0:
            self.orders[EMERALDS].append(
                Order(EMERALDS, EMERALDS_TRUE_PRICE,
                      -1 * bids_emerald.get(EMERALDS_TRUE_PRICE)
                      )  # We don't wanna over correct
            )

        elif position_emeralds < 20 and asks_emerald.get(EMERALDS_TRUE_PRICE, 0) > 0:
            self.orders[EMERALDS].append(
                Order(EMERALDS, EMERALDS_TRUE_PRICE,
                      -1 * asks_emerald.get(EMERALDS_TRUE_PRICE)
                      )  # We don't wanna over correct
            )

    '''# WIP
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
        bids_tomato = self.state.order_depths[TOMATOES].buy_orders
        asks_tomato = self.state.order_depths[TOMATOES].sell_orders

        # Previous best non-outlier bid and ask for tomatoes
        previous_best_stable_ask = past_data.get("best ask", -1)
        previous_best_stable_bid = past_data.get("best bid", -1)
        previous_best_stable_midpoint = (previous_best_stable_ask + previous_best_stable_bid)/2

        # Different types of bids (they may not necessarily be different values)
        best_ask = sorted(self.state.order_depths[TOMATOES].sell_orders.keys())[0]
        best_bid = sorted(self.state.order_depths[TOMATOES].buy_orders.keys())[-1]

        best_fair_ask = best_ask
        best_fair_bid = best_bid

        best_stable_ask = best_ask
        best_stable_bid = best_bid

        if best_fair_ask < previous_best_stable_midpoint:
            best_fair_ask = sorted(self.state.order_depths[TOMATOES].sell_orders.keys())[1]
            if best_fair_ask < previous_best_stable_midpoint:
                best_fair_ask = sorted(self.state.order_depths[TOMATOES].sell_orders.keys())[2]

        if best_fair_bid > previous_best_stable_midpoint:
            best_fair_bid = sorted(self.state.order_depths[TOMATOES].buy_orders.keys())[-2]
            if best_fair_bid > previous_best_stable_midpoint:
                best_fair_bid = sorted(self.state.order_depths[TOMATOES].buy_orders.keys())[-3]

        if abs(best_stable_ask - previous_best_stable_ask) > 1:
            best_stable_ask = sorted(self.state.order_depths[TOMATOES].sell_orders.keys())[1]
            if abs(best_stable_ask - previous_best_stable_ask) > 1:
                best_stable_ask = sorted(self.state.order_depths[TOMATOES].sell_orders.keys())[2]
                if abs(best_stable_ask - previous_best_stable_ask) > 1:
                    best_stable_ask = previous_best_stable_ask

        if abs(best_stable_bid - previous_best_stable_bid) > 1:
            best_stable_bid = sorted(self.state.order_depths[TOMATOES].buy_orders.keys())[-2]
            if abs(best_stable_bid - previous_best_stable_bid) > 1:
                best_stable_bid = sorted(self.state.order_depths[TOMATOES].buy_orders.keys())[-3]
                if abs(best_stable_bid - previous_best_stable_bid) > 1:
                    best_stable_bid = previous_best_stable_bid

        # The number of tomatoes that we hold
        position_tomatoes = 0

        # How many tomatoes are we holding?
        try:
            position_tomatoes = self.state.position[TOMATOES]
        except KeyError:
            pass'''