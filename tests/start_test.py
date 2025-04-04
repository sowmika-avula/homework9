import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

@pytest.fixture
def client():
    # Updated initialization for newer FastAPI/Starlette versions
    client = TestClient(app)
    return client

@pytest.fixture
def access_token(client):
    form_data = {
        "username": settings.ADMIN_USER,
        "password": settings.ADMIN_PASSWORD,
    }
    response = client.post("/token", data=form_data)
    # Add error handling
    if response.status_code != 200:
        pytest.fail(f"Failed to get token: {response.status_code} - {response.text}")
    return response.json()["access_token"]

# Rest of your tests remain unchanged
def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()

def test_login_for_access_token(client):
    form_data = {
        "username": settings.ADMIN_USER,
        "password": settings.ADMIN_PASSWORD,
    }
    response = client.post("/token", data=form_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_with_wrong_credentials(client):
    form_data = {
        "username": "wrong",
        "password": "wrong",
    }
    response = client.post("/token", data=form_data)
    assert response.status_code == 401

def test_create_qr_code_unauthorized(client):
    qr_request = {
        "url": "https://example.com",
        "fill_color": "black",
        "back_color": "white",
        "size": 10,
    }
    response = client.post("/qr-codes/", json=qr_request)
    assert response.status_code == 401

def test_create_qr_code(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    qr_request = {
        "url": "https://example.com",
        "fill_color": "black",
        "back_color": "white",
        "size": 10,
    }
    response = client.post("/qr-codes/", json=qr_request, headers=headers)
    assert response.status_code in [200, 201]
    assert "qr_code_url" in response.json()
    assert "links" in response.json()

def test_list_qr_codes(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/qr-codes/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_qr_code(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # First, create a QR code
    qr_request = {
        "url": "https://test-delete.com",
        "fill_color": "black",
        "back_color": "white",
        "size": 10,
    }
    create_response = client.post("/qr-codes/", json=qr_request, headers=headers)
    assert create_response.status_code in [200, 201]
    
    # Then delete it
    filename = "aHR0cHMlM0EvL3Rlc3QtZGVsZXRlLmNvbQ==.png"
    delete_response = client.delete(f"/qr-codes/{filename}", headers=headers)
    assert delete_response.status_code == 204

def test_invalid_qr_code_request(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    qr_request = {
        "url": "not-a-url",
        "fill_color": "invalid-color",
        "back_color": "white",
        "size": 0,
    }
    response = client.post("/qr-codes/", json=qr_request, headers=headers)
    assert response.status_code == 422  # Validation error
    