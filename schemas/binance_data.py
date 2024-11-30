"""
Pydantic models for Binance API data structures.

This module defines the data models used for validating and serializing
data from the Binance API responses. Each model corresponds to a specific
type of market data or trading information.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MarketData(BaseModel):
    """Real-time market data for a trading pair.

    This model represents current market data including price, volume,
    and other trading statistics.

    Attributes:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        interval (str): Time interval for the data (e.g., '1m', '5m', '1h')
        timestamp (datetime): Time when the data was retrieved
        price (float): Current market price
        volume (float): Trading volume in base currency
        bid (Optional[float]): Best bid price
        ask (Optional[float]): Best ask price
        trades_24h (Optional[int]): Number of trades in last 24 hours
    """
    symbol: str
    interval: str
    timestamp: datetime
    price: float = Field(gt=0, description="Current market price (must be > 0)")
    volume: float = Field(ge=0, description="Trading volume in base currency (must be >= 0)")
    bid: Optional[float] = Field(gt=0, description="Best bid price (must be > 0)")
    ask: Optional[float] = Field(gt=0, description="Best ask price (must be > 0)")
    trades_24h: Optional[int] = Field(ge=0, description="Number of trades in last 24 hours")

class Kline(BaseModel):
    """Candlestick/kline data for a trading pair.

    This model represents a single candlestick in a chart, containing
    OHLCV (Open, High, Low, Close, Volume) data.

    Attributes:
        open_time (datetime): Candle open time
        open (float): Opening price
        high (float): Highest price in the period
        low (float): Lowest price in the period
        close (float): Closing price
        volume (float): Trading volume in base currency
        close_time (datetime): Candle close time
        quote_volume (float): Trading volume in quote currency
        trades (int): Number of trades in the period
    """
    open_time: datetime
    open: float = Field(gt=0, description="Opening price (must be > 0)")
    high: float = Field(gt=0, description="Highest price in the period (must be > 0)")
    low: float = Field(gt=0, description="Lowest price in the period (must be > 0)")
    close: float = Field(gt=0, description="Closing price (must be > 0)")
    volume: float = Field(ge=0, description="Trading volume in base currency (must be >= 0)")
    close_time: datetime
    quote_volume: float = Field(ge=0, description="Trading volume in quote currency (must be >= 0)")
    trades: int = Field(ge=0, description="Number of trades in the period")

class HistoricalDataResponse(BaseModel):
    """Historical market data response containing a list of klines.

    This model wraps a list of kline data with metadata about the request.

    Attributes:
        symbol (str): Trading pair symbol
        interval (str): Time interval for the klines
        data (List[Kline]): List of kline data
    """
    symbol: str
    interval: str
    data: List[Kline]

class OrderBookEntry(BaseModel):
    """Single entry in the order book.

    Represents a single price level in the order book with its quantity.

    Attributes:
        price (float): Price level
        quantity (float): Quantity available at this price
    """
    price: float = Field(gt=0, description="Price level (must be > 0)")
    quantity: float = Field(gt=0, description="Quantity available at this price (must be > 0)")

class OrderBook(BaseModel):
    """Order book data for a trading pair.

    Complete order book snapshot with bids and asks at each price level.

    Attributes:
        symbol (str): Trading pair symbol
        timestamp (datetime): Time when the order book was retrieved
        bids (List[OrderBookEntry]): List of buy orders
        asks (List[OrderBookEntry]): List of sell orders
        last_update_id (int): Last update ID from Binance
    """
    symbol: str
    timestamp: datetime
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]
    last_update_id: int

class Trade(BaseModel):
    """Individual trade data.

    Represents a single executed trade on the exchange.

    Attributes:
        id (int): Trade ID
        price (float): Trade execution price
        quantity (float): Trade quantity
        time (datetime): Time of trade execution
        is_buyer_maker (bool): True if the buyer was the maker
        is_best_match (bool): True if this was the best price match
    """
    id: int
    price: float = Field(gt=0, description="Trade price (must be > 0)")
    quantity: float = Field(gt=0, description="Trade quantity (must be > 0)")
    time: datetime
    is_buyer_maker: bool
    is_best_match: bool

class AggregatedTrade(BaseModel):
    """Aggregated trade data combining multiple individual trades.

    Represents multiple trades aggregated at the same price level.

    Attributes:
        id (int): Aggregate trade ID
        price (float): Trade price
        quantity (float): Total quantity
        first_trade_id (int): First trade ID in the aggregate
        last_trade_id (int): Last trade ID in the aggregate
        time (datetime): Time of the trades
        is_buyer_maker (bool): True if the buyer was the maker
        is_best_match (bool): True if this was the best price match
    """
    id: int
    price: float = Field(gt=0, description="Trade price (must be > 0)")
    quantity: float = Field(gt=0, description="Total quantity (must be > 0)")
    first_trade_id: int
    last_trade_id: int
    time: datetime
    is_buyer_maker: bool
    is_best_match: bool

class Ticker24h(BaseModel):
    """24-hour rolling window price change statistics.

    Comprehensive price and volume statistics over the last 24 hours.

    Attributes:
        symbol (str): Trading pair symbol
        price_change (float): Absolute price change
        price_change_percent (float): Relative price change in percent
        weighted_avg_price (float): Weighted average price
        prev_close_price (float): Previous day's close price
        last_price (float): Latest price
        bid_price (float): Best bid price
        ask_price (float): Best ask price
        open_price (float): Open price
        high_price (float): Highest price
        low_price (float): Lowest price
        volume (float): Total volume
        quote_volume (float): Total quote asset volume
        open_time (datetime): Start time of the 24hr window
        close_time (datetime): End time of the 24hr window
        first_trade_id (int): First trade ID in the window
        last_trade_id (int): Last trade ID in the window
        trade_count (int): Total number of trades
    """
    symbol: str
    price_change: float
    price_change_percent: float
    weighted_avg_price: float = Field(gt=0, description="Weighted average price (must be > 0)")
    prev_close_price: float = Field(gt=0, description="Previous day's close price (must be > 0)")
    last_price: float = Field(gt=0, description="Latest price (must be > 0)")
    bid_price: float = Field(gt=0, description="Best bid price (must be > 0)")
    ask_price: float = Field(gt=0, description="Best ask price (must be > 0)")
    open_price: float = Field(gt=0, description="Open price (must be > 0)")
    high_price: float = Field(gt=0, description="Highest price (must be > 0)")
    low_price: float = Field(gt=0, description="Lowest price (must be > 0)")
    volume: float = Field(ge=0, description="Total volume (must be >= 0)")
    quote_volume: float = Field(ge=0, description="Total quote asset volume (must be >= 0)")
    open_time: datetime
    close_time: datetime
    first_trade_id: int
    last_trade_id: int
    trade_count: int = Field(ge=0, description="Total number of trades (must be >= 0)")

class TickerPrice(BaseModel):
    """Latest price for a symbol.

    Simple price ticker with just the symbol and current price.

    Attributes:
        symbol (str): Trading pair symbol
        price (float): Current price
    """
    symbol: str
    price: float = Field(gt=0, description="Current price (must be > 0)")

class BookTicker(BaseModel):
    """Best price/quantity on the order book for a symbol.

    Best bid and ask prices and quantities from the order book.

    Attributes:
        symbol (str): Trading pair symbol
        bid_price (float): Best bid price
        bid_quantity (float): Best bid quantity
        ask_price (float): Best ask price
        ask_quantity (float): Best ask quantity
    """
    symbol: str
    bid_price: float = Field(gt=0, description="Best bid price (must be > 0)")
    bid_quantity: float = Field(gt=0, description="Best bid quantity (must be > 0)")
    ask_price: float = Field(gt=0, description="Best ask price (must be > 0)")
    ask_quantity: float = Field(gt=0, description="Best ask quantity (must be > 0)")

class ExchangeInfo(BaseModel):
    """Exchange information including trading rules and symbol information.

    General exchange information and trading rules for all symbols.

    Attributes:
        timezone (str): Exchange timezone
        server_time (datetime): Current server time
        rate_limits (List[dict]): Rate limiting rules
        symbols (List[dict]): List of trading pair information
    """
    timezone: str
    server_time: datetime
    rate_limits: List[dict]
    symbols: List[dict]

class ExchangeFilter(BaseModel):
    """Trading rules for the exchange or a symbol.

    Defines various trading restrictions and limits.

    Attributes:
        filter_type (str): Type of filter (e.g., 'PRICE_FILTER', 'LOT_SIZE')
        min_price (Optional[float]): Minimum price allowed
        max_price (Optional[float]): Maximum price allowed
        tick_size (Optional[float]): Tick size for price
        min_qty (Optional[float]): Minimum quantity allowed
        max_qty (Optional[float]): Maximum quantity allowed
        step_size (Optional[float]): Step size for quantity
        min_notional (Optional[float]): Minimum notional value allowed
    """
    filter_type: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    tick_size: Optional[float] = None
    min_qty: Optional[float] = None
    max_qty: Optional[float] = None
    step_size: Optional[float] = None
    min_notional: Optional[float] = None

class OrderRequest(BaseModel):
    """Request model for creating orders.

    This model defines the required and optional parameters for creating
    different types of orders (MARKET, LIMIT, etc.).

    Attributes:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        side (str): Order side ('BUY' or 'SELL')
        type (str): Order type ('MARKET', 'LIMIT', etc.)
        quantity (float): Order quantity
        price (Optional[float]): Order price (required for LIMIT orders)
        time_in_force (Optional[str]): Time in force ('GTC', 'IOC', 'FOK')
        stop_price (Optional[float]): Stop price for stop orders
        iceberg_qty (Optional[float]): Iceberg quantity for iceberg orders
    """
    symbol: str = Field(..., description="Trading pair symbol (e.g., 'BTCUSDT')")
    side: str = Field(..., description="Order side", pattern="^(BUY|SELL)$")
    type: str = Field(..., description="Order type", pattern="^(MARKET|LIMIT|STOP_LOSS|STOP_LOSS_LIMIT|TAKE_PROFIT|TAKE_PROFIT_LIMIT|LIMIT_MAKER)$")
    quantity: float = Field(gt=0, description="Order quantity (must be > 0)")
    price: Optional[float] = Field(None, gt=0, description="Order price (required for LIMIT orders)")
    time_in_force: Optional[str] = Field(None, pattern="^(GTC|IOC|FOK)$", description="Time in force")
    stop_price: Optional[float] = Field(None, gt=0, description="Stop price for stop orders")
    iceberg_qty: Optional[float] = Field(None, gt=0, description="Iceberg quantity for iceberg orders")

class OrderResponse(BaseModel):
    """Response model for order creation.

    This model represents the response received after creating an order.

    Attributes:
        symbol (str): Trading pair symbol
        order_id (int): Order ID assigned by Binance
        client_order_id (str): Client-side order ID
        transact_time (datetime): Time the order was processed
        price (float): Order price
        orig_qty (float): Original quantity
        executed_qty (float): Executed quantity
        status (str): Order status
        type (str): Order type
        side (str): Order side
    """
    symbol: str
    order_id: int = Field(..., description="Order ID assigned by Binance")
    client_order_id: str = Field(..., description="Client-side order ID")
    transact_time: datetime = Field(..., description="Time the order was processed")
    price: float = Field(..., description="Order price")
    orig_qty: float = Field(..., description="Original quantity")
    executed_qty: float = Field(..., description="Executed quantity")
    status: str = Field(..., description="Order status")
    type: str = Field(..., description="Order type")
    side: str = Field(..., description="Order side")

class ConnectionStatus(BaseModel):
    """Response model for connection test endpoint.

    This model represents the response from the connection test endpoint.

    Attributes:
        status (str): Connection status ('connected' or 'error')
        environment (str): Current environment ('testnet' or 'mainnet')
        server_time (str): Server time from Binance
        timezone (str): Server timezone
    """
    status: str = Field(..., pattern="^(connected|error)$")
    environment: str = Field(..., pattern="^(testnet|mainnet)$")
    server_time: str
    timezone: str
