from fastapi.testclient import TestClient
from app.main import app
from app.models import SQLModel, Rule, User
from app.database import get_db, create_db_and_tables
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from datetime import datetime
from .utils import create_test_user, create_test_token

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)

def test_list_rules():
    with TestingSessionLocal() as session:
        user = create_test_user(session)
        rule = Rule(
            pattern="^[A-Z]{3}\\d{5}$",
            description="Test rule",
            data_type="Test",
            region="Test",
            created_at=datetime.now()
        )
        session.add(rule)
        session.commit()
    token = create_test_token(user)
    response = client.get("/rules", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_create_rule():
    with TestingSessionLocal() as session:
        user = create_test_user(session)
    test_rule = {
        "pattern": "^[A-Z]{4}\\d{6}$",
        "description": "Unique Test Rule",
        "data_type": "Test",
        "region": "Test"
    }
    token = create_test_token(user)
    response = client.post("/rules", json=test_rule, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["pattern"] == test_rule["pattern"]
    assert "id" in data
