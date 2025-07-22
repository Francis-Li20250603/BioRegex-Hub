from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.main import app
from app.database import engine, get_session  # 修正导入，使用已存在的engine
from app.models import Rule, User
from .utils import create_test_user, create_test_token
import pytest

client = TestClient(app)

# 覆盖 FastAPI 的依赖项，使用测试数据库会话
@pytest.fixture(scope="function")
def override_get_session():
    def get_session_override():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = get_session_override
    yield
    app.dependency_overrides.clear()  # 清理覆盖

def test_list_rules(override_get_session):
    with Session(engine) as session:
        user = create_test_user(session, email="list@test.com")
        token = create_test_token(user.id)
        
        response = client.get(
            "/rules",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"响应错误: {response.text}"
        assert isinstance(response.json(), list)

def test_create_rule(override_get_session):
    with Session(engine) as session:
        user = create_test_user(session, email="create@test.com", is_admin=True)
        token = create_test_token(user.id)
        
        rule_data = {
            "pattern": "^[A-Za-z0-9]+$",
            "description": "Test rule for creation",
            "data_type": "string",
            "region": "FDA",
            "reference_url": "https://example.com"
        }
        
        response = client.post(
            "/rules",
            json=rule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201, f"响应错误: {response.text}"
        data = response.json()
        assert data["pattern"] == rule_data["pattern"]
        
        statement = select(Rule).where(Rule.id == data["id"])
        rule = session.exec(statement).first()
        assert rule is not None
        assert rule.description == rule_data["description"]
