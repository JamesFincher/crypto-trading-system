import pytest
from fastapi import status

def test_get_realtime_market_data(client, auth_headers):
    response = client.get(
        "/binance/market-data/real-time",
        params={"symbol": "BTCUSDT"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "symbol" in data
    assert "price" in data
    assert "timestamp" in data
    assert data["symbol"] == "BTCUSDT"

def test_get_realtime_market_data_invalid_symbol(client, auth_headers):
    response = client.get(
        "/binance/market-data/real-time",
        params={"symbol": "INVALID"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Symbol INVALID not found" in response.json()["detail"]

def test_get_historical_market_data(client, auth_headers):
    params = {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "start_time": 1609459200000,  # 2021-01-01
        "end_time": 1609545600000     # 2021-01-02
    }
    response = client.get(
        "/binance/market-data/historical",
        params=params,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "open_time" in data[0]
        assert "open" in data[0]
        assert "high" in data[0]
        assert "low" in data[0]
        assert "close" in data[0]
        assert "volume" in data[0]

def test_get_historical_market_data_invalid_interval(client, auth_headers):
    params = {
        "symbol": "BTCUSDT",
        "interval": "invalid",
        "start_time": 1609459200000,
        "end_time": 1609545600000
    }
    response = client.get(
        "/binance/market-data/historical",
        params=params,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid interval" in response.json()["detail"]
