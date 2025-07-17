from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_rules():
    response = client.get("/rules")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_rule():
    test_rule = {
        "pattern": "^[A-Z]{3}\\d{5}$",
        "description": "Test rule",
        "data_type": "Test",
        "region": "Test"
    }
    response = client.post("/rules", json=test_rule)
    assert response.status_code == 200
    data = response.json()
    assert data["pattern"] == test_rule["pattern"]
    assert "id" in data
