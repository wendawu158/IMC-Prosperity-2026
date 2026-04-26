import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


def hydrogel_analysis():
    """
    Analysis of hydrogel data
    """

    """
    Getting the data
    """
    day0 = pd.read_csv('Data/prices_round_3_day_0.csv', sep=";")
    day1 = pd.read_csv('Data/prices_round_3_day_1.csv', sep=";")
    day2 = pd.read_csv('Data/prices_round_3_day_2.csv', sep=";")

    print(day0.head())
    print(day1.head())
    print(day2.head())

    F_day0 = day0[day0["product"] == "HYDROGEL_PACK"]
    F_day1 = day1[day1["product"] == "HYDROGEL_PACK"]
    F_day2 = day2[day2["product"] == "HYDROGEL_PACK"]

    hydrogel_packs = pd.concat([F_day0, F_day1, F_day2])
    hydrogel_packs["timestamp"] = hydrogel_packs["timestamp"] // 100
    hydrogel_packs["timestamp"] = hydrogel_packs["timestamp"] + hydrogel_packs["day"] * 10000

    hydrogel_packs.drop("day", axis=1, inplace=True)
    hydrogel_packs.set_index("timestamp", inplace=True)

    print(hydrogel_packs)

    """
    There seems to be two market makers that consistently place bids that are probably our best estimate for price.
    There is one that places 10 - 15 bids/asks, then one that places 20 - 30 bids/asks at a slightly worse price.
    Therefore, we can use this to estimate price
    """

    bid_wall_condition = [
        (hydrogel_packs["bid_volume_1"] > 10),
        (hydrogel_packs["bid_volume_1"] == 10) & (hydrogel_packs["bid_volume_2"] >= 20),
        (hydrogel_packs["bid_volume_2"] >= 10) & (hydrogel_packs["bid_volume_2"] <= 15)
    ]

    bid_wall_choices = [
        hydrogel_packs["bid_price_1"],
        hydrogel_packs["bid_price_1"],
        hydrogel_packs["bid_price_2"]
    ]

    ask_wall_condition = [
        (hydrogel_packs["ask_volume_1"] > 10),
        (hydrogel_packs["ask_volume_1"] == 10) & (hydrogel_packs["ask_volume_2"] >= 20),
        (hydrogel_packs["ask_volume_2"] >= 10) & (hydrogel_packs["ask_volume_2"] <= 15)
    ]

    ask_wall_choices = [
        hydrogel_packs["ask_price_1"],
        hydrogel_packs["ask_price_1"],
        hydrogel_packs["ask_price_2"]
    ]

    hydrogel_packs["bid_wall"] = np.select(bid_wall_condition, bid_wall_choices)
    hydrogel_packs["ask_wall"] = np.select(ask_wall_condition, ask_wall_choices)

    hydrogel_packs["price"] = (hydrogel_packs["bid_wall"] + hydrogel_packs["ask_wall"]) / 2

    print(hydrogel_packs["price"])

    """
    Autocorrelation?
    Appears to be very slight negative autocorrelation with lag 1
    Indicates that price is likely to do opposite of what it just did
    """

    hydrogel_packs["past_delta_price"] = hydrogel_packs["price"].diff().dropna()
    hydrogel_packs["future_delta_price"] = (hydrogel_packs['price'].shift(-1) - hydrogel_packs['price']).dropna()
    hydrogel_packs["future_price"] = hydrogel_packs["price"].shift(-1)

    hydrogel_packs.drop(0, inplace=True)
    print(hydrogel_packs["past_delta_price"])
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # 3. Plot the ACF
    # We pass the specific column from the DataFrame
    plot_acf(hydrogel_packs['past_delta_price'], ax=axes[0], lags=300)
    axes[0].set_title('Autocorrelation Function (ACF)')

    # 4. Plot the PACF
    plot_pacf(hydrogel_packs['past_delta_price'], ax=axes[1], lags=300)
    axes[1].set_title('Partial Autocorrelation Function (PACF)')

    # Display the plots cleanly
    plt.tight_layout()
    plt.show()

    """
    Golden cross?
    Appears to be a worthless trading strategy
    May attempt implementation if have time
    """

    # 2. Calculate Fast and Slow SMAs
    hydrogel_packs['Fast_SMA'] = hydrogel_packs['price'].rolling(window=5).mean()
    hydrogel_packs['Slow_SMA'] = hydrogel_packs['price'].rolling(window=100).mean()

    # 3. Identify Crossovers
    # Create a signal column: 1 if Fast is above Slow, else 0
    hydrogel_packs['Signal'] = 0.0
    hydrogel_packs['Signal'] = np.where(hydrogel_packs['Fast_SMA'] > hydrogel_packs['Slow_SMA'], 1.0, 0.0)

    # Identify where the signal changes (1 to 0 or 0 to 1)
    # 1.0 = Golden Cross, -1.0 = Death Cross
    hydrogel_packs['Crossover'] = hydrogel_packs['Signal'].diff()

    # 4. Plotting
    plt.figure(figsize=(15, 8))
    plt.plot(hydrogel_packs['price'], label='Price', color='black', alpha=0.3)
    plt.plot(hydrogel_packs['Fast_SMA'], label='Fast SMA (10)', color='blue', linewidth=1.5)
    plt.plot(hydrogel_packs['Slow_SMA'], label='Slow SMA (30)', color='orange', linewidth=1.5)

    # 5. Add Vertical Lines for Crossovers
    for index, row in hydrogel_packs.iterrows():
        if row['Crossover'] == 1:  # Golden Cross
            plt.axvline(x=index, color='green', linestyle='--', alpha=0.6,
                        label='Golden Cross' if 'Golden Cross' not in plt.gca().get_legend_handles_labels()[1] else "")
        elif row['Crossover'] == -1:  # Death Cross
            plt.axvline(x=index, color='red', linestyle='--', alpha=0.6,
                        label='Death Cross' if 'Death Cross' not in plt.gca().get_legend_handles_labels()[1] else "")

    plt.title('Moving Average Crossovers')
    plt.legend(loc='upper left')
    plt.show()

    """
    True Price/Distance from 10000?
    """

    # 2. Create the scatter plot
    # We drop the first row (.iloc[1:]) because the first 'Price_Change' is NaN
    plt.figure(figsize=(10, 6))
    plt.scatter(hydrogel_packs['price'], hydrogel_packs['future_delta_price'], alpha=0.5)

    # 3. Add labels and formatting
    plt.title('Price Level vs. Change in Price')
    plt.xlabel('Price ($P_t$)')
    plt.ylabel('Change in Price ($\Delta P_t$)')
    plt.axhline(0, color='black', lw=1, alpha=0.7)  # Add a horizontal line at 0
    plt.grid(True, linestyle='--', alpha=0.6)

    plt.show()

    # 2. Define the integer boundaries for your "boxes"
    # We find the min and max, then create a range of every integer between them
    x_min, x_max = int(np.floor(hydrogel_packs['price'].min())), int(np.ceil(hydrogel_packs['price'].max()))
    y_min, y_max = int(np.floor(hydrogel_packs['future_delta_price'].min())), int(np.ceil(hydrogel_packs['future_delta_price'].max()))

    # Create arrays of edges: [min, min+1, min+2, ..., max]
    x_edges = np.arange(x_min, x_max + 1)
    y_edges = np.arange(y_min, y_max + 1)

    # 3. Plot using specific bins
    plt.figure(figsize=(12, 8))

    # By passing [x_edges, y_edges], we force the histogram to use our integer boxes
    plt.hist2d(hydrogel_packs['price'], hydrogel_packs['future_delta_price'], bins=[x_edges, y_edges], cmap='viridis')

    plt.colorbar(label='Frequency')
    plt.xlabel('Price (Integer)')
    plt.ylabel('Price Change (Integer)')
    plt.title('2D Histogram with 1x1 Integer Boxes')

    # Optional: Add a light grid to see the individual integer boxes
    plt.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.3)

    plt.show()

    """
    Ask-Bid balance?
    """
    hydrogel_packs["delta_volume"] = (
        hydrogel_packs["bid_volume_1"].fillna(0) + hydrogel_packs["bid_volume_2"].fillna(0) + hydrogel_packs["bid_volume_3"].fillna(0) -
        hydrogel_packs["ask_volume_1"].fillna(0) - hydrogel_packs["ask_volume_2"].fillna(0) - hydrogel_packs["ask_volume_3"].fillna(0)
    )

    differences = 0
    for i in hydrogel_packs["delta_volume"]:
        if i > 0 or i < 0:
            differences += 1

    print(differences)

    # 2. Define the integer boundaries for your "boxes"
    # We find the min and max, then create a range of every integer between them
    x_min, x_max = int(np.floor(hydrogel_packs['delta_volume'].min())), int(np.ceil(hydrogel_packs['delta_volume'].max()))
    y_min, y_max = int(np.floor(hydrogel_packs['future_price'].min())), int(np.ceil(hydrogel_packs['future_price'].max()))

    # Create arrays of edges: [min, min+1, min+2, ..., max]
    x_edges = np.arange(x_min, x_max + 1)
    y_edges = np.arange(y_min, y_max + 1)

    # 3. Plot using specific bins
    plt.figure(figsize=(12, 8))

    # By passing [x_edges, y_edges], we force the histogram to use our integer boxes
    plt.hist2d(hydrogel_packs['delta_volume'], hydrogel_packs['future_price'], bins=[x_edges, y_edges], cmap='viridis', norm=colors.LogNorm())

    plt.colorbar(label='Frequency')
    plt.xlabel('Price (Integer)')
    plt.ylabel('Price Change (Integer)')
    plt.title('2D Histogram with 1x1 Integer Boxes')

    # Optional: Add a light grid to see the individual integer boxes
    plt.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.3)

    plt.show()

    # 2. Define the integer boundaries for your "boxes"
    # We find the min and max, then create a range of every integer between them
    x_min, x_max = int(np.floor(hydrogel_packs['delta_volume'].min())), int(np.ceil(hydrogel_packs['delta_volume'].max()))
    y_min, y_max = int(np.floor(hydrogel_packs['future_delta_price'].min())), int(np.ceil(hydrogel_packs['future_delta_price'].max()))

    # Create arrays of edges: [min, min+1, min+2, ..., max]
    x_edges = np.arange(x_min, x_max + 1)
    y_edges = np.arange(y_min, y_max + 1)

    # 3. Plot using specific bins
    plt.figure(figsize=(12, 8))

    # By passing [x_edges, y_edges], we force the histogram to use our integer boxes
    plt.hist2d(hydrogel_packs['delta_volume'], hydrogel_packs['future_delta_price'], bins=[x_edges, y_edges], cmap='viridis', norm=colors.LogNorm())

    plt.colorbar(label='Frequency')
    plt.xlabel('Price (Integer)')
    plt.ylabel('Price Change (Integer)')
    plt.title('2D Histogram with 1x1 Integer Boxes')

    # Optional: Add a light grid to see the individual integer boxes
    plt.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.3)

    plt.show()


def velvet_analysis():
    """
    Analysis of velvet data
    """

    """
    Getting the data
    """
    day0 = pd.read_csv('Data/prices_round_3_day_0.csv', sep=";")
    day1 = pd.read_csv('Data/prices_round_3_day_1.csv', sep=";")
    day2 = pd.read_csv('Data/prices_round_3_day_2.csv', sep=";")

    print(day0.head())
    print(day1.head())
    print(day2.head())

    F_day0 = day0[day0["product"] == "VELVETFRUIT_EXTRACT"]
    F_day1 = day1[day1["product"] == "VELVETFRUIT_EXTRACT"]
    F_day2 = day2[day2["product"] == "VELVETFRUIT_EXTRACT"]

    hydrogel_packs = pd.concat([F_day0, F_day1, F_day2])
    hydrogel_packs["timestamp"] = hydrogel_packs["timestamp"] // 100
    hydrogel_packs["timestamp"] = hydrogel_packs["timestamp"] + hydrogel_packs["day"] * 10000

    hydrogel_packs.drop("day", axis=1, inplace=True)
    hydrogel_packs.set_index("timestamp", inplace=True)

    print(hydrogel_packs)

    """
    There seems to be multi[ple market makers that consistently place bids that are probably our best estimate for price.
    There is one that places 45+ bids/asks
    One that places between 15 - 25 bids/asks
    Therefore, we can use this to estimate price
    """

    bid_wall_condition = [
        (hydrogel_packs["bid_volume_1"] > 15),
        (hydrogel_packs["bid_volume_1"] == 15) & (hydrogel_packs["bid_volume_2"] >= 25),
        True
    ]

    bid_wall_choices = [
        hydrogel_packs["bid_price_1"],
        hydrogel_packs["bid_price_1"],
        hydrogel_packs["bid_price_2"]
    ]

    ask_wall_condition = [
        (hydrogel_packs["ask_volume_1"] > 15),
        (hydrogel_packs["ask_volume_1"] == 15) & (hydrogel_packs["ask_volume_2"] >= 25),
        True
    ]

    ask_wall_choices = [
        hydrogel_packs["ask_price_1"],
        hydrogel_packs["ask_price_1"],
        hydrogel_packs["ask_price_2"]
    ]

    hydrogel_packs["bid_wall"] = np.select(bid_wall_condition, bid_wall_choices)
    hydrogel_packs["ask_wall"] = np.select(ask_wall_condition, ask_wall_choices)

    hydrogel_packs["price"] = (hydrogel_packs["bid_wall"] + hydrogel_packs["ask_wall"]) / 2

    print(hydrogel_packs["price"])

    """
    Autocorrelation?
    Appears to be very slight negative autocorrelation with lag 1
    Indicates that price is likely to do opposite of what it just did
    """

    hydrogel_packs["past_delta_price"] = hydrogel_packs["price"].diff().dropna()
    hydrogel_packs["future_delta_price"] = (hydrogel_packs['price'].shift(-1) - hydrogel_packs['price']).dropna()
    hydrogel_packs["future_price"] = hydrogel_packs["price"].shift(-1)

    hydrogel_packs.drop(0, inplace=True)
    print(hydrogel_packs["past_delta_price"])
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # 3. Plot the ACF
    # We pass the specific column from the DataFrame
    plot_acf(hydrogel_packs['past_delta_price'], ax=axes[0], lags=300)
    axes[0].set_title('Autocorrelation Function (ACF)')

    # 4. Plot the PACF
    plot_pacf(hydrogel_packs['past_delta_price'], ax=axes[1], lags=300)
    axes[1].set_title('Partial Autocorrelation Function (PACF)')

    # Display the plots cleanly
    plt.tight_layout()
    plt.show()

    """
    Golden cross?
    Appears to be a worthless trading strategy
    May attempt implementation if have time
    """

    # 2. Calculate Fast and Slow SMAs
    hydrogel_packs['Fast_SMA'] = hydrogel_packs['price'].rolling(window=5).mean()
    hydrogel_packs['Slow_SMA'] = hydrogel_packs['price'].rolling(window=100).mean()

    # 3. Identify Crossovers
    # Create a signal column: 1 if Fast is above Slow, else 0
    hydrogel_packs['Signal'] = 0.0
    hydrogel_packs['Signal'] = np.where(hydrogel_packs['Fast_SMA'] > hydrogel_packs['Slow_SMA'], 1.0, 0.0)

    # Identify where the signal changes (1 to 0 or 0 to 1)
    # 1.0 = Golden Cross, -1.0 = Death Cross
    hydrogel_packs['Crossover'] = hydrogel_packs['Signal'].diff()

    # 4. Plotting
    plt.figure(figsize=(15, 8))
    plt.plot(hydrogel_packs['price'], label='Price', color='black', alpha=0.3)
    plt.plot(hydrogel_packs['Fast_SMA'], label='Fast SMA (10)', color='blue', linewidth=1.5)
    plt.plot(hydrogel_packs['Slow_SMA'], label='Slow SMA (30)', color='orange', linewidth=1.5)

    # 5. Add Vertical Lines for Crossovers
    for index, row in hydrogel_packs.iterrows():
        if row['Crossover'] == 1:  # Golden Cross
            plt.axvline(x=index, color='green', linestyle='--', alpha=0.6,
                        label='Golden Cross' if 'Golden Cross' not in plt.gca().get_legend_handles_labels()[1] else "")
        elif row['Crossover'] == -1:  # Death Cross
            plt.axvline(x=index, color='red', linestyle='--', alpha=0.6,
                        label='Death Cross' if 'Death Cross' not in plt.gca().get_legend_handles_labels()[1] else "")

    plt.title('Moving Average Crossovers')
    plt.legend(loc='upper left')
    plt.show()

    """
    True Price/Distance from 10000?
    """

    # 2. Create the scatter plot
    # We drop the first row (.iloc[1:]) because the first 'Price_Change' is NaN
    plt.figure(figsize=(10, 6))
    plt.scatter(hydrogel_packs['price'], hydrogel_packs['future_delta_price'], alpha=0.5)

    # 3. Add labels and formatting
    plt.title('Price Level vs. Change in Price')
    plt.xlabel('Price ($P_t$)')
    plt.ylabel('Change in Price ($\Delta P_t$)')
    plt.axhline(0, color='black', lw=1, alpha=0.7)  # Add a horizontal line at 0
    plt.grid(True, linestyle='--', alpha=0.6)

    plt.show()

    # 2. Define the integer boundaries for your "boxes"
    # We find the min and max, then create a range of every integer between them
    x_min, x_max = int(np.floor(hydrogel_packs['price'].min())), int(np.ceil(hydrogel_packs['price'].max()))
    y_min, y_max = int(np.floor(hydrogel_packs['future_delta_price'].min())), int(np.ceil(hydrogel_packs['future_delta_price'].max()))

    # Create arrays of edges: [min, min+1, min+2, ..., max]
    x_edges = np.arange(x_min, x_max + 1)
    y_edges = np.arange(y_min, y_max + 1)

    # 3. Plot using specific bins
    plt.figure(figsize=(12, 8))

    # By passing [x_edges, y_edges], we force the histogram to use our integer boxes
    plt.hist2d(hydrogel_packs['price'], hydrogel_packs['future_delta_price'], bins=[x_edges, y_edges], cmap='viridis')

    plt.colorbar(label='Frequency')
    plt.xlabel('Price (Integer)')
    plt.ylabel('Price Change (Integer)')
    plt.title('2D Histogram with 1x1 Integer Boxes')

    # Optional: Add a light grid to see the individual integer boxes
    plt.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.3)

    plt.show()

    """
    Ask-Bid balance?
    """
    hydrogel_packs["delta_volume"] = (
        hydrogel_packs["bid_volume_1"].fillna(0) + hydrogel_packs["bid_volume_2"].fillna(0) + hydrogel_packs["bid_volume_3"].fillna(0) -
        hydrogel_packs["ask_volume_1"].fillna(0) - hydrogel_packs["ask_volume_2"].fillna(0) - hydrogel_packs["ask_volume_3"].fillna(0)
    )

    differences = 0
    for i in hydrogel_packs["delta_volume"]:
        if i > 0 or i < 0:
            differences += 1

    print(differences)

    # 2. Define the integer boundaries for your "boxes"
    # We find the min and max, then create a range of every integer between them
    x_min, x_max = int(np.floor(hydrogel_packs['delta_volume'].min())), int(np.ceil(hydrogel_packs['delta_volume'].max()))
    y_min, y_max = int(np.floor(hydrogel_packs['future_price'].min())), int(np.ceil(hydrogel_packs['future_price'].max()))

    # Create arrays of edges: [min, min+1, min+2, ..., max]
    x_edges = np.arange(x_min, x_max + 1)
    y_edges = np.arange(y_min, y_max + 1)

    # 3. Plot using specific bins
    plt.figure(figsize=(12, 8))

    # By passing [x_edges, y_edges], we force the histogram to use our integer boxes
    plt.hist2d(hydrogel_packs['delta_volume'], hydrogel_packs['future_price'], bins=[x_edges, y_edges], cmap='viridis', norm=colors.LogNorm())

    plt.colorbar(label='Frequency')
    plt.xlabel('Price (Integer)')
    plt.ylabel('Price Change (Integer)')
    plt.title('2D Histogram with 1x1 Integer Boxes')

    # Optional: Add a light grid to see the individual integer boxes
    plt.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.3)

    plt.show()

    # 2. Define the integer boundaries for your "boxes"
    # We find the min and max, then create a range of every integer between them
    x_min, x_max = int(np.floor(hydrogel_packs['delta_volume'].min())), int(np.ceil(hydrogel_packs['delta_volume'].max()))
    y_min, y_max = int(np.floor(hydrogel_packs['future_delta_price'].min())), int(np.ceil(hydrogel_packs['future_delta_price'].max()))

    # Create arrays of edges: [min, min+1, min+2, ..., max]
    x_edges = np.arange(x_min, x_max + 1)
    y_edges = np.arange(y_min, y_max + 1)

    # 3. Plot using specific bins
    plt.figure(figsize=(12, 8))

    # By passing [x_edges, y_edges], we force the histogram to use our integer boxes
    plt.hist2d(hydrogel_packs['delta_volume'], hydrogel_packs['future_delta_price'], bins=[x_edges, y_edges], cmap='viridis', norm=colors.LogNorm())

    plt.colorbar(label='Frequency')
    plt.xlabel('Price (Integer)')
    plt.ylabel('Price Change (Integer)')
    plt.title('2D Histogram with 1x1 Integer Boxes')

    # Optional: Add a light grid to see the individual integer boxes
    plt.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.3)

    plt.show()

if __name__ == "__main__":
    velvet_analysis()