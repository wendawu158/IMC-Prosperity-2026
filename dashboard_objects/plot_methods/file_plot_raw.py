# Functional imports
import numpy as np
import pandas as pd
from tkinter import messagebox
import re
from matplotlib.widgets import Cursor
from dashboard_objects.variables import *

# Parent imports
if False:
    from dashboard_objects.graph_area import GraphArea

def plot_raw_plot(plot: "GraphArea",
                    file_path: str,
                    traded_object: str):
    """
    The core plotting algorithm
    """

    trade_data: pd.DataFrame = process_file(plot, file_path, traded_object)

    if trade_data.empty:
        return

    # Plot new data
    for column in list(trade_data):
        if column in plot_config.keys():
            plot.ax.plot(trade_data.index,  # The time
                         trade_data[column],  # The data
                         plot_config[column][0],  # The marker
                         color=plot_config[column][1],  # The color of the plot
                         markersize=plot_config[column][2]  # The size of the marker
                         )

def process_file(plot: "GraphArea",
                 file_path: str,
                 traded_object: str) -> pd.DataFrame:

    trade_data = pd.DataFrame()

    # Looking for the file; does it exist?
    try:
        print(f"Plotting: File='{file_path}', Object='{traded_object}'")
        df = pd.read_csv(file_path, sep=";").set_index("timestamp")
    except FileNotFoundError:
        messagebox.showerror("Error", f"Could not find file: {file_path}\nPlease check your paths.")
        return pd.DataFrame()

    # If the file is empty
    if df.empty:
        print(f"Empty data in {file_path}")
        return pd.DataFrame()

    # Getting the days
    day = int(re.search(r"day_(.*)\.", file_path).group(1))

    # Changing the scale a bit, taking into account days
    # Removing unnecessary zeros
    df.index += day * 1e6
    df.index /= 100

    # Removing the days after the time data has been extracted
    # As it is now a redundant column

    if "day" in df.columns:
        df.drop("day", axis=1)

    # Getting the relevant data
    # We only want the data from the ticker we are interested in
    for ticker_option in ticker_columns:
        if ticker_option in df.columns:
            trade_data = df[df[ticker_option] == traded_object]
            break

    # If we don't have any data that matches
    if trade_data.empty:
        print(f"No matching data in {file_path}")

    # Removing midpoints if there isn't actually a bid/ask on that day
    if "mid_price" in trade_data.columns:
        no_bid = trade_data["bid_price_1"].isna() | (trade_data["bid_price_1"] == "")
        no_ask = trade_data["ask_price_1"].isna() | (trade_data["ask_price_1"] == "")
        trade_data.loc[no_bid, "mid_price"] = np.nan
        trade_data.loc[no_ask, "mid_price"] = np.nan

    # Getting the plotted data saved
    if "prices" in file_path:
        plot.active_orderbook_data = pd.concat([plot.active_orderbook_data, trade_data]).sort_index()
    elif "trades" in file_path:
        plot.active_trades_data = pd.concat([plot.active_trades_data, trade_data]).sort_index()

    return trade_data

def finish_raw_plot(plot: "GraphArea",
                     traded_object: str):
    """
    We run this at the end of plotting all the data we want to see
    This is to finish off the plot, add the bells and whistles
    """

    # Titles
    plot.ax.set_xlabel("Timestamp")
    plot.ax.set_ylabel("Price")
    plot.ax.set_title(f"{traded_object}")

    # Tickers
    plot.ax.callbacks.connect('xlim_changed', plot.on_xlims_change)
    plot.ax.callbacks.connect('ylim_changed', plot.on_ylims_change)

    # Gridlines
    plot.ax.grid(which='major', axis='x', color="#000000", alpha=0.5)
    plot.ax.grid(which='major', axis='y', color="#000000", alpha=0.5)
    plot.ax.grid(which='minor', axis='x', color="#202020", alpha=0.5)
    plot.ax.grid(which='minor', axis='y', color="#202020", alpha=0.5)

    # Disable scientific notation
    plot.ax.ticklabel_format(useOffset=False)

    # Re-apply crosshair cursor (since clearing axes destroys the old one)
    plot.ax.cursor = Cursor(plot.ax, useblit=True, horizOn=True, vertOn=True, color="#101010", linewidth=0.5)

    # Redraw canvas to autoscale axes to the new data
    plot.canvas.draw()

    plot.active_orderbook_data.to_csv("Debug Files/debug.csv")
