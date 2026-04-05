import tkinter as tk
import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.widgets import Cursor
import matplotlib.ticker as ticker
from dashboard_objects.variables import ticker_column_names

class GraphArea(tk.Frame):
    """
    Encapsulates the Matplotlib figure, canvas, and toolbar
    """

    def __init__(self, parent):
        super().__init__(parent)

        # Setup Figure and Axes
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(left=0.08, bottom=0.1, right=0.99, top=0.95, wspace=0, hspace=0)

        # Setup Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()

        # Setup Toolbar
        self.toolbar = VerticalNavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()

        # Packing
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Initialise Cursor
        self.ax.cursor = Cursor(self.ax, useblit=True, horizOn=True, vertOn=True, color="#101010", linewidth=0.5)

        # Event bindings
        self.canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed {event.key}"))
        self.canvas.mpl_connect("key_press_event", key_press_handler)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_motion)

        # Allow other objects to subscribe to mouse movement
        self.mouse_motion_subscribers = []

        # Track active data for the order book visualizer
        self.active_data = None

    def on_mouse_motion(self, event):
        """
        Handles cursor visibility and broadcasts mouse coordinates to other elements
        """

        # Notify subscribers (like the Statistics Tab)
        for callback in self.mouse_motion_subscribers:
            callback(event)

        # Cursor visibility
        # Weird bug happens if we don't ignore if panning
        if self.toolbar.mode != '':
            return

        # Changes the cursor
        if event.inaxes:
            self.canvas.get_tk_widget().config(cursor="none")
        else:
            self.canvas.get_tk_widget().config(cursor="arrow")


    def on_xlims_change(self, event):
        """
        Changes the timestamp scale
        """

        # Get the current view range
        xmin, xmax = event.get_xlim()
        view_width = xmax - xmin

        # Logic for pre-chosen scales
        if view_width <= 20:
            spacing = 1
        elif view_width <= 40:
            spacing = 2
        elif view_width <= 100:
            spacing = 5
        elif view_width <= 200:
            spacing = 10
        elif view_width <= 400:
            spacing = 20
        elif view_width <= 1000:
            spacing = 50
        elif view_width <= 2000:
            spacing = 100
        elif view_width <= 4000:
            spacing = 200
        elif view_width <= 10000:
            spacing = 500
        elif view_width <= 20000:
            spacing = 1000
        elif view_width <= 40000:
            spacing = 2000
        elif view_width <= 100000:
            spacing = 5000
        else:
            spacing = 10000

        # Apply the new scale
        event.xaxis.set_major_locator(ticker.MultipleLocator(spacing))
        if spacing > 2:
            event.xaxis.set_minor_locator(ticker.MultipleLocator(spacing // 5))
        elif spacing > 1:
            event.xaxis.set_minor_locator(ticker.MultipleLocator(spacing // 2))

    def on_ylims_change(self, event):
        """
        Changes the price scale
        """

        # Get the current view range
        ymin, ymax = event.get_ylim()
        view_width = ymax - ymin

        # Logic for pre-chosen scales
        if view_width <= 20:
            spacing = 1
        elif view_width <= 40:
            spacing = 2
        elif view_width <= 100:
            spacing = 5
        elif view_width <= 200:
            spacing = 10
        else:
            spacing = 20

        # Apply the new scale
        event.yaxis.set_major_locator(ticker.MultipleLocator(spacing))
        if spacing > 2:
            event.yaxis.set_minor_locator(ticker.MultipleLocator(spacing // 5))
        elif spacing > 1:
            event.yaxis.set_minor_locator(ticker.MultipleLocator(spacing // 2))

    def plot_order_book(self, file_path, traded_object):
        """
        The core plotting algorithm
        """

        # Looking for the file; does it exist?
        try:
            print(f"Plotting: File='{file_path}', Object='{traded_object}'")
            df = pd.read_csv(file_path, sep=";").set_index("timestamp")
        except FileNotFoundError:
            tk.messagebox.showerror("Error", f"Could not find file: {file_path}\nPlease check your paths.")
            return

        # If the file is empty
        if df.empty:
            print(f"Empty data in {file_path}")
            return

        # Getting the days
        day = int(re.search(r"day_(.*)\.", file_path).group(1))

        # Changing the scale a bit, taking into account days
        # Removing unnecessary zeros
        df.index += day * 1e6
        df.index /= 100

        # Getting the relevant data
        # We only want the data from the ticker we are interested in
        for ticker_option in ticker_column_names:
            if ticker_option in df.columns:
                TRADE_DATA = df[df[ticker_option] == traded_object]
                break

        # If we don't have any data that matches
        if TRADE_DATA.empty:
            print(f"No matching data in {file_path}")
            return

        # Getting the plotted data saved
        if self.active_data is None:
            self.active_data = TRADE_DATA.copy()
        else:
            self.active_data = pd.concat([self.active_data, TRADE_DATA]).sort_index()
            # Remove any duplicated timestamps due to concatenation
            self.active_data = self.active_data[~self.active_data.index.duplicated(keep='last')]

        plotConfig = {
            "ask_price_3":      ("v", "#ff2e2e", 6),
            "ask_price_2":      ("v", "#d80000", 6),
            "ask_price_1":      ("v", "#ff0000", 8.5),
            # "mid_price":        (".", "#000000", 10),
            "bid_price_1":      ("^", "#00ff00", 8.5),
            "bid_price_2":      ("^", "#00f00c", 6),
            "bid_price_3":      ("^", "#00ec64", 6),
            "price":            ("X", "#cc5500", 6.5)
        }

        # Plot new data
        for column in list(TRADE_DATA):
            if column in plotConfig.keys():
                self.ax.plot(TRADE_DATA.index,          # The time
                            TRADE_DATA[column],               # The data
                            plotConfig[column][0],            # The marker
                            color=plotConfig[column][1],      # The color of the plot
                            markersize=plotConfig[column][2]  # The size of the marker
                            )

    def finish_plot(self, traded_object):
        """
        We run this at the end of plotting all the data we want to see
        This is to finish off the plot, add the bells and whistles
        """

        # Titles
        self.ax.set_xlabel("Timestamp")
        self.ax.set_ylabel("Price")
        self.ax.set_title(f"{traded_object}")

        # Tickers
        self.ax.callbacks.connect('xlim_changed', self.on_xlims_change)
        self.ax.callbacks.connect('ylim_changed', self.on_ylims_change)

        # Gridlines
        self.ax.grid(which='major', axis='x', color="#000000", alpha=0.5)
        self.ax.grid(which='major', axis='y', color="#000000", alpha=0.5)
        self.ax.grid(which='minor', axis='x', color="#202020", alpha=0.5)
        self.ax.grid(which='minor', axis='y', color="#202020", alpha=0.5)

        # Disable scientific notation
        self.ax.ticklabel_format(useOffset=False)

        # Re-apply crosshair cursor (since clearing axes destroys the old one)
        self.ax.cursor = Cursor(self.ax, useblit=True, horizOn=True, vertOn=True, color="#101010", linewidth=0.5)

        # Redraw canvas to autoscale axes to the new data
        self.canvas.draw()

    def annotate(self):
        """
        Future function to show more information on trades and orders
        """

        pass

class VerticalNavigationToolbar2Tk(NavigationToolbar2Tk):
    """
    This is so that I can have a vertical toolbar with evil OOP magic
    hehehehehehehe
    Thanks @acw1668 from stackoverflow
    """

    def __init__(self, targetCanvas, parent):
        super().__init__(targetCanvas, parent, pack_toolbar=False)

    # override _Button() to re-pack the toolbar button in vertical direction
    def _Button(self, text, image_file, toggle, command):
        b = super()._Button(text, image_file, toggle, command)
        b.pack(side=tk.TOP)  # re-pack button in vertical direction
        return b

    # override _Spacer() to create vertical separator
    def _Spacer(self):
        s = tk.Frame(self, width=26, relief=tk.RIDGE, bg="DarkGray", padx=2)
        s.pack(side=tk.TOP, pady=5)  # pack in vertical direction
        return s

    # disable showing mouse position in toolbar
    def set_message(self, s):
        pass


