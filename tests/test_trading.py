import pytest
from fastapi import status

def test_create_trading_crew(client, auth_headers):
    crew_data = {
        "name": "Test Crew",
        "strategy": "MACD_RSI",
        "trading_pairs": ["BTCUSDT", "ETHUSDT"],
        "risk_level": "medium",
        "max_position_size": 1000.0
    }
    response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == crew_data["name"]
    assert data["strategy"] == crew_data["strategy"]
    assert data["trading_pairs"] == crew_data["trading_pairs"]
    assert "id" in data
    assert "created_at" in data

def test_get_trading_crews(client, auth_headers):
    # First create a crew
    crew_data = {
        "name": "Test Crew",
        "strategy": "MACD_RSI",
        "trading_pairs": ["BTCUSDT"],
        "risk_level": "low",
        "max_position_size": 500.0
    }
    client.post("/trading/crews", json=crew_data, headers=auth_headers)

    # Then get all crews
    response = client.get("/trading/crews", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == crew_data["name"]

def test_get_trading_crew(client, auth_headers):
    # First create a crew
    crew_data = {
        "name": "Test Crew",
        "strategy": "MACD_RSI",
        "trading_pairs": ["BTCUSDT"],
        "risk_level": "low",
        "max_position_size": 500.0
    }
    create_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = create_response.json()["id"]

    # Then get the specific crew
    response = client.get(f"/trading/crews/{crew_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == crew_id
    assert data["name"] == crew_data["name"]

def test_activate_trading_crew(client, auth_headers):
    # First create a crew
    crew_data = {
        "name": "Test Crew",
        "strategy": "MACD_RSI",
        "trading_pairs": ["BTCUSDT"],
        "risk_level": "low",
        "max_position_size": 500.0
    }
    create_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = create_response.json()["id"]

    # Then activate the crew
    response = client.put(f"/trading/crews/{crew_id}/activate", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == crew_id
    assert data["status"] == "active"

def test_deactivate_trading_crew(client, auth_headers):
    # First create and activate a crew
    crew_data = {
        "name": "Test Crew",
        "strategy": "MACD_RSI",
        "trading_pairs": ["BTCUSDT"],
        "risk_level": "low",
        "max_position_size": 500.0
    }
    create_response = client.post("/trading/crews", json=crew_data, headers=auth_headers)
    crew_id = create_response.json()["id"]
    client.put(f"/trading/crews/{crew_id}/activate", headers=auth_headers)

    # Then deactivate the crew
    response = client.put(f"/trading/crews/{crew_id}/deactivate", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == crew_id
    assert data["status"] == "inactive"
