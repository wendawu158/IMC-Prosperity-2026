import math
import json
from typing import Dict, List, Any


from datamodel import OrderDepth, UserId, TradingState, Order

# Use these imports in your actual file

class Trader:
    def __init__(self):
        # Hyperparameters
        self.risk_free_rate = 0.0
        self.volatility = 0.0373  # Tuned to the 3-day window from our previous analysis

        # Position Limits (Make sure to verify these in the round instructions)
        self.VELVET_LIMIT = 250
        self.HYDROGEL_LIMIT = 250
        self.OPTION_LIMIT = 100

        self.TOTAL_TIME_STEPS = 3000000  # 3 Days * 1,000,000 timestamps

    # --- Black-Scholes Math Helpers ---
    def norm_cdf(self, x: float) -> float:
        """Approximates the cumulative distribution function for a standard normal."""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    def calculate_bs_call(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        if T <= 0: return max(0.0, S - K)
        if sigma <= 0: return max(0.0, S - K)
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        return S * self.norm_cdf(d1) - K * math.exp(-r * T) * self.norm_cdf(d2)

    def calculate_delta(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        if T <= 0: return 1.0 if S > K else 0.0
        if sigma <= 0: return 1.0 if S > K else 0.0
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        return self.norm_cdf(d1)

    # --- Main Execution ---
    def run(self, state: Any) -> tuple[Dict[str, List[Any]], int, str]:
        result = {}
        conversions = 0

        # ==========================================
        # FIX 4: TIME TO EXPIRY (T) RESETS
        # Load and parse persistent state data to track the actual day
        # ==========================================
        trader_state = {"day": 0, "last_timestamp": -1, "hydrogel_history": []}
        if state.traderData:
            try:
                trader_state = json.loads(state.traderData)
            except:
                pass  # Fallback to defaults if parsing fails

        # Detect day rollover: if current timestamp is smaller than last seen, a new day started
        if state.timestamp < trader_state["last_timestamp"]:
            trader_state["day"] += 1

        trader_state["last_timestamp"] = state.timestamp

        # Calculate global time and scale T
        global_timestamp = (trader_state["day"] * 1000000) + state.timestamp
        time_to_expiry = max(0.00001, (self.TOTAL_TIME_STEPS - global_timestamp) / self.TOTAL_TIME_STEPS)

        # 1. Extract Underlying Asset Price
        underlying_asset = "VELVETFRUIT_EXTRACT"
        underlying_price = None
        if underlying_asset in state.order_depths:
            bids = state.order_depths[underlying_asset].buy_orders
            asks = state.order_depths[underlying_asset].sell_orders
            if bids and asks:
                best_bid = max(bids.keys())
                best_ask = min(asks.keys())
                underlying_price = (best_bid + best_ask) / 2.0

        # ==========================================
        # FIX 1: PORTFOLIO DELTA
        # Calculate delta of our ALREADY EXISTING inventory
        # ==========================================
        portfolio_delta = 0.0
        if underlying_price is not None:
            for product, current_pos in state.position.items():
                if product.startswith("VEV_"):
                    strike = float(product.split("_")[1])
                    opt_delta = self.calculate_delta(
                        S=underlying_price, K=strike, T=time_to_expiry, r=self.risk_free_rate, sigma=self.volatility
                    )
                    portfolio_delta += (opt_delta * current_pos)

        # ==========================================
        # FIX 3: LIMIT ORDERS FOR OPTIONS
        # Market making around the Fair Value to avoid crossing the spread
        # ==========================================
        for product in state.order_depths:
            if product.startswith("VEV_") and underlying_price is not None:
                strike = float(product.split("_")[1])
                theoretical_value = self.calculate_bs_call(
                    S=underlying_price, K=strike, T=time_to_expiry, r=self.risk_free_rate, sigma=self.volatility
                )

                # Check current position in this specific option to avoid limit breaches
                current_opt_pos = state.position.get(product, 0)

                orders = []
                # Define our edge margin (how much profit we want to bake into our quotes)
                edge = 2.0

                my_bid_price = math.floor(theoretical_value - edge)
                my_ask_price = math.ceil(theoretical_value + edge)

                # We can safely quote up to our position limits
                bid_qty = self.OPTION_LIMIT - current_opt_pos
                ask_qty = -self.OPTION_LIMIT - current_opt_pos

                # Place Limit Orders (Wait for other bots to cross the spread and trade with us)
                if bid_qty > 0:
                    orders.append(Order(product, my_bid_price, bid_qty))
                if ask_qty < 0:
                    orders.append(Order(product, my_ask_price, ask_qty))

                if orders:
                    result[product] = orders

        # ==========================================
        # FIX 2: POSITION LIMITS ON DELTA HEDGE
        # Aggressively hedge the underlying, but respect engine limits
        # ==========================================
        if underlying_price is not None:
            # We want our stock position to perfectly offset our options delta
            ideal_target_position = -int(round(portfolio_delta))

            # Clamp the target so we don't violate position limits
            clamped_target = max(-self.VELVET_LIMIT, min(self.VELVET_LIMIT, ideal_target_position))

            current_underlying_position = state.position.get(underlying_asset, 0)
            required_trade = clamped_target - current_underlying_position

            underlying_orders = []
            order_depth = state.order_depths[underlying_asset]

            # Because this is a hedge, we cross the spread (take liquidity) to ensure we are protected immediately
            if required_trade > 0 and len(order_depth.sell_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                underlying_orders.append(Order(underlying_asset, best_ask, required_trade))
            elif required_trade < 0 and len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())
                underlying_orders.append(Order(underlying_asset, best_bid, required_trade))

            if underlying_orders:
                result[underlying_asset] = underlying_orders

        # ==========================================
        # FIX 5: MEAN REVERSION INVENTORY MANAGER & STOP LOSS
        # ==========================================
        hydrogel = "HYDROGEL_PACK"
        if hydrogel in state.order_depths:
            bids = state.order_depths[hydrogel].buy_orders
            asks = state.order_depths[hydrogel].sell_orders

            if bids and asks:
                best_bid = max(bids.keys())
                best_ask = min(asks.keys())
                mid_price = (best_bid + best_ask) / 2.0

                # Update history
                trader_state["hydrogel_history"].append(mid_price)
                if len(trader_state["hydrogel_history"]) > 20:
                    trader_state["hydrogel_history"].pop(0)

                    sma = sum(trader_state["hydrogel_history"]) / len(trader_state["hydrogel_history"])
                    current_hydro_pos = state.position.get(hydrogel, 0)

                    # Stop-Loss: If it drifts more than 25 points, it's a trend, do not trade
                    if abs(mid_price - sma) <= 25:

                        # Inventory Management: The larger our position, the wider our required margin to trade more
                        # If we have 100 units, the required margin to buy more increases, making us more cautious
                        inventory_skew = current_hydro_pos * 0.1

                        hydrogel_orders = []
                        trade_qty = 10  # Tranche size

                        # Short Condition
                        if mid_price > (sma + 5.0 + inventory_skew):
                            allowed_short = -self.HYDROGEL_LIMIT - current_hydro_pos
                            qty_to_short = max(allowed_short, -trade_qty)  # Ensures we stay within bounds
                            if qty_to_short < 0:
                                hydrogel_orders.append(Order(hydrogel, best_bid, qty_to_short))

                        # Buy Condition
                        elif mid_price < (sma - 5.0 + inventory_skew):
                            allowed_long = self.HYDROGEL_LIMIT - current_hydro_pos
                            qty_to_buy = min(allowed_long, trade_qty)
                            if qty_to_buy > 0:
                                hydrogel_orders.append(Order(hydrogel, best_ask, qty_to_buy))

                        if hydrogel_orders:
                            result[hydrogel] = hydrogel_orders

        # Save state to string for next tick
        trader_data_out = json.dumps(trader_state)

        return result, conversions, trader_data_out