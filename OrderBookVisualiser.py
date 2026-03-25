import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.widgets import Cursor


class VerticalNavigationToolbar2Tk(NavigationToolbar2Tk):
    '''
    This is so that I can have a vertical toolbar with evil OOP magic
    hehehehehehehe
    Thanks @acw1668 from stackoverflow
    '''
    def __init__(self, canvas, window):
        super().__init__(canvas, window, pack_toolbar=False)

    # override _Button() to re-pack the toolbar button in vertical direction
    def _Button(self, text, image_file, toggle, command):
        b = super()._Button(text, image_file, toggle, command)
        b.pack(side=tk.TOP) # re-pack button in vertical direction
        return b

    # override _Spacer() to create vertical separator
    def _Spacer(self):
        s = tk.Frame(self, width=26, relief=tk.RIDGE, bg="DarkGray", padx=2)
        s.pack(side=tk.TOP, pady=5) # pack in vertical direction
        return s

    # disable showing mouse position in toolbar
    def set_message(self, s):
        pass


def cursor(event):
    '''
    Little function to determine what the cursor should be
    '''
    # However, we do want the cursor to show when we are in pan/zoom mode
    if toolbar.mode != '':
        return

    if event.inaxes:
        canvas.get_tk_widget().config(cursor="none")
    else:
        canvas.get_tk_widget().config(cursor="arrow")


# <editor-fold desc="Section to read the file and process it slightly">

# Filepath
filepath = "Tutorial Data/prices_round_0_day_-1.csv"
tradedItem = "TOMATOES"

# The main dataframe
df = pd.read_csv(filepath, sep=";", index_col=1)

# Some additional data in the frame. Tbh I don't think this will be very useful
df["bids"] = df["bid_volume_1"].fillna(0) + df["bid_volume_2"].fillna(0) + df["bid_volume_3"].fillna(0)
df["asks"] = df["ask_volume_1"].fillna(0) + df["ask_volume_2"].fillna(0) + df["ask_volume_3"].fillna(0)

# Separates the tradable goods into seperate pandas arrays
TRADE_DATA = df[df["product"] == tradedItem]

# Matplotlib initialisation

fig, ax = plt.subplots()
fig.subplots_adjust(left=0.05, bottom=0.07, right=0.95, top=0.95, wspace=0, hspace=0)

# Now we can see all the columns
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

ax.plot(TRADE_DATA.index, TRADE_DATA["ask_price_1"], "v", color="#00ff00")
ax.plot(TRADE_DATA.index, TRADE_DATA["ask_price_2"], "v", color="#20ff20")
ax.plot(TRADE_DATA.index, TRADE_DATA["ask_price_3"], "v", color="#50ff50")

ax.plot(TRADE_DATA.index, TRADE_DATA["mid_price"], ".", color="#000000")

ax.plot(TRADE_DATA.index, TRADE_DATA["bid_price_1"], "^", color="#ff0000")
ax.plot(TRADE_DATA.index, TRADE_DATA["bid_price_2"], "^", color="#ff2020")
ax.plot(TRADE_DATA.index, TRADE_DATA["bid_price_3"], "^", color="#ff5050")

# </editor-fold>

# <editor-fold desc="Initialise Tkinter">

# The root of the tkinter gui
root = tk.Tk()

# Initialising some traits of the window
root.wm_title("Order Book Visualiser")

# Making sure that the damn window actually closes
root.bind("<Destroy>", plt.close())

# </editor-fold>

# <editor-fold desc="Initialise graph container">

# The canvas for the Graph
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().focus_set()
canvas.draw()

# Implementing the cursor function
canvas.mpl_connect('motion_notify_event', cursor)

# Crosshair (again, code is thanks to acw1668. This guy is like my saviour lmao)
ax.cursor = Cursor(ax, useblit=True, horizOn=True, vertOn=True, color="#101010", linewidth=0.5)

# The built-in matplotlib toolbar
toolbar = VerticalNavigationToolbar2Tk(canvas, root)
toolbar.update()

# Packing in this order so that the toolbar is left of the canvas
toolbar.pack(side=tk.LEFT, fill=tk.BOTH)
canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
canvas.get_tk_widget().focus_set()

# Mainly for debug to detect keyboard shortcuts
canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed {event.key}"))
canvas.mpl_connect("key_press_event", key_press_handler)

# </editor-fold>

# <editor-fold desc="Initialise Notebook container">

# Notebook object to display key statistics/house functionality buttons etc
AdvancedControls = ttk.Notebook(root)
AdvancedControls.configure(width=300)

# Add here to add more tabs
frame1 = ttk.Frame(AdvancedControls, relief=tk.RAISED)
frame2 = ttk.Frame(AdvancedControls, relief=tk.RAISED)
frame3 = ttk.Frame(AdvancedControls, relief=tk.RAISED)

# Add here to add content into the tabs
# Window 1
label1 = ttk.Label(frame1, text="Statistics")
label1.pack(padx=5, pady=5)
tk.Button

# Window 2
label2 = ttk.Label(frame2, text="Window 2")
label2.pack(padx=5, pady=5)

# Window 3
label3 = ttk.Label(frame3, text="Window 3")
label3.pack(padx=5, pady=5)

# Packing the windows
frame1.pack(padx=5, pady=5)
frame2.pack(padx=5, pady=5)
frame3.pack(padx=5, pady=5)

# Adding titles to the windows
AdvancedControls.add(frame1, text="Window 1")
AdvancedControls.add(frame2, text="Window 2")
AdvancedControls.add(frame3, text="Window 3")

# Packing the damn thing
AdvancedControls.pack(side=tk.LEFT, fill=tk.BOTH)

# </editor-fold>

# <editor-fold desc="Initialise Buttons">
# </editor-fold>

# The Loop (TM)
root.mainloop()
