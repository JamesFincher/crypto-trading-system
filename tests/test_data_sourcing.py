import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_fetch_data_for_crew(client, auth_headers):
    # First create a trading crew
    crew_data = {
        "name": "Test Crew",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    assert crew_response.status_code == 201
    crew_id = crew_response.json()["id"]

    # Then fetch data for the crew
    current_time = int(datetime.utcnow().timestamp() * 1000)
    day_ago = int((datetime.utcnow() - timedelta(days=1)).timestamp() * 1000)
    
    fetch_data = {
        "crew_id": crew_id,
        "start_time": day_ago,
        "end_time": current_time,
        "intervals": ["1h", "4h"]
    }
    response = client.post("/data-sourcing/fetch", json=fetch_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "crew_id" in data
    assert "status" in data
    assert "data_points" in data
    assert isinstance(data["data_points"], dict)
    assert "BTCUSDT" in data["data_points"]
    assert "1h" in data["data_points"]["BTCUSDT"]
    assert "4h" in data["data_points"]["BTCUSDT"]

def test_fetch_data_invalid_crew(client, auth_headers):
    current_time = int(datetime.utcnow().timestamp() * 1000)
    day_ago = int((datetime.utcnow() - timedelta(days=1)).timestamp() * 1000)
    
    fetch_data = {
        "crew_id": 999999,  # Non-existent crew
        "start_time": day_ago,
        "end_time": current_time,
        "intervals": ["1h"]
    }
    response = client.post("/data-sourcing/fetch", json=fetch_data, headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Trading crew not found" in response.json()["detail"]

def test_fetch_data_invalid_interval(client, auth_headers):
    # First create a trading crew
    crew_data = {
        "name": "Test Crew 2",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    assert crew_response.status_code == 201
    crew_id = crew_response.json()["id"]

    # Then try to fetch data with invalid interval
    current_time = int(datetime.utcnow().timestamp() * 1000)
    day_ago = int((datetime.utcnow() - timedelta(days=1)).timestamp() * 1000)
    
    fetch_data = {
        "crew_id": crew_id,
        "start_time": day_ago,
        "end_time": current_time,
        "intervals": ["invalid_interval"]
    }
    response = client.post("/data-sourcing/fetch", json=fetch_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid interval" in response.json()["detail"]

def test_fetch_data_invalid_time_range(client, auth_headers):
    # First create a trading crew
    crew_data = {
        "name": "Test Crew 3",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    assert crew_response.status_code == 201
    crew_id = crew_response.json()["id"]

    # Then try to fetch data with invalid time range
    current_time = int(datetime.utcnow().timestamp() * 1000)
    future_time = current_time + 1000000  # Some time in the future
    
    fetch_data = {
        "crew_id": crew_id,
        "start_time": future_time,
        "end_time": current_time,  # End time before start time
        "intervals": ["1h"]
    }
    response = client.post("/data-sourcing/fetch", json=fetch_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid time range" in response.json()["detail"]

@pytest.mark.asyncio
async def test_data_persistence(client, auth_headers, test_db):
    # First create a trading crew
    crew_data = {
        "name": "Test Crew 4",
        "strategy_config": {"type": "MACD_RSI", "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        "trading_pairs": ["BTCUSDT"],
        "risk_percentage": 2.0,
        "max_position_size": 500.0
    }
    crew_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    assert crew_response.status_code == 201
    crew_id = crew_response.json()["id"]

    # Fetch some data
    current_time = int(datetime.utcnow().timestamp() * 1000)
    day_ago = int((datetime.utcnow() - timedelta(days=1)).timestamp() * 1000)
    
    fetch_data = {
        "crew_id": crew_id,
        "start_time": day_ago,
        "end_time": current_time,
        "intervals": ["1h"]
    }
    response = client.post("/data-sourcing/fetch", json=fetch_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    # Verify data was persisted in database
    from models.market_data import MarketData
    market_data = test_db.query(MarketData).filter(MarketData.crew_id == crew_id).all()
    assert len(market_data) > 0
    for data_point in market_data:
        assert data_point.symbol == "BTCUSDT"
        assert data_point.interval == "1h"
        assert data_point.timestamp >= datetime.fromtimestamp(day_ago / 1000)
        assert data_point.timestamp <= datetime.fromtimestamp(current_time / 1000)
        assert data_point.open_price is not None
        assert data_point.high_price is not None
        assert data_point.low_price is not None
        assert data_point.close_price is not None
        assert data_point.volume is not None
