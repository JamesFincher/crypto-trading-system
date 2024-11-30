"""
Tests for the Binance data endpoints and client functionality.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import os
import logging

# Configure logging
logging.getLogger().setLevel(logging.INFO)

from main import app
from utils.binance_client import BinanceClientWrapper

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    # Store original environment
    original_env = {
        "APP_ENV": os.getenv("APP_ENV"),
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "ALGORITHM": os.getenv("ALGORITHM"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    }
    
    # Set test environment
    os.environ["APP_ENV"] = "development"
    os.environ["SECRET_KEY"] = "your-secret-key"  # Match the key in dependencies.py
    os.environ["ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    
    yield
    
    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

@pytest.fixture
def auth_headers():
    """Generate valid authentication headers for testing"""
    # Create a test user and get JWT token
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    # Register a test user
    user_data = {
        "username": "test@example.com",
        "password": "testpassword123",
        "email": "test@example.com"
    }
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201, f"Registration failed: {register_response.json()}"
    
    # Login to get access token
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    login_response = client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_binance_connection(client, auth_headers):
    """Test Binance API connection and verify testnet"""
    response = client.get("/binance/test-connection", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["environment"] == "testnet"
    assert "server_time" in data

def test_binance_client_testnet(client, auth_headers):
    """Test BinanceClientWrapper testnet configuration"""
    response = client.get("/binance/test-connection", headers=auth_headers)
    assert response.status_code == 200

def test_binance_testnet_api(client, auth_headers):
    """Test Binance API calls with testnet"""
    # Test fetching klines data
    response = client.get(
        "/binance/klines",
        params={"symbol": "BTCUSDT", "interval": "1h", "limit": 10},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10  # Should return at most 10 klines

def test_unauthorized_access(client):
    """Test that endpoints require authentication"""
    response = client.get("/binance/test-connection")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.skip(reason="Mainnet credentials not available in test environment")
def test_binance_us_mainnet_config():
    """Test BinanceClient configuration for Binance.US mainnet"""
    # Set production environment
    os.environ["APP_ENV"] = "production"
    
    client = BinanceClientWrapper()
    
    # Verify Binance.US URLs
    assert client.client.API_URL == client.MAINNET_API_URL
    assert client.MAINNET_API_URL == "https://api.binance.us"
    assert client.MAINNET_STREAM_URL == "wss://stream.binance.us:9443"
    assert not client.testnet

@pytest.mark.skip(reason="Mainnet credentials not available in test environment")
def test_environment_switching():
    """Test automatic switching between testnet and Binance.US based on environment"""
    # Test production environment (Binance.US)
    os.environ["APP_ENV"] = "production"
    prod_client = BinanceClientWrapper()
    assert not prod_client.testnet
    assert prod_client.client.API_URL == prod_client.MAINNET_API_URL
    
    # Test development environment (testnet)
    os.environ["APP_ENV"] = "development"
    dev_client = BinanceClientWrapper()
    assert dev_client.testnet
    assert dev_client.client.API_URL == dev_client.TESTNET_API_URL

def test_get_real_time_price(client, auth_headers):
    """Test getting real-time price data"""
    response = client.get(
        "/binance/price",
        params={"symbol": "BTCUSDT"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data
    assert "price" in data
    assert data["symbol"] == "BTCUSDT"
    assert float(data["price"]) > 0

def test_get_exchange_info(client, auth_headers):
    """Test getting exchange information"""
    response = client.get("/binance/exchange-info", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "timezone" in data
    assert "serverTime" in data
    assert "symbols" in data
    assert len(data["symbols"]) > 0

def test_get_symbol_info(client, auth_headers):
    """Test getting symbol specific information"""
    response = client.get(
        "/binance/symbol-info",
        params={"symbol": "BTCUSDT"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data
    assert data["symbol"] == "BTCUSDT"
    assert "status" in data
    assert "baseAsset" in data
    assert "quoteAsset" in data

def test_create_market_order(client, auth_headers):
    """Test creating a market order"""
    order_data = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 0.001  # Small quantity for testing
    }
    response = client.post("/binance/order", json=order_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "orderId" in data
    assert "symbol" in data
    assert data["symbol"] == "BTCUSDT"
    assert data["type"] == "MARKET"
    assert data["side"] == "BUY"

def test_create_limit_order(client, auth_headers):
    """Test creating a limit order"""
    # Get current price first
    price_response = client.get(
        "/binance/price",
        params={"symbol": "BTCUSDT"},
        headers=auth_headers
    )
    current_price = float(price_response.json()["price"])

    # Create limit order 5% below current price
    limit_price = current_price * 0.95
    order_data = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": 0.001,  # Small quantity for testing
        "price": limit_price
    }
    response = client.post("/binance/order", json=order_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "orderId" in data
    assert "symbol" in data
    assert data["symbol"] == "BTCUSDT"
    assert data["type"] == "LIMIT"
    assert data["side"] == "BUY"
    # Allow for small rounding differences due to exchange precision requirements
    assert abs(float(data["price"]) - limit_price) < 0.01

def test_invalid_symbol(client, auth_headers):
    """Test error handling for invalid symbol"""
    response = client.get(
        "/binance/price",
        params={"symbol": "INVALIDPAIR"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Invalid symbol" in response.json()["detail"]

def test_invalid_order_params(client, auth_headers):
    """Test error handling for invalid order parameters"""
    # Test missing quantity for limit order
    order_data = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",  # Missing quantity and price
        "timeInForce": "GTC"
    }
    response = client.post("/binance/order", json=order_data, headers=auth_headers)
    assert response.status_code == 400
    assert "Quantity is required for non-market orders" in response.json()["detail"]
    
    # Test missing price for limit order
    order_data = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": 0.001  # Missing price
    }
    response = client.post("/binance/order", json=order_data, headers=auth_headers)
    assert response.status_code == 400
    assert "Price is required for LIMIT orders" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
