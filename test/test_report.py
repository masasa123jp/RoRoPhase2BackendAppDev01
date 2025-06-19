import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_report():
    user_id = "some_user_id"
    response = client.post(f"/reports/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert data["status"] == "completed"
    assert "download_url" in data
