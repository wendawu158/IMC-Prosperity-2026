import tkinter as tk

if False:
    from dashboard_objects.control_panel import ControlPanel
    from dashboard_objects.graph_area import GraphArea


class AnalysisPlotTab(tk.Frame):
    """
    Awaiting future functionality
    """

    def __init__(self,
                 parent: "ControlPanel",
                 graph_area: "GraphArea"):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=2)