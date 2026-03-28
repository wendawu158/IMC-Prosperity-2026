import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.widgets import Cursor


class OrderBookApp(tk.Tk):
    """
    The Root Application window
    """

    def __init__(self):
        super().__init__()
        self.wm_title("Order Book Visualiser")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialise Core Components
        self.graph_area = GraphArea(self)
        self.control_panel = ControlPanel(self, self.graph_area)

        # Pack Core Components
        self.graph_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.control_panel.pack(side=tk.LEFT, fill=tk.BOTH)

    def on_closing(self):
        """
        Safely shuts down matplotlib and the tkinter window
        """
        plt.close('all')
        self.destroy()


class GraphArea(tk.Frame):
    """
    Encapsulates the Matplotlib figure, canvas, and toolbar.
    """

    def __init__(self, parent):
        super().__init__(parent)

        # Setup Figure and Axes
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(left=0.05, bottom=0.07, right=0.95, top=0.95, wspace=0, hspace=0)

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
        self.setup_cursor()

        # Event bindings
        self.canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed {event.key}"))
        self.canvas.mpl_connect("key_press_event", key_press_handler)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_motion)

        # Allow other objects to subscribe to mouse movement
        self.mouse_motion_subscribers = []

    def setup_cursor(self):
        """
        Re-initialises the cursor
        Required after ax.clear() is called
        """
        self.ax.cursor = Cursor(self.ax, useblit=True, horizOn=True, vertOn=True, color="#101010", linewidth=0.5)

    def on_mouse_motion(self, event):
        """Handles cursor visibility and broadcasts mouse coordinates."""
        if self.toolbar.mode != '':
            return

        if event.inaxes:
            self.canvas.get_tk_widget().config(cursor="none")
        else:
            self.canvas.get_tk_widget().config(cursor="arrow")

        # Notify subscribers (like the Statistics Tab)
        for callback in self.mouse_motion_subscribers:
            callback(event)

    def plot_order_book(self, file_path, traded_object):
        """The core plotting algorithm."""
        try:
            print(f"Plotting: File='{file_path}', Object='{traded_object}'")
            df = pd.read_csv(file_path, sep=";").set_index("timestamp")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not find file: {file_path}\nPlease check your paths.")
            return

        # Clear the old data so the axes can reset
        self.ax.clear()

        df["bids"] = df["bid_volume_1"].fillna(0) + df["bid_volume_2"].fillna(0) + df["bid_volume_3"].fillna(0)
        df["asks"] = df["ask_volume_1"].fillna(0) + df["ask_volume_2"].fillna(0) + df["ask_volume_3"].fillna(0)

        TRADE_DATA = df[df["product"] == traded_object]

        plotConfig = {
            "ask_price_3":      ("v", "#50ff50"),
            "ask_price_2":      ("v", "#20ff20"),
            "ask_price_1":      ("v", "#00ff00"),
            "mid_price":        (".", "#000000"),
            "bid_price_1":      ("^", "#ff0000"),
            "bid_price_2":      ("^", "#ff2020"),
            "bid_price_3":      ("^", "#ff5050"),
        }
        # Plot new data
        for column in list(TRADE_DATA):
            if column in plotConfig.keys():
                self.ax.plot(TRADE_DATA.index, TRADE_DATA[column], plotConfig[column][0], color=plotConfig[column][1])

        # Re-apply crosshair cursor (since clearing axes destroys the old one)
        self.setup_cursor()

        # Redraw canvas to autoscale axes to the new data
        self.canvas.draw()


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


class ControlPanel(ttk.Notebook):
    """
    The main side panel housing all control tabs.
    """

    def __init__(self, parent, graph_area):
        super().__init__(parent)
        self.configure(width=300)

        # Initialize tabs
        self.data_tab = DataTab(self, graph_area)
        self.stats_tab = StatisticsTab(self, graph_area)
        self.window3_tab = Window3Tab(self)

        # Add tabs to notebook
        self.add(self.data_tab, text="Data")
        self.add(self.stats_tab, text="Statistics")
        self.add(self.window3_tab, text="Window 3")


class DataTab(tk.Frame):
    """
    Data selection and triggering plots
    """

    def __init__(self, parent, graph_area):
        super().__init__(parent, relief=tk.RAISED)
        self.graph_area = graph_area

        # Buttons Housing
        self.data_button_housing = tk.Frame(self)

        # Plot Button
        self.plot_button = tk.Button(self.data_button_housing, relief=tk.RAISED, text="Plot Data Selection", command=self.trigger_plot)
        self.plot_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.refresh_button = tk.Button(self.data_button_housing, relief=tk.RAISED, text="Refresh File Selection", command=self.refresh_files)
        self.refresh_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.data_button_housing.pack(side=tk.TOP, fill=tk.X)

        # Setting everything for the first time, so that the command refresh_files
        # can destroy everything properly
        self.selection_notebook = ttk.Notebook(self)
        self.file_selection = tk.Frame(self.selection_notebook, relief=tk.RAISED)
        self.object_selection = tk.Frame(self.selection_notebook, relief=tk.RAISED)

        self.selection_notebook.add(self.file_selection, text="File Selection")
        self.selection_notebook.add(self.object_selection, text="Object Selection")
        self.selection_notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def refresh_files(self):

        # Destroying everything correctly
        self.selection_notebook.destroy()

        self.selection_notebook = ttk.Notebook(self)
        self.file_selection = tk.Frame(self.selection_notebook, relief=tk.RAISED)
        self.object_selection = tk.Frame(self.selection_notebook, relief=tk.RAISED)

        self.selection_notebook.add(self.file_selection, text="File Selection")
        self.selection_notebook.add(self.object_selection, text="Object Selection")
        self.selection_notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for file in os.listdir("Data"):
            print(file)


    def trigger_plot(self):
        # Currently hardcoded, ready for you to link to UI dropdowns/listboxes!
        self.graph_area.plot_order_book("Data/prices_round_0_day_-1.csv", "TOMATOES")


class StatisticsTab(tk.Frame):
    """Displays real-time stats like mouse position."""

    def __init__(self, parent, graph_area):
        super().__init__(parent, relief=tk.RAISED)

        self.label_x = tk.Label(self, text="x: ")
        self.label_y = tk.Label(self, text="y: ")

        self.label_x.pack(side=tk.TOP, anchor=tk.NW, padx=5, pady=5)
        self.label_y.pack(side=tk.TOP, anchor=tk.NW, padx=5, pady=5)

        # Subscribe to mouse movements from the graph
        graph_area.mouse_motion_subscribers.append(self.update_coordinates)

    def update_coordinates(self, event):
        if event.inaxes:
            self.label_x.config(text=f"x: {int(event.xdata)}")
            self.label_y.config(text=f"y: {int(event.ydata)}")
        else:
            self.label_x.config(text="x: Out of bounds")
            self.label_y.config(text="y: Out of bounds")


class Window3Tab(tk.Frame):
    """
    Placeholder for future functionality
    """

    def __init__(self, parent):
        super().__init__(parent, relief=tk.RAISED)
        self.label = tk.Label(self, text="Window 3 Content")
        self.label.pack(padx=5, pady=5)


if __name__ == "__main__":
    app = OrderBookApp()
    app.mainloop()