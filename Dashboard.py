import os
import re
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.widgets import Cursor
import matplotlib.ticker as ticker


# Global Variables
ticker_column_names = ("product", "symbol")


class OrderBookApp(tk.Tk):
    """
    The Root Application window
    """

    def __init__(self):
        super().__init__()

        # Sets the title
        self.wm_title("Dashboard")

        # Makes sure that everything closes when the window is closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialise Core Components
        self.graph_area = GraphArea(self)
        self.control_panel = ControlPanel(self, self.graph_area)

        # Pack Core Components
        self.graph_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.control_panel.pack(side=tk.LEFT, fill=tk.BOTH)

    def on_closing(self):
        """
        Shuts down matplotlib and the tkinter window
        """
        plt.close('all')
        self.destroy()


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

    def on_mouse_motion(self, event):
        """
        Handles cursor visibility and broadcasts mouse coordinates to other elements
        """

        # Notify subscribers (like the Statistics Tab)
        for callback in self.mouse_motion_subscribers:
            callback(event)

        # Cursor visibility
        # Ignore if panning
        # Weird bug happens if we don't ignore if panning
        if self.toolbar.mode != '':
            return

        if event.inaxes:
            self.canvas.get_tk_widget().config(cursor="none")
        else:
            self.canvas.get_tk_widget().config(cursor="arrow")


    def on_xlims_change(self, event):
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
        """The core plotting algorithm."""
        try:
            print(f"Plotting: File='{file_path}', Object='{traded_object}'")
            df = pd.read_csv(file_path, sep=";").set_index("timestamp")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not find file: {file_path}\nPlease check your paths.")
            return

        day = int(re.search(r"day_(.*)\.", file_path).group(1))

        df.index += day * 1e6
        df.index /= 100

        for ticker_option in ticker_column_names:
            if ticker_option in df.columns:
                TRADE_DATA = df[df[ticker_option] == traded_object]
                break

        if df.empty:
            print(f"Empty data in {file_path}")
            return

        plotConfig = {
            "ask_price_3":      ("v", "#50ff50"),
            "ask_price_2":      ("v", "#20ff20"),
            "ask_price_1":      ("v", "#00ff00"),
            "mid_price":        (".", "#000000"),
            "bid_price_1":      ("^", "#ff0000"),
            "bid_price_2":      ("^", "#ff2020"),
            "bid_price_3":      ("^", "#ff5050"),
            "price":            ("X", "#cc5500")
        }

        # Plot new data
        for column in list(TRADE_DATA):
            if column in plotConfig.keys():
                self.ax.plot(TRADE_DATA.index, TRADE_DATA[column], plotConfig[column][0], color=plotConfig[column][1])

    def finish_plot(self):
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

        # Everything selection
        self.selection_notebook = ttk.Notebook(self)

        self.refresh_files()


    def refresh_files(self):
        # Destroying everything correctly
        self.selection_notebook.destroy()

        # Resetting everything
        self.selection_notebook = ttk.Notebook(self)

        # File selection
        self.file_selection = tk.Frame(self.selection_notebook, relief=tk.RAISED)
        # A list of checkboxes for all the files
        self.file_checks = []
        self.file_checks_vars = []

        # Getting tickers frm every file
        # This is going to be a 2D-Array
        self.file_tickers = []

        # Ticker selection
        self.ticker_selection = tk.Frame(self.selection_notebook, relief=tk.RAISED)
        # Ticker selection radio buttons is handled by self.radio_refresh()

        # Adding the file selection page to the notebook
        # The ticker selection page will be added by a different func
        self.selection_notebook.add(self.file_selection, text="File Selection")
        self.selection_notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ticker_column_names = ["product", "symbol"]

        # Getting files
        for file_name in os.listdir("Data"):

            # Making sure that it's the right file ending (don't want any mishaps)
            if file_name[-4:] == ".csv":

                # Opening and checking all the column names seems right
                # This bit of code is to get the file checkboxes up
                with open(f"Data/{file_name}") as file:
                    column_names = file.readline().split(";")

                    # We want the timestamp as our index and a column telling us which ticker has been traded
                    # This will be for selection
                    if ("timestamp" in column_names and
                            bool(set(ticker_column_names) & set(column_names))
                        ):

                        # Adding checkmarks to see if we want to plot those files
                        self.file_checks_vars.append(
                            tk.StringVar()
                        )
                        self.file_checks.append(
                            tk.Checkbutton(self.file_selection, text=file_name, variable=self.file_checks_vars[-1], onvalue=file_name, offvalue="", command=self.radio_refresh)
                        )
                        self.file_checks[-1].pack(side=tk.TOP, anchor=tk.NW)
                    else:
                        continue

            # This bit of code is to get the ticker radio buttons up
            df = pd.read_csv(f"Data/{file_name}", sep=";")

            for ticker_column in ticker_column_names:
                if ticker_column in df.columns:
                    self.file_tickers.append(list(df[ticker_column].unique()))
                    break

        self.radio_refresh()


    def radio_refresh(self):

        # Destroying the ticker view to reset it
        self.ticker_selection.destroy()

        # Recreating it
        self.ticker_selection = tk.Frame(self.selection_notebook, relief=tk.RAISED)

        # A list of radio buttons for all the traded objects
        # Radio buttons are mutually exclusive
        self.ticker_radios = []
        self.ticker_selected = tk.StringVar()

        # All tickers that can be found in the files in the Data Folder
        self.relevant_tickers = set()

        # For every single checkbox, loop and get the tickers from those files
        for is_checked in range(0, len(self.file_checks_vars)):
            if self.file_checks_vars[is_checked].get() != "":

                # Adding to the ticker list displayed
                self.relevant_tickers.update(
                    set(self.file_tickers[is_checked])
                )

        # Actually displaying the tickers
        for ticker in sorted(self.relevant_tickers):

            # Setting the default one to be the first one
            if self.ticker_selected.get() == "":
                self.ticker_selected.set(ticker)

            # Setting up the radio buttons
            self.ticker_radios.append(tk.Radiobutton(self.ticker_selection, text=ticker, variable=self.ticker_selected, value=ticker))
            self.ticker_radios[-1].pack(side=tk.TOP, anchor=tk.NW)

        # Adding the page to the notebook
        self.selection_notebook.add(self.ticker_selection, text="Ticker Selection")



    def trigger_plot(self):
        # Clear the old data so the axes can reset
        self.graph_area.ax.clear()

        # Plots all the files
        for file in self.file_checks_vars:
            if file.get() != "":
                print(f"plotting {file.get()}")
                self.graph_area.plot_order_book(f"Data/{file.get()}", self.ticker_selected.get())

        self.graph_area.finish_plot()


class StatisticsTab(tk.Frame):
    """Displays real-time stats like mouse position."""

    def __init__(self, parent, graph_area):
        super().__init__(parent, relief=tk.RAISED)

        # X and Y position
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