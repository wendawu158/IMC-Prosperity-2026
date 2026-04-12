# Functional Imports
import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
from dashboard_objects.variables import *

# Parental Imports
if False:
    from dashboard_objects.control_panel import ControlPanel
    from dashboard_objects.graph_area import GraphArea


class DataTab(tk.Frame):
    """
    Handles data processing
    """

    def __init__(self,
                 parent: "ControlPanel",
                 graph_area: "GraphArea"):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=2)

        self.parent = parent

        # To reference the graph object
        self.graph_area = graph_area

        # Buttons Housing
        self.data_button_housing = DataButtonHousing(self)
        self.data_button_housing.pack(side=tk.TOP, fill=tk.X)

        # Setting everything for the first time, so that the command refresh_files
        # can destroy everything properly

        # Selecting historical data
        self.selection_notebook = SelectionNotebook(self)
        self.refresh_files()

    def refresh_files(self) -> None:
        self.selection_notebook.refresh_files()

    def trigger_orderbook(self) -> None:
        self.selection_notebook.trigger_orderbook()


class DataButtonHousing(tk.Frame):
    """
    Holds the buttons for data refresh
    """

    def __init__(self,
                 parent: "DataTab"):
        super().__init__(parent)

        # Plot Button
        self.plot_button = tk.Button(self,
                                     relief=tk.RAISED,
                                     text="Plot Data Selection",
                                     command=parent.trigger_orderbook)
        self.refresh_button = tk.Button(self,
                                        relief=tk.RAISED,
                                        text="Refresh File Selection",
                                        command=parent.refresh_files)

        # Packing the plot button
        self.plot_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.refresh_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)


class SelectionNotebook(ttk.Notebook):
    """
    Selection notebook for files
    """

    def __init__(self,
                 parent: "DataTab"):
        super().__init__(parent)
        self.parent = parent

        self.refresh_files()

    def refresh_files(self) -> None:
        """
        Refreshing the files, if we update the Data directory
        """

        # Destroying everything correctly
        self.destroy()

        # Resetting everything
        super().__init__(self.parent)

        # File selection
        self.file_selection = tk.Frame(self, relief=tk.RIDGE, borderwidth=2)
        # A list of checkboxes for all the files
        self.file_checks: list[tk.Checkbutton] = []
        self.file_checks_vars: list[tk.StringVar] = []

        # Getting tickers form every file
        # This is going to be a 2D-Array
        self.file_tickers: list[list[str]] = []

        # Ticker selection
        self.ticker_selection = tk.Frame(self, relief=tk.RIDGE, borderwidth=2)
        # Ticker selection radio buttons is handled by self.radio_refresh()

        # Adding the file selection page to the notebook
        # The ticker selection page will be added by a different func
        self.add(self.file_selection, text="File Selection")
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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
                            bool(set(ticker_columns) & set(column_names))
                    ):

                        # Adding checkmarks to see if we want to plot those files
                        self.file_checks_vars.append(
                            tk.StringVar()
                        )
                        self.file_checks.append(
                            tk.Checkbutton(self.file_selection, text=file_name, variable=self.file_checks_vars[-1],
                                           onvalue=file_name, offvalue="", command=self.radio_refresh)
                        )
                        self.file_checks[-1].pack(side=tk.TOP, anchor=tk.NW)
                    else:
                        continue

            # This bit of code is to get the ticker radio buttons up
            df = pd.read_csv(f"Data/{file_name}", sep=";")

            # Check if we have tickers we want
            for ticker_column in ticker_columns:
                if ticker_column in df.columns:
                    # Add tickers
                    self.file_tickers.append(list(df[ticker_column].unique()))
                    break

        # Refresh radio buttons (by default)
        self.radio_refresh()

    def radio_refresh(self) -> None:
        """
        Changing the radio buttons on display based on which checkboxes have been checked
        """

        # Destroying the ticker view to reset it
        self.ticker_selection.destroy()

        # Recreating it
        self.ticker_selection = tk.Frame(self, relief=tk.RIDGE, borderwidth=2)

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
        self.add(self.ticker_selection, text="Ticker Selection")

    def trigger_orderbook(self) -> None:
        """
        Getting the plots to be plotted
        """

        # Clear the old graph so the axes can reset
        self.parent.graph_area.clear()

        # Plots all the files
        for file in self.file_checks_vars:
            if file.get() != "":
                print(f"plotting {file.get()}")
                self.parent.graph_area.plot_raw_plot(f"Data/{file.get()}", self.ticker_selected.get())

        self.parent.graph_area.finish_raw_plot(self.ticker_selected.get())

        self.parent.parent.stats_tab.orderbook.set_orderbook()
