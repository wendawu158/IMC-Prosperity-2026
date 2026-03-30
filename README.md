# IMC Prosperity 2026

# Background

<img width="1000" alt="image" src="https://github.com/user-attachments/assets/222dc82c-3074-4e65-855e-97875cc5a4c1" />

Hello! My name is Wenda Wu, and I am a first year at Imperial College London studying Mathematics (How exciting!). 
I'll be working with [Abiola Abidoye](https://www.linkedin.com/in/abiola-abidoye/), who is also a first year at Imperial College London.

Here is our code for the Prosperity Challenge! 
Since it's our first year competing, we don't expect to do well; it's the learning that counts!

I'll be uploading all of our code here for you to steal (if you want, I don't really care), 
and I'll try to explain my processes a little, mainly for our benefit.

Think of this repo as a dummy's guide to IMC Prosperity 4 (because it's written by an actual dummy)

<img width="1000" alt="image" src="https://github.com/user-attachments/assets/9906eb78-3d7e-462d-9306-5a6e4e118345" />

> A rare photo of the owner of this repository

Also, thanks to [Utkarsh Jetly](https://www.linkedin.com/in/utkarsh-jetly/) [@theycallmejetly](https://www.instagram.com/theycallmejetly/) for helping me with some (most) of this

Also thanks to previous teams posting their write-ups. You can find them here:

- [Frankfurt Hedgehogs](https://github.com/TimoDiehm/imc-prosperity-3?tab=readme-ov-file#tools), second in the world for Prosperity 3
- [Linear Utility](https://github.com/ericcccsliu/imc-prosperity-2), second in the world for Prosperity 2
- [CMU Physics](https://github.com/chrispyroberts/imc-prosperity-3), first in the USA for Prosperity 3

And you can find the wiki containing all of this information from the IMC team here:

- [IMC Prosperity 4 Wiki](https://imc-prosperity.notion.site/prosperity-4-wiki)

# Dashboard

Like any good data analyst, you need to be able to visualise the data that you have been given

I decided to program my own. 
You can find it as the "Dashboard.py" file. 
It takes .csv files from the folder named Data,
and spits out a visualisation of what's going on. Pretty simple.

## Features

# Objects

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
  - run() is run every single timestamp (and can only run for 900ms, so nothing fancy)
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

This is the input of your function, and it has these variables:

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
  - How much of each ticker you have. Tells you your current inventory. Gives us a dictionary
    - Keys being strings (of products)
    - Values being integers. Positive is long, Negative is short
  - This object will be used to make sure you aren't breaching [position limits](#position-limits)
  - Interestingly, this object seems to use product instead of symbol
  - This seems to imply that a product can have many symbols, potentially leading to arbitrage opportunities

- observations
  - Apparently this mechanic will not be used, so safe to ignore

## Listing Object

```python
class Listing:

    def __init__(self, symbol: Symbol, product: Product, denomination: Product):
        self.symbol = symbol
        self.product = product
        self.denomination = denomination
```

Each listing object has three variables:

- A symbol string
- A product string
- A denomination string (the currency of the listing)

This object is likely used for metadata about the exchange

(e.g, a product having multiple symbols in different currencies)

I suspect that this is indicative of multiple currencies being introduced

Last year, there was a manual trading round involving simple currency arbitrage,
and I suspect this year we will have the opportunity to trade with multiple currencies

An alternative possibility is that these will be used for ETFs for "baskets" of goods

## OrderDepth Object

```python
class OrderDepth:

    def __init__(self):
        self.buy_orders: Dict[int, int] = {}
        self.sell_orders: Dict[int, int] = {}
```

Each OrderDepth object has two dictionaries as variables:

- One is buy_orders, listing bids, one is sell_orders, listing asks.
- Keys being ints (of prices)
- Values being ints (of number of orders at that price)
- Important to notes that bids are positive and asks are negative

## Trade Object

```python
class Trade:

    def __init__(self, symbol: Symbol, price: int, quantity: int, buyer: UserId = None, seller: UserId = None,
                 timestamp: int = 0) -> None:
        self.symbol = symbol
        self.price: int = price
        self.quantity: int = quantity
        self.buyer = buyer
        self.seller = seller
        self.timestamp = timestamp

    def __str__(self) -> str:
        return "(" + self.symbol + ", " + self.buyer + " << " + self.seller + ", " + str(self.price) + ", " + str(
            self.quantity) + ", " + str(self.timestamp) + ")"

    def __repr__(self) -> str:
        return "(" + self.symbol + ", " + self.buyer + " << " + self.seller + ", " + str(self.price) + ", " + str(
            self.quantity) + ", " + str(self.timestamp) + ")"
```

This Object is used to tell us about previous trades that have happened.

In the TradingState Object, we will only see trades that happened in the previous time stamp.

Each Trade object has these variables:

- A symbol string: what has been traded?
- A price string: what was the price offered for the good?
- A quantity integer: how much of the good was traded?
- A buyer UserID string: who bought?
- A seller UserID string: who sold?
- A timestamp integer: when did this occur?

Note that buyer and seller will usually be empty, unless the buyer/seller is the Trader we program

In that case, buyer/seller will be "SUBMISSION"

## Order Object

```python
class Order:

    def __init__(self, symbol: Symbol, price: int, quantity: int) -> None:
        self.symbol = symbol
        self.price = price
        self.quantity = quantity

    def __str__(self) -> str:
        return "(" + self.symbol + ", " + str(self.price) + ", " + str(self.quantity) + ")"

    def __repr__(self) -> str:
        return "(" + self.symbol + ", " + str(self.price) + ", " + str(self.quantity) + ")"
```

This is one of the components of the output of the run() function

Each Order object has these variables:

- A symbol string: what symbol to trade with?
- A price integer: what price to offer?
- A quantity integer: how much? (Positive is buy, negative is sell)








# Mechanics

## Trade Execution

Trades are executed like this
1. The timestamp starts, and exchange data is sent to our run() function
2. We determine what orders we want to place, and send those to the exchange
3. The exchange fulfills our orders, and leaves our unfulfilled orders for the bots
4. The bots determine what orders they want to place, and send those to the exchange
5. The exchange fulfills their orders
6. The exchange cancels our unfulfilled orders
7. The next timestamp starts

## Time limits

The run method must be able to return a response in 900ms

If this is not achieved, no response will be sent, and no trades will be executed

## Position limits

Each product has a position limit

We can only hold so much of either a long (having the product) or a short (owing the product), 
which are defined by the position limit



