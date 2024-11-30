import pytest
from fastapi import status
from datetime import datetime
from unittest.mock import patch, MagicMock

def test_get_realtime_market_data(client, auth_headers):
    response = client.get(
        "/binance/market-data/real-time",
        params={"symbol": "BTCUSDT"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Validate response structure and data types
    assert data["symbol"] == "BTCUSDT"
    assert isinstance(data["price"], float) and data["price"] > 0
    assert isinstance(data["volume"], float) and data["volume"] >= 0
    assert isinstance(data["bid"], float) and data["bid"] > 0
    assert isinstance(data["ask"], float) and data["ask"] > 0
    assert isinstance(data["trades_24h"], int) and data["trades_24h"] >= 0
    assert "timestamp" in data
    
    # Validate price consistency
    assert data["bid"] <= data["price"] <= data["ask"], "Price should be between bid and ask"

def test_get_realtime_market_data_invalid_symbol(client, auth_headers):
    response = client.get(
        "/binance/market-data/real-time",
        params={"symbol": "INVALID"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_historical_market_data(client, auth_headers):
    # Use more recent timestamps to ensure data availability
    current_time = int(datetime.now().timestamp() * 1000)
    one_day_ago = current_time - (24 * 60 * 60 * 1000)  # 24 hours ago
    
    params = {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "start_time": one_day_ago,
        "end_time": current_time
    }
    response = client.get(
        "/binance/market-data/historical",
        params=params,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Validate response structure
    assert data["symbol"] == "BTCUSDT"
    assert data["interval"] == "1h"
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0, "Should have at least one data point for the last 24 hours"
    
    # Validate kline data
    for kline in data["data"]:
        assert isinstance(kline["open_time"], str)
        assert isinstance(kline["close_time"], str)
        assert isinstance(kline["open"], float) and kline["open"] > 0
        assert isinstance(kline["high"], float) and kline["high"] > 0
        assert isinstance(kline["low"], float) and kline["low"] > 0
        assert isinstance(kline["close"], float) and kline["close"] > 0
        assert isinstance(kline["volume"], float) and kline["volume"] >= 0
        assert isinstance(kline["quote_volume"], float) and kline["quote_volume"] >= 0
        assert isinstance(kline["trades"], int) and kline["trades"] >= 0
        
        # Validate price relationships
        assert kline["low"] <= kline["high"], "Low price should be <= high price"
        assert kline["low"] <= kline["open"] <= kline["high"], "Open price should be between low and high"
        assert kline["low"] <= kline["close"] <= kline["high"], "Close price should be between low and high"

def test_get_historical_market_data_invalid_interval(client, auth_headers):
    current_time = int(datetime.now().timestamp() * 1000)
    one_day_ago = current_time - (24 * 60 * 60 * 1000)
    
    params = {
        "symbol": "BTCUSDT",
        "interval": "invalid",
        "start_time": one_day_ago,
        "end_time": current_time
    }
    response = client.get(
        "/binance/market-data/historical",
        params=params,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
