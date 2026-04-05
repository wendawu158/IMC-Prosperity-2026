import tkinter as tk
from tkinter import ttk
import numpy as np


class StatisticsTab(tk.Frame):
    """
    Displays stats and the orderbook
    """

    def __init__(self, parent, graph_area):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=2)

        # Cursor location
        self.cursor_position = CursorPosition(self, graph_area)
        self.cursor_position.pack(side=tk.TOP, fill=tk.X, anchor=tk.NW)

        # The data
        self.graph_area = graph_area
        self.orderbook_data = graph_area.active_data
        self.current_orderbook_timestamp = None

        # The Orderbook
        self.orderbook = tk.Frame(self, relief=tk.RIDGE, borderwidth=2)
        self.canvas = tk.Canvas(self.orderbook)

        # The
        self.table = ttk.Frame(self.canvas)
        self.prices = []

        # The scrollbar
        self.scrollbar = ttk.Scrollbar(self.orderbook, orient=tk.VERTICAL, command=self.canvas.yview)
        self.table.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Letting the scrollbar scroll
        self.canvas.create_window((0, 0), window=self.table, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        self.orderbook.pack(side=tk.TOP, fill=tk.Y, expand=True)

        # Subscribe to mouse movements from the graph
        graph_area.mouse_motion_subscribers.append(self.update_orderbook)

    def update_orderbook(self, event):
        """
        Displays orderbook data
        """

        if event.inaxes and self.orderbook_data is not None and not self.orderbook_data.empty:
            timestamp = int(np.rint(event.xdata))


class CursorPosition(tk.Frame):
    """
    Little frame to display current location of cursor
    """

    def __init__(self, parent, graph_area):
        super().__init__(parent)

        # X and Y position
        self.label_x = tk.Label(self, text="Timestamp: ")
        self.label_y = tk.Label(self, text="Price: ")

        self.label_x.pack(side=tk.TOP, anchor=tk.NW, padx=5, pady=5)
        self.label_y.pack(side=tk.TOP, anchor=tk.NW, padx=5, pady=5)

        # Subscribe to mouse movements from the graph
        graph_area.mouse_motion_subscribers.append(self.update_coordinates)

    def update_coordinates(self, event):
        """
        Displays current x and y location of the cursor
        """

        # I want integers for nice display
        if event.inaxes:
            self.label_x.config(text=f"Timestamp: {int(np.rint(event.xdata))}")
            self.label_y.config(text=f"Price: {int(np.rint(event.ydata))}")
        else:
            self.label_x.config(text="Timestamp: Out of bounds")
            self.label_y.config(text="Price: Out of bounds")