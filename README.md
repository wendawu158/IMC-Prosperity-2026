# IMC Prosperity 2026

# Background

<img width="1000" alt="image" src="https://github.com/user-attachments/assets/222dc82c-3074-4e65-855e-97875cc5a4c1" />

Hello! My name is Wenda Wu, and I am a first year at Imperial College London studying Mathematics (How exciting!). I'll be working with [Abiola Abidoye](https://www.linkedin.com/in/abiola-abidoye/), who is also a first year at Imperial College London.

Here is our code for the Prosperity Challenge! Since it's our first year competing, we don't expect to do well; it's the learning that counts!

I'll be uploading all of our code here for you to steal (if you want, I don't really care), and I'll try to explain my processes a little, mainly for our benefit.

Think of this repo as a dummy's guide to IMC Prosperity 4 (because it's written by an actual dummy)

Also, thanks to [Utkarsh Jetly](https://www.linkedin.com/in/utkarsh-jetly/) [@theycallmejetly](https://www.instagram.com/theycallmejetly/) for helping me with some (most) of this

Also thanks to previous teams posting their write-ups. You can find them here:

- [Frankfurt Hedgehogs](https://github.com/TimoDiehm/imc-prosperity-3?tab=readme-ov-file#tools), second in the world for Prosperity 3
- [Linear Utility](https://github.com/ericcccsliu/imc-prosperity-2), second in the world for Prosperity 2
- [CMU Physics](https://github.com/chrispyroberts/imc-prosperity-3), first in the USA for Prosperity 3

# Dashboard

So, like any good data analyst, you need to be able to visualise the data.

I decided to program my own. You can find it as the "Dashboard.py" file. It takes .csv files from the folder named Data and spits out a visualisation of what's going on. Pretty simple.

## Features

# Basics of Implementation

So I started with the documentation, trying to understand how I would have to code my algorithms first.

From what I understand, the code behind each implementation is pretty simple (at least initially)

Here is a breakdown of all the components of implementation

## Trader Object

Every algorithm needs to define a **Trader** Object, and a **run()** function within that Object.

- Imports
  - OrderDepth - The [OrderDepth Object](#orderdepth-object)
  - UserID - Used to identify who made what trade (I suspect something similar to Olivia last year for squid ink)
  - TradingState - The main input, which is a [TradingState Object](#tradingstate-object)
  - Order - The [Order Object](#order-object)

- run()
  - The **Trader.run()** function takes for input a **TradingState** Object (really a glorified list) and returns:
    - result: A dictionary
      - Keys being strings (of tickers)
      - Values being a list of **Order** Objects
    - conversions: How many units to convert for products/rounds where conversion mechanics exist
      - Apparently this year we aren't using this mechanic. Big Sadge
    - traderData: What you want to send to the next timestamp (this is passed to TradingState.tradrData
  - The **Trader.run()** function is run every single timestamp (and can only run for 100ms, so nothing fancy)

For later rounds, apparently a **Trader.bid()** function is also necessary to define, but I'll get to that when more information comes out.

## TradingState Object

This is the input of your function, and it has these parameters

- traderData - string
  - This is your memory. This string is passed from the previous Trader.run()
- timestamp - integer
  - What time is it? This gives us the current timestamp we are trading on
  - Importantly, there is no latency for trading
    - I.e. You trade on the current orderbook 
- listings
  - Gives us a dictionary
    - Keys being strings (of tickers)
    - Values being [Listing Objects](#listing-objectss)
- order-depths
  - The current order book for every ticker. Gives us a dictionary
    - Keys being strings (of tickers)
    - Values being an [OrderDepth Objects](#orderdepth-objects)
- own_trades
  - Trades that you have executed. Gives us a dictionary
    - Keys being strings (of symbols)
    - Values being lists of [Trade Objects](#trade-objects)
- market_trades
  - Trades that have been executed by the market. Gives us a dictionary
    - Keys being strings (of symbols)
    - Values being lists of [Trade Objects](#trade-objects)
- position
  - How much of each ticker you have. Tells you your current inventory

## Order Object

This is one of the components of the output of your function, and it has these parameters

## Trade Object

## OrderDepth Object
Each OrderDepth object is two dictionaries:
- One is buy_orders, listing bids, one is sell_orders, listing asks.
- Keys being ints (of prices)
- Values being ints (of number of orders at that price)
- Important to notes that bids are positive and asks are negative

## Listing Objects

Each listing object has three parameters:
- A symbol string
- A product string
- A denomination string (the currency of the listing)
