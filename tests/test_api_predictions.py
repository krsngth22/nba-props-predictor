import pytest

def test_predictions_requires_auth(client):
    response = client.get("/predictions/1626164")
    assert response.status_code == 401

def test_get_predictions_valid_player(client, auth_headers):
    response = client.get("/predictions/1626164", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == 1626164
    assert data["full_name"] == "Devin Booker"
    assert "points" in data
    assert "rebounds" in data
    assert "assists" in data

def test_predictions_have_required_fields(client, auth_headers):
    response = client.get("/predictions/1626164", headers=auth_headers)
    data = response.json()
    for target in ["points", "rebounds", "assists"]:
        assert data[target] is not None
        assert "predicted_value" in data[target]
        assert "model_mae" in data[target]
        assert data[target]["predicted_value"] >= 0

def test_predictions_player_not_found(client, auth_headers):
    response = client.get("/predictions/99999999", headers=auth_headers)
    assert response.status_code == 404

def test_predictions_cached_on_second_call(client, auth_headers):
    response1 = client.get("/predictions/1626164", headers=auth_headers)
    response2 = client.get("/predictions/1626164", headers=auth_headers)
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json() == response2.json()
