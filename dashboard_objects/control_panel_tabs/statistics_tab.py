import tkinter as tk
from tkinter import ttk
import numpy as np

if False:
    from dashboard_objects.control_panel import ControlPanel
    from dashboard_objects.graph_area import GraphArea


class StatisticsTab(tk.Frame):
    """
    Displays stats and the orderbook
    """

    def __init__(self,
                 parent: "ControlPanel",
                 graph_area: "GraphArea"):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=2)

        # Cursor location
        self.cursor_position = CursorPosition(self, graph_area)
        self.cursor_position.pack(side=tk.TOP, fill=tk.X, anchor=tk.NW)

        # The data
        self.graph_area = graph_area
        self.orderbook_data = graph_area.active_orderbook_data
        self.current_orderbook_timestamp = None

        # The Orderbook
        self.orderbook = OrderbookDisplay(self, graph_area)
        self.orderbook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class CursorPosition(tk.Frame):
    """
    Little frame to display current location of cursor
    """

    def __init__(self,
                 parent: StatisticsTab,
                 graph_area: "GraphArea"):
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


class OrderbookDisplay(tk.Frame):
    """
    Display for Orderbook at cursor location
    """

    def __init__(self,
                 parent: StatisticsTab,
                 graph_area: "GraphArea"):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=2)


        self.orderbook_data = graph_area.active_orderbook_data
        self.current_orderbook_timestamp = None

        self.orderbook_canvas = tk.Canvas(self)
        self.orderbook_table = tk.Frame(self.orderbook_canvas)
        self.prices = []

        # The scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.orderbook_table,
            orient=tk.VERTICAL,
            command=self.orderbook_canvas.yview
        )

        # Binding the scrollbar
        self.orderbook_table.bind(
            "<Configure>",
            lambda e:
            self.orderbook_canvas.configure(
                scrollregion=self.orderbook_canvas.bbox("all")
            )
        )

        # Letting the scrollbar scroll
        self.orderbook_canvas.create_window(
            (0, 0),
            window=self.orderbook_table,
            anchor=tk.NW)
        self.orderbook_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orderbook_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        self.orderbook_table.pack(side=tk.TOP, fill=tk.Y, expand=True)

        # Subscribe to mouse movements from the graph
        graph_area.mouse_motion_subscribers.append(self.update_orderbook)

    def update_orderbook(self, event):
        """
        Displays orderbook data
        """

        # Cleans data
        orderbook_data_clean = self.orderbook_data


        if event.inaxes and self.orderbook_data is not None and not self.orderbook_data.empty:
            timestamp = int(np.rint(event.xdata))
            timestamp_info = self.orderbook_data.loc[timestamp]


