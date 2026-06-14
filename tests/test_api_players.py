import pytest

def test_get_players_requires_auth(client):
    response = client.get("/players")
    assert response.status_code == 401

def test_get_players_with_auth(client, auth_headers):
    response = client.get("/players", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_players_with_search(client, auth_headers):
    response = client.get("/players?search=Booker", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all("booker" in p["full_name"].lower() for p in data)

def test_get_players_limit(client, auth_headers):
    response = client.get("/players?limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5

def test_get_players_limit_validation(client, auth_headers):
    response = client.get("/players?limit=500", headers=auth_headers)
    assert response.status_code == 422

def test_get_player_by_id(client, auth_headers):
    response = client.get("/players/1626164", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == 1626164
    assert data["full_name"] == "Devin Booker"

def test_get_player_not_found(client, auth_headers):
    response = client.get("/players/99999999", headers=auth_headers)
    assert response.status_code == 404

def test_get_player_stats(client, auth_headers):
    response = client.get("/players/1626164/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "points" in data[0]
    assert "rebounds" in data[0]
    assert "assists" in data[0]

def test_get_player_stats_with_limit(client, auth_headers):
    response = client.get("/players/1626164/stats?limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5

def test_get_player_stats_not_found(client, auth_headers):
    response = client.get("/players/99999999/stats", headers=auth_headers)
    assert response.status_code == 404
