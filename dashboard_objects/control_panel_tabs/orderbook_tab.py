import tkinter as tk
from tkinter import ttk
import numpy as np

from dashboard_objects.variables import bid_prices, ask_prices, bid_volumes, ask_volumes

if False:
    from dashboard_objects.control_panel import ControlPanel
    from dashboard_objects.graph_area import GraphArea


class OrderbookTab(tk.Frame):
    """
    Displays stats and the orderbook
    """

    def __init__(self,
                 parent: "ControlPanel",
                 graph_area: "GraphArea"):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=2)
        self.parent = parent

        # Cursor location
        self.cursor_position_display = CursorPositionDisplay(self, graph_area)
        self.cursor_position_display.pack(side=tk.TOP, fill=tk.X, anchor=tk.NW)

        # The data
        self.graph_area = graph_area
        self.orderbook_data = graph_area.active_orderbook_data
        self.current_orderbook_timestamp = None

        # The Orderbook
        self.orderbook = OrderbookDisplay(self, graph_area)
        self.orderbook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Orderbook control bar
        self.orderbook_display_controls = OrderbookDisplayControls(self, graph_area)
        self.orderbook_display_controls.pack(side=tk.TOP, fill=tk.X)


class CursorPositionDisplay(tk.Frame):
    """
    Little frame to display current location of cursor
    """

    def __init__(self,
                 parent: OrderbookTab,
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


class OrderbookDisplayControls(tk.Frame):
    """
    Buttons and controls for our orderbook display
    """

    def __init__(self,
                 parent: "OrderbookTab",
                 graph_area: "GraphArea"):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=2)

        # Inheritance (Luke I am your father)
        self.parent = parent
        self.graph_area = graph_area

        self.lock_information_button = tk.Button(self, text="Lock\nInformation", relief='raised', underline=5,
                                                 command=self.lock_information_button_func)
        self.lock_orderbook_view_button = tk.Button(self, text="Lock\nOrderbook\nView", relief='raised', underline=5,
                                                    command=self.lock_orderbook_view_button_func)
        self.collapse_zeros_button = tk.Button(self, text="Collapse\nZeros", relief='raised', underline=5,
                                               command=self.collapse_zeros_button_func)

        self.is_locked_information = False
        self.is_locked_view = False
        self.is_collapse_zeros = False

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.lock_information_button.grid(row=0, column=0, sticky=tk.NSEW)
        self.lock_orderbook_view_button.grid(row=0, column=1, sticky=tk.NSEW)
        self.collapse_zeros_button.grid(row=0, column=2, sticky=tk.NSEW)

        self.parent.parent.parent.bind("<Key>", self.key_press)

    def key_press(self, event: tk.Event):
        match event.char:
            case "i":
                self.lock_information_button_func()
            case "o":
                self.lock_orderbook_view_button_func()
            case "p":
                self.collapse_zeros_button_func()


    def lock_information_button_func(self):
        if self.lock_information_button.config('relief')[-1] == 'sunken':
            self.lock_information_button.config(relief='raised')
            self.is_locked_information = False
        else:
            self.lock_information_button.config(relief='sunken')
            self.is_locked_information = True

    def lock_orderbook_view_button_func(self):
        if self.lock_orderbook_view_button.config('relief')[-1] == 'sunken':
            self.lock_orderbook_view_button.config(relief='raised')
            self.is_locked_view = False
        else:
            self.lock_orderbook_view_button.config(relief='sunken')
            self.is_locked_view = True

    def collapse_zeros_button_func(self):
        if self.collapse_zeros_button.config('relief')[-1] == 'sunken':
            self.collapse_zeros_button.config(relief='raised')
            self.is_collapse_zeros = False
        else:
            self.collapse_zeros_button.config(relief='sunken')
            self.is_collapse_zeros = True



class OrderbookDisplay(tk.Frame):
    """
    Display for Orderbook at cursor location
    """

    def __init__(self,
                 parent: OrderbookTab,
                 graph_area: "GraphArea"):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=2)

        # References to other info
        self.parent = parent
        self.graph_area = graph_area
        self.current_orderbook_timestamp = 0

        # Orderbook info
        self.prices: list[tk.Label] = []
        self.volumes: list[dict[str, tk.Canvas | int]] = []
        self.max_vol = 0
        self.min_price = 0
        self.max_price = 0
        self.time_bounds: tuple[int, int] = (0, 0)
        self.canvas_width = 0

        # Scrolling Functionality
        self.orderbook_canvas = tk.Canvas(self)
        # The scrollbar
        self.scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.orderbook_canvas.yview
        )

        self.orderbook_table = tk.Frame(self.orderbook_canvas)

        self.orderbook_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orderbook_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Letting the scrollbar scroll
        self.orderbook_canvas.create_window(
            (0, 0),
            window=self.orderbook_table,
            anchor=tk.NW,
            )

        # Binding the scrollbar
        self.orderbook_table.bind(
            "<Configure>",
            lambda e:
            self.orderbook_canvas.configure(
                scrollregion=self.orderbook_canvas.bbox("all")
            )
        )
        # Subscribe to mouse movements from the graph
        graph_area.mouse_motion_subscribers.append(self.update_orderbook)

    def set_orderbook(self):
        # Clear existing widgets
        for widget in self.orderbook_table.winfo_children():
            widget.destroy()
        self.prices.clear()
        self.volumes.clear()

        # Get data
        data = self.graph_area.active_orderbook_data
        if data.empty:
            return

        self.min_price = int(data[bid_prices].min().min())
        self.max_price = int(data[ask_prices].max().max())

        self.max_vol = int(data[bid_volumes + ask_volumes].max().max())

        self.time_bounds = (int(data.index.min()), int(data.index.max()))

        # Create a vertical separator that spans all rows
        ttk.Separator(self.orderbook_table, orient=tk.VERTICAL).grid(
            row=0, column=1, rowspan=(self.max_price - self.min_price + 1), sticky=tk.NS, padx=5
        )

        # We want the bars to take up all the empty space
        self.orderbook_table.columnconfigure(0, weight=0)
        self.orderbook_table.columnconfigure(1, weight=0)
        self.orderbook_table.columnconfigure(2, weight=10)

        # Going through every price possible
        for i, price in enumerate(range(self.max_price, self.min_price - 1, -1)):
            # Price Label
            lbl = tk.Label(self.orderbook_table, text=f"{price}:")
            lbl.grid(column=0, row=i, sticky=tk.E)
            self.prices.append(lbl)

            # Volume Bar (Canvas)
            # Fixed width for the 'column', height matches label
            c = tk.Canvas(self.orderbook_table, height=20, highlightthickness=0)
            c.grid(column=2, row=i, sticky=tk.NSEW, columnspan=10)

            # Create a rectangle we can resize later (initial width 0)
            # We store the ID of the rectangle and the canvas itself
            rect_id = c.create_rectangle(0, 0, 0, 20, fill="skyblue", outline="")
            text_id = c.create_text(5, 10, anchor=tk.W, text="0")

            self.volumes.append({"canvas": c, "rect": rect_id, "text": text_id})

        self.orderbook_table.update_idletasks()
        self.orderbook_canvas.configure(scrollregion=self.orderbook_canvas.bbox("all"))
        self.canvas_width = self.volumes[0]["canvas"].winfo_width()


    def update_orderbook(self, event):
        orderbook_data = self.graph_area.active_orderbook_data
        if not event.inaxes or orderbook_data.empty:
            return

        if self.parent.orderbook_display_controls.is_locked_information:
            return

        timestamp = int(np.rint(event.xdata))

        # Simple check to ensure timestamp is in index
        if timestamp < self.time_bounds[0] or timestamp > self.time_bounds[1]:
            return

        row_data = orderbook_data.loc[timestamp].fillna(-1)

        for bar in self.volumes:
            # Update the rectangle size
            bar["canvas"].coords(bar["rect"], 0, 0, 0, 20)
            bar["canvas"].itemconfig(bar["text"], text=str(0))

        for label in range(len(bid_prices)):
            price = int(row_data[bid_prices[label]])
            volume = int(row_data[bid_volumes[label]])

            if price == -1:
                break

            bar = self.volumes[self.max_price - price]

            new_width = (volume / self.max_vol) * self.canvas_width

            bar["canvas"].coords(bar["rect"], 0, 0, new_width, 20)
            bar["canvas"].itemconfig(bar["text"], text=str(volume))
            bar["canvas"].itemconfig(bar["rect"], fill="#008000")


        for label in range(len(ask_prices)):
            price = int(row_data[ask_prices[label]])
            volume = int(row_data[ask_volumes[label]])

            if price == -1:
                break

            bar = self.volumes[self.max_price - price]

            new_width = (volume / self.max_vol) * self.canvas_width

            bar["canvas"].coords(bar["rect"], 0, 0, new_width, 20)
            bar["canvas"].itemconfig(bar["text"], text=str(volume))
            bar["canvas"].itemconfig(bar["rect"], fill="#FF0000")
