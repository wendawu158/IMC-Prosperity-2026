import pandas as pd
import matplotlib.pyplot as plt

# Matplotlib initialisation

fig, axs = plt.subplots(2)

# Now we can see all the columns
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Relative path of file
df = pd.read_csv("Tutorial Data/prices_round_0_day_-1.csv", sep=";")
df["bids"] = df["bid_volume_1"].fillna(0) + df["bid_volume_2"].fillna(0) + df["bid_volume_3"].fillna(0)
df["asks"] = df["ask_volume_1"].fillna(0) + df["ask_volume_2"].fillna(0) + df["ask_volume_3"].fillna(0)

TOMATOES = df[df["product"] == "TOMATOES"].set_index("timestamp")
EMERALDS = df[df["product"] == "EMERALDS"].set_index("timestamp")

axs[0].plot(TOMATOES.index, TOMATOES["bid_price_1"], "o", color = "#ff0000")
axs[0].plot(TOMATOES.index, TOMATOES["bid_price_2"], "o", color = "#ff2020")
axs[0].plot(TOMATOES.index, TOMATOES["bid_price_3"], "o", color = "#ff5050")

axs[0].plot(TOMATOES.index, TOMATOES["ask_price_1"], "o", color = "#00ff00")
axs[0].plot(TOMATOES.index, TOMATOES["ask_price_2"], "o", color = "#20ff20")
axs[0].plot(TOMATOES.index, TOMATOES["ask_price_3"], "o", color = "#50ff50")

axs[1].plot(EMERALDS.index, EMERALDS["bid_price_1"], "o", color = "#ff0000")
axs[1].plot(EMERALDS.index, EMERALDS["bid_price_2"], "o", color = "#ff2020")
axs[1].plot(EMERALDS.index, EMERALDS["bid_price_3"], "o", color = "#ff5050")

axs[1].plot(EMERALDS.index, EMERALDS["ask_price_1"], "o", color = "#00ff00")
axs[1].plot(EMERALDS.index, EMERALDS["ask_price_2"], "o", color = "#20ff20")
axs[1].plot(EMERALDS.index, EMERALDS["ask_price_3"], "o", color = "#50ff50")

plt.show()
