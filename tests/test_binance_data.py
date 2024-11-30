"""
Tests for the Binance data endpoints and client functionality.
"""

import pytest
import logging
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from typing import Dict, List
import time

# Configure logging
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger('binance.api').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)

from main import app
from utils.binance_client import BinanceClient
from schemas.binance_data import (
    MarketData, Kline, OrderBook, Trade, AggregatedTrade,
    Ticker24h, TickerPrice, BookTicker, ExchangeInfo
)

# Test constants
TEST_SYMBOL = "BTCUSDT"
TEST_INTERVAL = "1m"
TEST_LIMIT = 10

@pytest.fixture(autouse=True)
def setup_test_client(client, test_user, auth_headers):
    return client, auth_headers

def test_get_real_time_price(setup_test_client):
    client, headers = setup_test_client
    response = client.get(f"/binance/price/{TEST_SYMBOL}", headers=headers)
    assert response.status_code == 200

def test_get_historical_data(setup_test_client):
    client, headers = setup_test_client
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    response = client.get(
        f"/binance/historical/{TEST_SYMBOL}",
        params={
            "interval": TEST_INTERVAL,
            "start_time": int(start_time.timestamp() * 1000),
            "end_time": int(end_time.timestamp() * 1000),
            "limit": TEST_LIMIT
        },
        headers=headers
    )
    assert response.status_code == 200

def test_get_order_book(setup_test_client):
    client, headers = setup_test_client
    response = client.get(f"/binance/orderbook/{TEST_SYMBOL}", headers=headers)
    assert response.status_code == 200

def test_get_recent_trades(setup_test_client):
    client, headers = setup_test_client
    response = client.get(f"/binance/trades/{TEST_SYMBOL}", headers=headers)
    assert response.status_code == 200

def test_get_aggregated_trades(setup_test_client):
    client, headers = setup_test_client
    response = client.get(f"/binance/agg-trades/{TEST_SYMBOL}", headers=headers)
    assert response.status_code == 200

def test_get_24h_ticker(setup_test_client):
    client, headers = setup_test_client
    response = client.get(f"/binance/ticker/24hr/{TEST_SYMBOL}", headers=headers)
    assert response.status_code == 200

def test_get_price_ticker(setup_test_client):
    client, headers = setup_test_client
    response = client.get(f"/binance/ticker/price/{TEST_SYMBOL}", headers=headers)
    assert response.status_code == 200

def test_get_book_ticker(setup_test_client):
    client, headers = setup_test_client
    response = client.get(f"/binance/ticker/book/{TEST_SYMBOL}", headers=headers)
    assert response.status_code == 200

def test_get_exchange_info(setup_test_client):
    client, headers = setup_test_client
    response = client.get("/binance/exchange-info", headers=headers)
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
