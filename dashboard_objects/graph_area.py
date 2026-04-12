# Functionality imports
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.widgets import Cursor
import matplotlib.ticker as ticker
from typing import List

# Child imports
from dashboard_objects.plot_methods.file_plot_raw import plot_raw_plot, finish_raw_plot

# Parent imports
if False:
    from dashboard_objects.window import OrderbookApp


class GraphArea(tk.Frame):
    """
    Encapsulates the Matplotlib figure, canvas, and toolbar
    """

    def __init__(self,
                 parent: "OrderbookApp"):
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

        # Allow objects to subscribe to mouse movement
        self.mouse_motion_subscribers: List[callable(tk.Event)] = [self.cursor_display]

        # Track active data for the order book visualizer
        self.active_orderbook_data: pd.DataFrame = pd.DataFrame()
        self.active_trades_data: pd.DataFrame = pd.DataFrame()

    def on_mouse_motion(self, event) -> None:
        """
        Handles cursor movement by broadcasting mouse coordinates to other elements
        """

        # Notify subscribers (like the Statistics Tab)
        for callback in self.mouse_motion_subscribers:
            callback(event)

    def cursor_display(self, event) -> None:
        """
        Shows the crosshair cursor
        """

        # Cursor visibility
        # Weird bug happens if we don't ignore if panning
        if self.toolbar.mode != '':
            return

        # Changes the cursor
        if event.inaxes:
            self.canvas.get_tk_widget().config(cursor="none")
        else:
            self.canvas.get_tk_widget().config(cursor="arrow")

    @staticmethod
    def on_xlims_change(event) -> None:
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

    @staticmethod
    def on_ylims_change(event) -> None:
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

    def plot_raw_plot(self,
                      file_path: str,
                      traded_object: str) -> None:
        """
        Plotting raw files (not editing the data)
        """
        plot_raw_plot(self, file_path, traded_object)

    def finish_raw_plot(self,
                        traded_object: str) -> None:
        """
        Finishing off the orderbook plot
        """
        finish_raw_plot(self, traded_object)

    def clear(self) -> None:
        self.ax.clear()

        # Removing the saved data
        self.active_orderbook_data = pd.DataFrame()

    def annotate(self) -> None:
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

    def __init__(self,
                 targetCanvas: "FigureCanvasTkAgg",
                 parent: "GraphArea"):
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
