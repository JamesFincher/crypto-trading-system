import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_create_paper_trading_session(client, auth_headers):
    session_data = {
        "name": "Test Paper Trading",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT", "ETHUSDT"],
        "risk_percentage": 2.0,
        "initial_balance": 10000.0,
        "max_position_size": 500.0
    }
    response = client.post("/paper-trading/sessions", json=session_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == session_data["name"]
    assert data["trading_pairs"] == session_data["trading_pairs"]
    assert data["strategy_config"] == session_data["strategy_config"]
    assert data["risk_percentage"] == session_data["risk_percentage"]
    assert data["initial_balance"] == session_data["initial_balance"]
    assert data["max_position_size"] == session_data["max_position_size"]
    assert "id" in data
    assert "user_id" in data

def test_get_paper_trading_sessions(client, auth_headers):
    # First create a session
    session_data = {
        "name": "Test Session",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "initial_balance": 10000.0,
        "max_position_size": 500.0
    }
    client.post("/paper-trading/sessions", json=session_data, headers=auth_headers)

    # Then get all sessions
    response = client.get("/paper-trading/sessions", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    session = data[0]
    assert session["name"] == session_data["name"]
    assert session["trading_pairs"] == session_data["trading_pairs"]
    assert session["strategy_config"] == session_data["strategy_config"]
    assert session["risk_percentage"] == session_data["risk_percentage"]
    assert session["initial_balance"] == session_data["initial_balance"]
    assert session["max_position_size"] == session_data["max_position_size"]
    assert "id" in session
    assert "user_id" in session

def test_get_paper_trading_session_performance(client, auth_headers):
    # First create a session
    session_data = {
        "name": "Test Session",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "initial_balance": 10000.0,
        "max_position_size": 500.0
    }
    create_response = client.post("/paper-trading/sessions", json=session_data, headers=auth_headers)
    session_id = create_response.json()["id"]

    # Get performance data
    response = client.get(f"/paper-trading/sessions/{session_id}/performance", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_trades" in data
    assert "win_rate" in data
    assert "average_profit" in data
    assert "total_profit" in data
    assert "current_balance" in data

def test_execute_paper_trade(client, auth_headers):
    # First create a session
    session_data = {
        "name": "Test Session",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "initial_balance": 10000.0,
        "max_position_size": 500.0
    }
    create_response = client.post("/paper-trading/sessions", json=session_data, headers=auth_headers)
    session_id = create_response.json()["id"]

    # Execute a trade
    trade_data = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": 0.1,
        "price": 50000.0
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
    assert "status" in data
