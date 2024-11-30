"""
Binance data router for handling market data requests.

This module provides FastAPI endpoints for accessing various types of market data
from the Binance cryptocurrency exchange, including real-time prices, historical data,
order book information, and trading statistics.

The router uses the BinanceClient utility for making API calls and Pydantic models
for request/response validation. All endpoints require authentication.

Tags:
    binance: All Binance-related endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Path
from typing import List, Optional, Union
from datetime import datetime
from schemas.binance_data import (
    MarketData, Kline, HistoricalDataResponse, OrderBook, Trade, AggregatedTrade,
    Ticker24h, TickerPrice, BookTicker, ExchangeInfo
)
from utils.binance_client import BinanceClient
from utils.auth_utils import get_current_user

router = APIRouter(prefix="/binance", tags=["binance"])

@router.get(
    "/price/{symbol}",
    response_model=TickerPrice,
    summary="Get Real-time Price",
    description="Get the current price for a trading pair from Binance."
)
async def get_real_time_price(
    symbol: str = Path(..., description="Trading pair symbol (e.g., 'BTCUSDT')"),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get real-time price for a trading pair.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        current_user (dict): Current authenticated user

    Returns:
        TickerPrice: Real-time price information

    Raises:
        HTTPException: If the symbol is invalid or the request fails
    """
    try:
        client = BinanceClient()
        return client.get_real_time_price(symbol)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/historical/{symbol}",
    response_model=HistoricalDataResponse,
    summary="Get Historical Data",
    description="Get historical kline/candlestick data for a trading pair."
)
async def get_historical_data(
    symbol: str = Path(..., description="Trading pair symbol (e.g., 'BTCUSDT')"),
    interval: str = Query(
        ...,
        pattern=r'^[1-9][0-9]?[mhdwM]$',
        description="Kline interval (e.g., '1m', '5m', '1h')"
    ),
    start_time: Optional[int] = Query(
        None,
        description="Start time in milliseconds"
    ),
    end_time: Optional[int] = Query(
        None,
        description="End time in milliseconds"
    ),
    limit: int = Query(
        default=500,
        le=1000,
        description="Number of klines to retrieve (max 1000)"
    ),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get historical kline/candlestick data for a trading pair.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        interval (str): Kline interval (e.g., '1m', '5m', '1h')
        start_time (Optional[int]): Start time in milliseconds
        end_time (Optional[int]): End time in milliseconds
        limit (int): Number of klines to retrieve (max 1000)
        current_user (dict): Current authenticated user

    Returns:
        HistoricalDataResponse: Historical kline data

    Raises:
        HTTPException: If parameters are invalid or the request fails
    """
    try:
        client = BinanceClient()
        start_dt = datetime.fromtimestamp(start_time/1000) if start_time else None
        end_dt = datetime.fromtimestamp(end_time/1000) if end_time else None
        
        klines = client.get_klines(
            symbol=symbol,
            interval=interval,
            start_time=start_dt,
            end_time=end_dt,
            limit=limit
        )
        
        return {
            "symbol": symbol,
            "interval": interval,
            "data": klines
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/orderbook/{symbol}",
    response_model=OrderBook,
    summary="Get Order Book",
    description="Get current order book for a trading pair."
)
async def get_order_book(
    symbol: str = Path(..., description="Trading pair symbol (e.g., 'BTCUSDT')"),
    limit: int = Query(
        default=100,
        le=1000,
        description="Number of bids/asks to retrieve (max 1000)"
    ),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current order book for a trading pair.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        limit (int): Number of bids/asks to retrieve (max 1000)
        current_user (dict): Current authenticated user

    Returns:
        OrderBook: Order book data

    Raises:
        HTTPException: If the symbol is invalid or the request fails
    """
    try:
        client = BinanceClient()
        return client.get_orderbook(symbol, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/trades/{symbol}",
    response_model=List[Trade],
    summary="Get Recent Trades",
    description="Get recent trades for a trading pair."
)
async def get_recent_trades(
    symbol: str = Path(..., description="Trading pair symbol (e.g., 'BTCUSDT')"),
    limit: int = Query(
        default=500,
        le=1000,
        description="Number of trades to retrieve (max 1000)"
    ),
    current_user: dict = Depends(get_current_user)
) -> List[dict]:
    """
    Get recent trades for a trading pair.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        limit (int): Number of trades to retrieve (max 1000)
        current_user (dict): Current authenticated user

    Returns:
        List[Trade]: List of recent trades

    Raises:
        HTTPException: If the symbol is invalid or the request fails
    """
    try:
        client = BinanceClient()
        return client.get_recent_trades(symbol, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/agg-trades/{symbol}",
    response_model=List[AggregatedTrade],
    summary="Get Aggregated Trades",
    description="Get compressed/aggregate trades for a trading pair."
)
async def get_aggregated_trades(
    symbol: str = Path(..., description="Trading pair symbol (e.g., 'BTCUSDT')"),
    from_id: Optional[int] = Query(
        None,
        description="Trade ID to fetch from"
    ),
    start_time: Optional[int] = Query(
        None,
        description="Start time in milliseconds"
    ),
    end_time: Optional[int] = Query(
        None,
        description="End time in milliseconds"
    ),
    limit: int = Query(
        default=500,
        le=1000,
        description="Number of trades to retrieve (max 1000)"
    ),
    current_user: dict = Depends(get_current_user)
) -> List[dict]:
    """
    Get compressed/aggregate trades for a trading pair.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        from_id (Optional[int]): Trade ID to fetch from
        start_time (Optional[int]): Start time in milliseconds
        end_time (Optional[int]): End time in milliseconds
        limit (int): Number of trades to retrieve (max 1000)
        current_user (dict): Current authenticated user

    Returns:
        List[AggregatedTrade]: List of aggregated trades

    Raises:
        HTTPException: If parameters are invalid or the request fails
    """
    try:
        client = BinanceClient()
        # Convert millisecond timestamps to datetime objects
        start_dt = datetime.fromtimestamp(start_time / 1000) if start_time else None
        end_dt = datetime.fromtimestamp(end_time / 1000) if end_time else None
        
        trades = client.get_aggregated_trades(
            symbol=symbol,
            start_time=start_dt,
            end_time=end_dt,
            limit=limit
        )
        
        # Transform trades to match Pydantic model
        return [
            {
                "id": trade["id"],
                "price": float(trade["price"]),
                "quantity": float(trade["quantity"]),
                "first_trade_id": trade["first_trade_id"],
                "last_trade_id": trade["last_trade_id"],
                "time": trade["time"],
                "is_buyer_maker": trade["is_buyer_maker"],
                "is_best_match": trade["is_best_match"]
            }
            for trade in trades
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/ticker/24hr/{symbol}",
    response_model=Ticker24h,
    summary="Get 24hr Ticker",
    description="Get 24-hour rolling window price change statistics for a trading pair."
)
async def get_24hr_ticker(
    symbol: str = Path(..., description="Trading pair symbol (e.g., 'BTCUSDT')"),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get 24-hour rolling window price change statistics.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        current_user (dict): Current authenticated user

    Returns:
        Ticker24h: 24-hour ticker statistics

    Raises:
        HTTPException: If the symbol is invalid or the request fails
    """
    try:
        client = BinanceClient()
        data = client.get_ticker_24hr(symbol)
        # Transform data to match Pydantic model
        return {
            "symbol": data["symbol"],
            "price_change": float(data["price_change"]),
            "price_change_percent": float(data["price_change_percent"]),
            "weighted_avg_price": float(data["weighted_avg_price"]),
            "prev_close_price": float(data["prev_close_price"]),
            "last_price": float(data["last_price"]),
            "bid_price": float(data["bid_price"]),
            "ask_price": float(data["ask_price"]),
            "open_price": float(data["open_price"]),
            "high_price": float(data["high_price"]),
            "low_price": float(data["low_price"]),
            "volume": float(data["volume"]),
            "quote_volume": float(data["quote_volume"]),
            "open_time": data["open_time"],
            "close_time": data["close_time"],
            "first_trade_id": data["first_trade_id"],
            "last_trade_id": data["last_trade_id"],
            "trade_count": data["trade_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/ticker/price/{symbol}",
    response_model=TickerPrice,
    summary="Get Price Ticker",
    description="Get latest price for a trading pair."
)
async def get_price_ticker(
    symbol: str = Path(..., description="Trading pair symbol (e.g., 'BTCUSDT')"),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get latest price for a trading pair.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        current_user (dict): Current authenticated user

    Returns:
        TickerPrice: Latest price information

    Raises:
        HTTPException: If the symbol is invalid or the request fails
    """
    try:
        client = BinanceClient()
        data = client.get_ticker_price(symbol)
        # Transform data to match Pydantic model
        return {
            "symbol": data["symbol"],
            "price": float(data["price"])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/ticker/book/{symbol}",
    response_model=BookTicker,
    summary="Get Book Ticker",
    description="Get best price/quantity on the order book for a trading pair."
)
async def get_book_ticker(
    symbol: str = Path(..., description="Trading pair symbol (e.g., 'BTCUSDT')"),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get best price/quantity on the order book.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        current_user (dict): Current authenticated user

    Returns:
        BookTicker: Best price/quantity on the order book

    Raises:
        HTTPException: If the symbol is invalid or the request fails
    """
    try:
        client = BinanceClient()
        data = client.get_ticker_book(symbol)
        # Transform data to match Pydantic model
        return {
            "symbol": data["symbol"],
            "bid_price": float(data["bid_price"]),
            "bid_quantity": float(data["bid_quantity"]),
            "ask_price": float(data["ask_price"]),
            "ask_quantity": float(data["ask_quantity"])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/exchange-info",
    response_model=ExchangeInfo,
    summary="Get Exchange Information",
    description="Get current exchange trading rules and symbol information."
)
async def get_exchange_info(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current exchange trading rules and symbol information.

    Args:
        current_user (dict): Current authenticated user

    Returns:
        ExchangeInfo: Exchange information including trading rules and symbols

    Raises:
        HTTPException: If the request fails
    """
    try:
        client = BinanceClient()
        return client.get_exchange_info()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
