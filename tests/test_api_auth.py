import pytest

def test_login_success(client):
    response = client.post(
        "/auth/token",
        data={"username": "demo", "password": "nba2025"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    response = client.post(
        "/auth/token",
        data={"username": "demo", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/token",
        data={"username": "nonexistent", "password": "anything"}
    )
    assert response.status_code == 401

def test_get_me_with_valid_token(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "demo"
    assert data["role"] == "user"

def test_get_me_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_get_me_with_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token_here"})
    assert response.status_code == 401
