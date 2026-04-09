# Child imports
from tkinter import ttk
from dashboard_objects.control_panel_tabs.data_selection_tab import DataTab
from dashboard_objects.control_panel_tabs.statistics_tab import StatisticsTab
from dashboard_objects.control_panel_tabs.future_tab import Window_3

# Parent and Sibling imports
if False:
    from dashboard_objects.window import OrderbookApp
    from dashboard_objects.graph_area import GraphArea

class ControlPanel(ttk.Notebook):
    """
    The main side panel housing all control tabs.
    """

    def __init__(self,
                 parent: "OrderbookApp",
                 graph_area: "GraphArea"):
        super().__init__(parent)
        self.configure(width=300)

        # Initialize tabs
        self.data_tab = DataTab(self, graph_area)
        self.stats_tab = StatisticsTab(self, graph_area)
        self.orderbook_tab = Window_3(self, graph_area)

        # Add tabs to notebook
        self.add(self.data_tab, text="Data")
        self.add(self.stats_tab, text="Statistics")
        self.add(self.orderbook_tab, text="Window 3")
