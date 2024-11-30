from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from schemas.binance_data import MarketData, HistoricalDataResponse, Kline
from utils.binance_client import BinanceClient
import re

router = APIRouter()

def get_binance_client():
    return BinanceClient()

@router.get("/market-data/real-time", response_model=MarketData)
async def get_real_time_market_data(
    symbol: str = Query(..., description="Trading pair symbol (e.g., 'BTCUSDT')", regex=r'^[A-Z0-9]{2,}[A-Z]{2,}$'),
    interval: Optional[str] = Query("1m", description="Time interval for the data"),
    client: BinanceClient = Depends(get_binance_client)
):
    """
    Fetch real-time market data for a given symbol.

    Parameters:
    - symbol: Trading pair symbol (e.g., 'BTCUSDT')
    - interval: Time interval for the data (default: '1m')

    Returns:
    - dict: Real-time market data including price and volume
    """
    try:
        # Get real-time price data from Binance
        price_data = client.get_real_time_price(symbol)
        
        # Get 24h ticker data for additional information
        ticker_data = client.client.ticker_24hr(symbol)
        
        return {
            "symbol": symbol,
            "interval": interval,
            "timestamp": datetime.now(),
            "price": float(price_data["price"]),
            "volume": float(ticker_data["volume"]),
            "bid": float(ticker_data["bidPrice"]),
            "ask": float(ticker_data["askPrice"]),
            "trades_24h": int(ticker_data["count"])
        }
    except Exception as e:
        if "Invalid symbol" in str(e):
            raise HTTPException(status_code=422, detail=f"Invalid symbol: {symbol}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-data/historical", response_model=HistoricalDataResponse)
async def get_historical_market_data(
    symbol: str = Query(..., description="Trading pair symbol (e.g., 'BTCUSDT')", regex=r'^[A-Z0-9]{2,}[A-Z]{2,}$'),
    start_time: int = Query(..., description="Start time for historical data (Unix timestamp in ms)"),
    end_time: int = Query(..., description="End time for historical data (Unix timestamp in ms)"),
    interval: str = Query("1h", description="Time interval for the data", regex=r'^[0-9]+[mhdwM]$'),
    client: BinanceClient = Depends(get_binance_client)
):
    """
    Fetch historical market data for a given symbol and time range.

    Parameters:
    - symbol: Trading pair symbol (e.g., 'BTCUSDT')
    - start_time: Start time for historical data (Unix timestamp in ms)
    - end_time: End time for historical data (Unix timestamp in ms)
    - interval: Time interval for the data (default: '1h')

    Returns:
    - dict: Historical market data including OHLCV data
    """
    try:
        # Convert timestamps to datetime for the client
        start_datetime = datetime.fromtimestamp(start_time / 1000)
        end_datetime = datetime.fromtimestamp(end_time / 1000)
        
        # Get historical klines data from Binance
        klines = client.get_klines(
            symbol=symbol,
            interval=interval,
            start_time=start_datetime,
            end_time=end_datetime
        )
        
        # Transform klines data to match our schema
        klines_data = []
        for k in klines:
            klines_data.append({
                "open_time": datetime.fromtimestamp(k[0] / 1000),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": datetime.fromtimestamp(k[6] / 1000),
                "quote_volume": float(k[7]),
                "trades": int(k[8])
            })
        
        return {
            "symbol": symbol,
            "interval": interval,
            "data": klines_data
        }
    except Exception as e:
        if "Invalid symbol" in str(e):
            raise HTTPException(status_code=422, detail=f"Invalid symbol: {symbol}")
        if "Invalid interval" in str(e):
            raise HTTPException(status_code=422, detail=f"Invalid interval: {interval}")
        raise HTTPException(status_code=500, detail=str(e))
