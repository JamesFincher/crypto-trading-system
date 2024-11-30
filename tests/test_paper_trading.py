import pytest
from fastapi import status

def test_create_paper_trading_session(client, auth_headers):
    session_data = {
        "name": "Test Paper Trading",
        "initial_balance": 10000.0,
        "trading_pairs": ["BTCUSDT", "ETHUSDT"],
        "strategy": "MACD_RSI",
        "risk_level": "medium"
    }
    response = client.post("/paper-trading/sessions", json=session_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == session_data["name"]
    assert data["initial_balance"] == session_data["initial_balance"]
    assert data["current_balance"] == session_data["initial_balance"]
    assert "id" in data
    assert "created_at" in data

def test_get_paper_trading_sessions(client, auth_headers):
    # First create a session
    session_data = {
        "name": "Test Session",
        "initial_balance": 10000.0,
        "trading_pairs": ["BTCUSDT"],
        "strategy": "MACD_RSI",
        "risk_level": "low"
    }
    client.post("/paper-trading/sessions", json=session_data, headers=auth_headers)

    # Then get all sessions
    response = client.get("/paper-trading/sessions", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == session_data["name"]

def test_get_paper_trading_session_performance(client, auth_headers):
    # First create a session
    session_data = {
        "name": "Test Session",
        "initial_balance": 10000.0,
        "trading_pairs": ["BTCUSDT"],
        "strategy": "MACD_RSI",
        "risk_level": "low"
    }
    create_response = client.post("/paper-trading/sessions", json=session_data, headers=auth_headers)
    session_id = create_response.json()["id"]

    # Then get its performance
    response = client.get(f"/paper-trading/sessions/{session_id}/performance", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_trades" in data
    assert "win_rate" in data
    assert "profit_loss" in data
    assert "current_balance" in data
    assert "roi" in data

def test_execute_paper_trade(client, auth_headers):
    # First create a session
    session_data = {
        "name": "Test Session",
        "initial_balance": 10000.0,
        "trading_pairs": ["BTCUSDT"],
        "strategy": "MACD_RSI",
        "risk_level": "low"
    }
    create_response = client.post("/paper-trading/sessions", json=session_data, headers=auth_headers)
    session_id = create_response.json()["id"]

    # Then execute a trade
    trade_data = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": 0.1,
        "price": 30000.0
    }
    response = client.post(
        f"/paper-trading/sessions/{session_id}/trades",
        json=trade_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["symbol"] == trade_data["symbol"]
    assert data["side"] == trade_data["side"]
    assert data["quantity"] == trade_data["quantity"]
    assert data["price"] == trade_data["price"]
    assert "id" in data
    assert "timestamp" in data
    assert "total_value" in data
