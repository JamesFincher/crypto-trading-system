import pytest
from fastapi import status

def test_get_performance_logs(client, auth_headers):
    # First create a trading crew and execute some operations
    crew_data = {
        "name": "Test Crew",
        "strategy": "MACD_RSI",
        "trading_pairs": ["BTCUSDT"],
        "risk_level": "low",
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = crew_response.json()["id"]
    
    # Then get performance logs
    response = client.get(
        "/logs/performance",
        params={"crew_id": crew_id},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for log in data:
        assert "timestamp" in log
        assert "crew_id" in log
        assert "metrics" in log
        assert isinstance(log["metrics"], dict)

def test_get_performance_logs_with_timerange(client, auth_headers):
    # First create a trading crew
    crew_data = {
        "name": "Test Crew",
        "strategy": "MACD_RSI",
        "trading_pairs": ["BTCUSDT"],
        "risk_level": "low",
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = crew_response.json()["id"]
    
    # Then get performance logs with time range
    params = {
        "crew_id": crew_id,
        "start_time": 1609459200000,  # 2021-01-01
        "end_time": 1609545600000     # 2021-01-02
    }
    response = client.get("/logs/performance", params=params, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for log in data:
        assert log["timestamp"] >= params["start_time"]
        assert log["timestamp"] <= params["end_time"]

def test_get_performance_logs_invalid_crew(client, auth_headers):
    response = client.get(
        "/logs/performance",
        params={"crew_id": 999999},  # Non-existent crew
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Trading crew not found" in response.json()["detail"]

def test_get_performance_metrics(client, auth_headers):
    # First create a trading crew
    crew_data = {
        "name": "Test Crew",
        "strategy": "MACD_RSI",
        "trading_pairs": ["BTCUSDT"],
        "risk_level": "low",
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = crew_response.json()["id"]
    
    # Then get performance metrics
    response = client.get(
        f"/logs/performance/{crew_id}/metrics",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_trades" in data
    assert "win_rate" in data
    assert "profit_loss" in data
    assert "sharpe_ratio" in data
    assert "max_drawdown" in data
    assert "roi" in data

def test_get_performance_metrics_invalid_crew(client, auth_headers):
    response = client.get(
        "/logs/performance/999999/metrics",  # Non-existent crew
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Trading crew not found" in response.json()["detail"]
