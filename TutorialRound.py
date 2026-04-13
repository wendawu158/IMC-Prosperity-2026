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

        # The trading logic
        self.emerald()

        return self.orders, 0, self.traderData

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
                    )   # Here we are placing a sell to any bid above the fair price

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

        #Trading algorithm specifically for Emeralds

        #Ticker
        """"
        TOMATO are a drifting product
        Their true price stays at midpoint exactly
        The bid/ask given by the bot market makers is always 
        However, sometimes we can see traders taking exit liquidity

        Strategy
        Undercut other market makers by 1 unit, offering at just above and below their bid/ask
        Use people taking exit liquidity to rebalance position
        Never take bids/asks below/above 10000
        """""
        

        # Useful information from the TradingState
        self.orders[TOMATO] = list()
        bids_tomato = self.state.order_depths[TOMATO].buy_orders
        asks_tomato = self.state.order_depths[TOMATO].sell_orders

        # TOMATO
        TOMATO = "Tomato"

        # True price for TOMATO
        TOMATO_TRUE_PRICE =  

        # The order book without us
        TOMATO_STABLE_ASK = 
        TOMATO_STABLE_BID = 

        # Market making
        best_ask = TOMATO_STABLE_ASK
        best_bid = TOMATO_STABLE_BID

        # The number of emeralds that we hold
        position_tomato = 0

        # How many TOMATOs are we holding?
        try:
            position_tomato = self.state.position[TOMATO]
        except KeyError:
            pass

        # Check for immediately profitable bids
        if len(bids_tomato.keys()) != 0:

            # Checking all the bids
            for bid in bids_tomato.keys():

                # Is there a bid better than the stable price of the EMERALDS?
                if bid > TOMATO_TRUE_PRICE:
                    self.orders[TOMATO].append(
                        Order(TOMATO, bid, -1 * bids_tomato[bid])
                    )   # Here we are placing a sell to any bid above the fair price

                # Figuring out the best bid
                if bid > best_bid:
                    best_bid = bid

        # Check for immediately profitable asks
        if len(asks_tomato.keys()) != 0:

            # Checking all the asks
            for ask in asks_tomato.keys():

                # Is there an ask better than the stable price of the EMERALDS?
                if ask < TOMATO_TRUE_PRICE:
                    self.orders[TOMATO].append(
                        Order(TOMATO, ask, -1 * asks_tomato[ask])
                    )   # Here we are placing a buy to any ask below the fair price

                # Figuring out the best ask
                if ask < best_ask:
                    best_ask = ask

        # Undercutting the competition, but still need to be above the true price
        # Minimum price change is one unit of currency, hence the +/- 1
        if best_ask > TOMATO_TRUE_PRICE:
            best_ask -= 1
        else:
            best_ask = TOMATO_TRUE_PRICE

        if best_bid < TOMATO_TRUE_PRICE:
            best_bid += 1
        else:
            best_bid = TOMATO_TRUE_PRICE

        # Adding our normal orders
        # We aim to make profit on these trades
        self.orders[TOMATO].append(
            Order(TOMATO, best_bid, 40)
        )
        self.orders[TOMATO].append(
            Order(TOMATO, best_ask, -40)
        )

        # Rebalance our inventory, if we are out of balance
        # This is to prevent us from getting into situations where we are unable to place profitable trades
        # Basically, we buy up any trades at the true price to rebalance our position
        if position_tomato > 20 and bids_emerald.get(TOMATO_TRUE_PRICE, 0) > 0:
            self.orders[TOMATO].append(
                Order(TOMATO, TOMATO_TRUE_PRICE,
                      -1 * bids_tomato.get(TOMATO_TRUE_PRICE)
                      )  # We don't wanna over correct
            )

        elif position_tomato < 20 and asks_tomato.get(TOMATO_TRUE_PRICE, 0) > 0:
            self.orders[TOMATO].append(
                Order(TOMATO, TOMATO_TRUE_PRICE,
                      -1 * asks_tomato.get(TOMATO_TRUE_PRICE)
                      )  # We don't wanna over correct














