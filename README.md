# IMC Prosperity 2026

# Background

<img width="1000" alt="image" src="https://github.com/user-attachments/assets/222dc82c-3074-4e65-855e-97875cc5a4c1" />

Hello! My name is Wenda Wu, and I am a first year at Imperial College London studying Mathematics (How exciting!)

Here is my code for the Prosperity Challenge! Since it's my first year competing, and I'm competing alone, I don't expect to do well; it's the learning that counts!

I'll be uploading all of my code here for you to steal (if you want, I don't really care) or not, and I'll try to explain my processes a little, mainly for my benefit.

Think of this repo as a dummy's guide to IMC Prosperity 4 (because it's written by an actual dummy)

Also, thanks to [Utkarsh Jetly](https://www.linkedin.com/in/utkarsh-jetly/) [@theycallmejetly](https://www.instagram.com/theycallmejetly/) for helping me with some (most) of this

# Dashboard

So, like any good data analyst, you need to be able to visualise the data.

I decided to program my own. You can find it as the "Dashboard.py" file. It takes .csv files from the folder named Data and spits out a visualisation of what's going on. Pretty simple.

# Basics of Implementation

So I started with the documentation, trying to understand how I would have to code my algorithms first.

From what I understand, the code behind each implementation is pretty simple (at least initially)

Here is a breakdown of all the components of implementation

## Trader Object

Every algorithm needs to define a **Trader** Object, and a **run()** function within that Object.

- Imports
  - OrderDepth - Essentially holds two dictionaries, a buy_orders dictionary for bids, and a sell_orders dictionary for asks
  - UserID - Used to identify who made what trade (I suspect something similar to Olivia last year for squid ink)
  - TradingState - [link](#tradingstate-object)
  - Order - [link](#order-object)

- run()
  - The **Trader.run()** function takes a **TradingState** Object (really a glorified list) and returns:
    - result: A dictionary, keys being the ticker, and values being a list of **Order** Objects
    - conversions: How many units to convert for products/rounds where conversion mechanics exist
    - traderData: What you want to send to the next timestamp
  - The **Trader.run()** function is run every single timestamp (and can only run for 100ms, so nothing fancy)

For later rounds, apparently a **Trader.bid()** function is also necessary to define, but I'll get to that when more information comes out.

## TradingState Object

This is the input of your function, and it has these parameters

- traderData - string
  - This is your memory. This string is passed from the previous Trader.run()
- timestamp - time
  - What time is it? This gives us the time
- listings
  - Gives us a dictionary, keys being strings (of tickers) and values being [Listing Objects](#listing-objects)
- order-depths
  - 

## Order Object

This is one of the components of the output of your function, and it has these parameters

## Listing Objects

Each listing object has three parameters:
- A symbol string
- A product string
- A denomination string (the currency of the listing)
