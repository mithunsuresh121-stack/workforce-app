import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post("/auth/login", json={"email": "admin@app.com", "password": "supersecure123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
