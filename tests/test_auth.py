import pytest
from fastapi import status

def test_login_success(client):
    # First register a user
    register_data = {
        "username": "testuser",
        "password": "testpassword123",
        "email": "test@example.com"
    }
    response = client.post("/auth/register", json=register_data)
    print("Register response:", response.json())  # Debug print
    assert response.status_code == status.HTTP_201_CREATED

    # Then try to login
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", json=login_data)  # Changed from data to json
    print("Login response:", response.json())  # Debug print
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_data)  # Changed from data to json
    print("Invalid credentials response:", response.json())  # Debug print
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"

def test_register_success(client):
    user_data = {
        "username": "newuser",
        "password": "newpassword123",
        "email": "new@example.com"
    }
    response = client.post("/auth/register", json=user_data)
    print("Register response:", response.json())  # Debug print
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data

def test_register_duplicate_username(client, test_user):
    user_data = {
        "username": "testuser",  # Same username as test_user
        "password": "anotherpassword123",
        "email": "another@example.com"
    }
    response = client.post("/auth/register", json=user_data)
    print("Duplicate username response:", response.json())  # Debug print
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already registered" in response.json()["detail"]
