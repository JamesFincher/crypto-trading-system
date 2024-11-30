import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_create_trading_crew(client, auth_headers):
    crew_data = {
        "name": "Test Crew",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT", "ETHUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 1000.0
    }
    response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == crew_data["name"]
    assert data["trading_pairs"] == crew_data["trading_pairs"]
    assert data["strategy_config"] == crew_data["strategy_config"]
    assert data["risk_percentage"] == crew_data["risk_percentage"]
    assert data["max_position_size"] == crew_data["max_position_size"]
    assert not data["is_active"]
    assert "id" in data
    assert "user_id" in data

def test_get_trading_crews(client, auth_headers):
    # First create a crew
    crew_data = {
        "name": "Test Crew",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    client.post("/trading/crews", json=crew_data, headers=auth_headers)

    # Then get all crews
    response = client.get("/trading/crews", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    crew = data[0]
    assert crew["name"] == crew_data["name"]
    assert crew["trading_pairs"] == crew_data["trading_pairs"]
    assert crew["strategy_config"] == crew_data["strategy_config"]
    assert crew["risk_percentage"] == crew_data["risk_percentage"]
    assert crew["max_position_size"] == crew_data["max_position_size"]
    assert not crew["is_active"]
    assert "id" in crew
    assert "user_id" in crew

def test_get_trading_crew(client, auth_headers):
    # First create a crew
    crew_data = {
        "name": "Test Crew",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    create_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = create_response.json()["id"]

    # Then get the crew
    response = client.get(f"/trading/crews/{crew_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == crew_id
    assert data["name"] == crew_data["name"]
    assert data["trading_pairs"] == crew_data["trading_pairs"]
    assert data["strategy_config"] == crew_data["strategy_config"]
    assert data["risk_percentage"] == crew_data["risk_percentage"]
    assert data["max_position_size"] == crew_data["max_position_size"]
    assert not data["is_active"]
    assert "user_id" in data

def test_activate_trading_crew(client, auth_headers):
    # First create a crew
    crew_data = {
        "name": "Test Crew",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    create_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = create_response.json()["id"]

    # Then activate it
    response = client.post(f"/trading/crews/{crew_id}/activate", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == crew_id
    assert data["is_active"]

def test_deactivate_trading_crew(client, auth_headers):
    # First create and activate a crew
    crew_data = {
        "name": "Test Crew",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    create_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = create_response.json()["id"]

    # Activate it
    client.post(f"/trading/crews/{crew_id}/activate", headers=auth_headers)

    # Then deactivate it
    response = client.post(f"/trading/crews/{crew_id}/deactivate", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == crew_id
    assert not data["is_active"]
