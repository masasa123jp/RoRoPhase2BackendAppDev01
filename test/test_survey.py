import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_survey():
    survey_data = {
        "title": "Customer Satisfaction Survey",
        "questions": [
            {
                "text": "How satisfied are you with our service?",
                "choices": [
                    {"text": "Very satisfied"},
                    {"text": "Satisfied"},
                    {"text": "Neutral"},
                    {"text": "Dissatisfied"},
                    {"text": "Very dissatisfied"}
                ]
            }
        ]
    }
    response = client.post("/surveys/", json=survey_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == survey_data["title"]
    assert len(data["questions"]) == 1
