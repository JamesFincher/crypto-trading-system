from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MarketData(BaseModel):
    """
    Schema for real-time market data.
    """
    symbol: str = Field(..., description="Trading pair symbol (e.g., 'BTCUSDT')", pattern="^[A-Z0-9]+$")
    price: float = Field(..., description="Current price", gt=0)
    volume: float = Field(..., description="Trading volume in base currency", ge=0)
    timestamp: datetime = Field(..., description="Timestamp of the market data")
    bid: Optional[float] = Field(None, description="Best bid price", gt=0)
    ask: Optional[float] = Field(None, description="Best ask price", gt=0)
    trades_24h: Optional[int] = Field(None, description="Number of trades in last 24 hours", ge=0)

class Kline(BaseModel):
    """
    Schema for candlestick/kline data.
    """
    open_time: datetime = Field(..., description="Candle open time")
    open: float = Field(..., description="Opening price", gt=0)
    high: float = Field(..., description="Highest price", gt=0)
    low: float = Field(..., description="Lowest price", gt=0)
    close: float = Field(..., description="Closing price", gt=0)
    volume: float = Field(..., description="Trading volume in base currency", ge=0)
    close_time: datetime = Field(..., description="Candle close time")
    quote_volume: float = Field(..., description="Trading volume in quote currency", ge=0)
    trades: int = Field(..., description="Number of trades in the period", ge=0)

class HistoricalDataRequest(BaseModel):
    """
    Schema for historical data request.
    """
    symbol: str = Field(..., description="Trading pair symbol (e.g., 'BTCUSDT')")
    interval: str = Field(..., description="Kline interval (e.g., '1m', '1h', '1d')")
    start_time: datetime = Field(..., description="Start time for historical data")
    end_time: datetime = Field(..., description="End time for historical data")

class HistoricalDataResponse(BaseModel):
    """
    Schema for historical data response.
    """
    symbol: str = Field(..., description="Trading pair symbol", pattern="^[A-Z0-9]+$")
    interval: str = Field(..., description="Kline interval", pattern="^[0-9]+[mhdwM]$")
    data: List[Kline] = Field(..., description="List of kline data")
