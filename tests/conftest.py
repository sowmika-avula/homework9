# conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def get_access_token_for_test(client):
    form_data = {"username": "admin", "password": "secret"}
    response = client.post("/token", data=form_data)
    return response.json()["access_token"]