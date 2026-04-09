# Functionality Imports
import tkinter as tk
import matplotlib.pyplot as plt

# Child Imports
from dashboard_objects.control_panel import ControlPanel
from dashboard_objects.graph_area import GraphArea

class OrderbookApp(tk.Tk):
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
        self.graph_area: GraphArea = GraphArea(self)
        self.control_panel: ControlPanel = ControlPanel(self, self.graph_area)

        # Pack Core Components
        self.graph_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.control_panel.pack(side=tk.LEFT, fill=tk.BOTH)

    def on_closing(self) -> None:
        """
        Shuts down matplotlib and the tkinter window
        """
        plt.close('all')
        self.destroy()