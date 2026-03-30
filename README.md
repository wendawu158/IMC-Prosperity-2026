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

```python
from datamodel import *

class Trader:

    def bid(self):
        pass
    
    def run(self, state: TradingState):
        orders = {}         # Keys are symbols, Values are Orders
        conversions = 0     # Allegedly unused
        traderData = ""     # Memory for next iteration
        
        """
        Your trading algorithm goes here
        """
        
        return orders, conversions, traderData
```

- bid()
  - A function that does not yet have any use
  - Further details will be released in round 2
  - The function will only be used in round 2

- run()
  - Inputs:
    - A [TradingState Object](#tradingstate-object)
  - Outputs:
    - orders: A dictionary
      - Keys being strings (of tickers)
      - Values being a list of **Order** Objects
    - conversions: 
      - How many units to convert for products/rounds where conversion mechanics exist
      - Apparently this year we aren't using this mechanic. Big Sadge
    - traderData: What you want to send to the next timestamp (this is passed to TradingState.tradeData)
      - This is used for memory as class and global variables are not kept between trades due to the implementation
      - Hard limit of 50000 characters (would be very surprised if anyone actually reached that)
  - run() is run every single timestamp (and can only run for 100ms, so nothing fancy)
  - Submission identifiers are generated for every submission, and a Run identifier is generated for every run
    - Useful for bug squashing

## TradingState Object

```python
Time = int
Symbol = str
Product = str
Position = int

class TradingState(object):
   def __init__(self,
                 traderData: str,
                 timestamp: Time,
                 listings: Dict[Symbol, Listing],
                 order_depths: Dict[Symbol, OrderDepth],
                 own_trades: Dict[Symbol, List[Trade]],
                 market_trades: Dict[Symbol, List[Trade]],
                 position: Dict[Product, Position],
                 observations: Observation):
        self.traderData = traderData
        self.timestamp = timestamp
        self.listings = listings
        self.order_depths = order_depths
        self.own_trades = own_trades
        self.market_trades = market_trades
        self.position = position
        self.observations = observations
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
```

This is the input of your function, and it has these parameters

- traderData - string
  - This is your memory. This string is passed from the previous Trader.run()
- timestamp - integer
  - What time is it? This gives us the current timestamp we are trading on
  - Importantly, there is no latency for trading
    - I.e. You trade on the current orderbook, not the next one
- listings
  - Gives us a dictionary
    - Keys being strings (of tickers)
    - Values being [Listing Objects](#listing-object)
- order-depths
  - The current order book for every ticker. Gives us a dictionary
    - Keys being strings (of tickers)
    - Values being an [OrderDepth Objects](#orderdepth-object)
- own_trades
  - Trades that you have executed. Gives us a dictionary
    - Keys being strings (of symbols)
    - Values being lists of [Trade Objects](#trade-object)
- market_trades
  - Trades that have been executed by the market. Gives us a dictionary
    - Keys being strings (of symbols)
    - Values being lists of [Trade Objects](#trade-object)
- position
  - How much of each ticker you have. Tells you your current inventory
    - Keys being integers (of prices)
    - Values being integers (of number of limit orders at that price)
      - It is important to note that:
      - Buy limit orders (bids) are positive
      - Sell limit orders (asks) are negative
      - I.E. if there are 5 bids @ 10 and 6 asks @ 11, then the position dictionary would be {10: 5, 11: -6}
    - This object will be used to make sure you aren't breaching [position limits](#position-limits)

## Listing Object

```python
class Listing:

    def __init__(self, symbol: Symbol, product: Product, denomination: Product):
        self.symbol = symbol
        self.product = product
        self.denomination = denomination
```

Each listing object has three parameters:
- A symbol string
- A product string
- A denomination string (the currency of the listing)

This object is likely used for metadata about the exchange

(e.g, a product having multiple symbols in different currencies)

I suspect that this is indicative of multiple currencies being introduced

Last year, there was a manual trading round involving simple currency arbitrage,
and I suspect this year we will have the opportunity to trade with multiple currencies

## OrderDepth Object

```python
class OrderDepth:

    def __init__(self):
        self.buy_orders: Dict[int, int] = {}
        self.sell_orders: Dict[int, int] = {}
```

Each OrderDepth object is two dictionaries:

- One is buy_orders, listing bids, one is sell_orders, listing asks.
- Keys being ints (of prices)
- Values being ints (of number of orders at that price)
- Important to notes that bids are positive and asks are negative

## Trade Object

This Object is used to tell us about previous trades that have happened.

In the TradingState Object, we will only see trades that happened in the 


## Order Object

This is one of the components of the output of your function, and it has these parameters




