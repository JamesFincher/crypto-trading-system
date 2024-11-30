import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_get_performance_logs(client, auth_headers):
    # First create a trading crew and execute some operations
    crew_data = {
        "name": "Test Crew",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = crew_response.json()["id"]

    # Get performance logs
    response = client.get(
        "/logs/performance",
        params={"crew_id": crew_id},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_get_performance_logs_with_timerange(client, auth_headers):
    # First create a trading crew
    crew_data = {
        "name": "Test Crew",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = crew_response.json()["id"]

    # Get performance logs with time range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=1)

    response = client.get(
        "/logs/performance",
        params={
            "crew_id": crew_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_get_performance_logs_invalid_crew(client, auth_headers):
    response = client.get(
        "/logs/performance",
        params={"crew_id": 999999},  # Non-existent crew
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Trading crew not found" in response.json()["detail"]

def test_get_trading_metrics(client, auth_headers):
    # First create a trading crew
    crew_data = {
        "name": "Test Crew",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = crew_response.json()["id"]

    # Get trading metrics
    response = client.get(
        f"/logs/performance/{crew_id}/metrics",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "profit" in data
    assert "win_rate" in data
    assert "max_drawdown" in data
    assert "sharpe_ratio" in data

def test_get_trading_metrics_with_timerange(client, auth_headers):
    # First create a trading crew
    crew_data = {
        "name": "Test Crew",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = crew_response.json()["id"]

    # Get trading metrics with time range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=1)

    response = client.get(
        f"/logs/performance/{crew_id}/metrics",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "profit" in data
    assert "win_rate" in data
    assert "max_drawdown" in data
    assert "sharpe_ratio" in data

def test_get_trading_metrics_invalid_crew(client, auth_headers):
    response = client.get(
        "/logs/performance/999999/metrics",  # Non-existent crew
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Trading crew not found" in response.json()["detail"]
