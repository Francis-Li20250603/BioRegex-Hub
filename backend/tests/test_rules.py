from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.main import app
from app.database import engine, get_db
from app.models import Rule
from .utils import create_test_user, create_test_token
import pytest


client = TestClient(app)


@pytest.fixture(scope="function")
def test_session():
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture(scope="function")
def override_dependency(test_session):
    def get_test_db():
        yield test_session
    
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.clear()


def test_list_rules(override_dependency, test_session):
    user = create_test_user(test_session, email="list@test.com")
    token = create_test_token(user.id)
    
    response = client.get(
        "/rules",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200, f"请求失败: {response.text}"
    assert isinstance(response.json(), list)


def test_create_rule(override_dependency, test_session):
    admin_user = create_test_user(
        test_session, 
        email="create@test.com", 
        is_admin=True
    )
    token = create_test_token(admin_user.id)
    
    rule_data = {
        "pattern": r"^[A-Za-z0-9_]+$",
        "description": "Cloud test rule",
        "data_type": "string",
        "region": "FDA",
        "reference_url": "https://example.com/cloud"
    }
    
    response = client.post(
        "/rules",
        json=rule_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 预期状态码改为201，与API实际返回一致
    assert response.status_code == 201, f"创建失败: {response.text}"
    created_rule = response.json()
    assert created_rule["pattern"] == rule_data["pattern"]
    
    statement = select(Rule).where(Rule.id == created_rule["id"])
    db_rule = test_session.exec(statement).first()
    assert db_rule is not None
    assert db_rule.pattern == rule_data["pattern"]
