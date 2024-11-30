import pytest
from fastapi import status

def test_fetch_data_for_crew(client, auth_headers):
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

    # Then fetch data for the crew
    fetch_data = {
        "crew_id": crew_id,
        "start_time": 1609459200000,  # 2021-01-01
        "end_time": 1609545600000,    # 2021-01-02
        "intervals": ["1h", "4h"]
    }
    response = client.post("/data-sourcing/fetch", json=fetch_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "crew_id" in data
    assert "status" in data
    assert "data_points" in data
    assert isinstance(data["data_points"], dict)
    assert "1h" in data["data_points"]
    assert "4h" in data["data_points"]

def test_fetch_data_invalid_crew(client, auth_headers):
    fetch_data = {
        "crew_id": 999999,  # Non-existent crew
        "start_time": 1609459200000,
        "end_time": 1609545600000,
        "intervals": ["1h"]
    }
    response = client.post("/data-sourcing/fetch", json=fetch_data, headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Trading crew not found" in response.json()["detail"]

def test_fetch_data_invalid_interval(client, auth_headers):
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

    # Then try to fetch data with invalid interval
    fetch_data = {
        "crew_id": crew_id,
        "start_time": 1609459200000,
        "end_time": 1609545600000,
        "intervals": ["invalid"]
    }
    response = client.post("/data-sourcing/fetch", json=fetch_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid interval" in response.json()["detail"]

def test_fetch_data_invalid_time_range(client, auth_headers):
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

    # Then try to fetch data with end_time before start_time
    fetch_data = {
        "crew_id": crew_id,
        "start_time": 1609545600000,  # 2021-01-02
        "end_time": 1609459200000,    # 2021-01-01
        "intervals": ["1h"]
    }
    response = client.post("/data-sourcing/fetch", json=fetch_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid time range" in response.json()["detail"]
