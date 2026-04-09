# Global Variables

ticker_columns = ("product", "symbol")

orderbook_columns = ("bid_price_1", "bid_price_2", "bid_price_3",
                     "bid_volume_1", "bid_volume_2", "bid_volume_3",
                     "ask_price_1", "ask_price_2", "ask_price_3",
                     "ask_volume_1", "ask_volume_2", "ask_volume_3"
                     )

orderbook_display_columns_vital = ("bid_price_1", "bid_volume_1",
                                   "ask_price_1", "ask_volume_1",
                                   "product")

plot_config = {
    "ask_price_3": ("v", "#ff2e2e", 6),
    "ask_price_2": ("v", "#d80000", 6),
    "ask_price_1": ("v", "#ff0000", 8.5),
    "mid_price": (".", "#000000", 10),
    "bid_price_1": ("^", "#00ff00", 8.5),
    "bid_price_2": ("^", "#00f00c", 6),
    "bid_price_3": ("^", "#00ec64", 6),
    "price": ("X", "#cc5500", 6.5)
}