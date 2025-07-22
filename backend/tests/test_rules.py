from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.main import app
from app.database import get_engine, get_session  # 导入会话工厂
from app.models import Rule, User
from .utils import create_test_user, create_test_token
import pytest

# 配置测试客户端，覆盖默认依赖
client = TestClient(app)

# 覆盖 FastAPI 的依赖项，使用测试数据库会话
@pytest.fixture(scope="function")
def override_get_session():
    engine = get_engine()
    def get_session_override():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = get_session_override
    yield
    app.dependency_overrides.clear()  # 清理覆盖，避免影响其他测试

def test_list_rules(override_get_session):
    """测试获取规则列表（使用测试会话）"""
    engine = get_engine()
    with Session(engine) as session:
        # 创建测试用户
        user = create_test_user(session, email="list@test.com")
        token = create_test_token(user.id)
        
        # 发送请求
        response = client.get(
            "/rules",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 验证响应
        assert response.status_code == 200, f"响应错误: {response.text}"
        assert isinstance(response.json(), list), "响应格式应为列表"

def test_create_rule(override_get_session):
    """测试创建规则（验证权限和数据完整性）"""
    engine = get_engine()
    with Session(engine) as session:
        # 创建测试用户（管理员权限）
        user = create_test_user(session, email="create@test.com", is_admin=True)
        token = create_test_token(user.id)
        
        # 准备测试数据
        rule_data = {
            "pattern": "^[A-Za-z0-9]+$",
            "description": "Test rule for creation",
            "data_type": "string",
            "region": "FDA",
            "reference_url": "https://example.com"
        }
        
        # 发送请求
        response = client.post(
            "/rules",
            json=rule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 验证响应
        assert response.status_code == 201, f"响应错误: {response.text}"
        data = response.json()
        assert data["pattern"] == rule_data["pattern"], "规则模式不匹配"
        
        # 验证数据库记录
        statement = select(Rule).where(Rule.id == data["id"])
        rule = session.exec(statement).first()
        assert rule is not None, "规则未保存到数据库"
        assert rule.description == rule_data["description"], "描述不匹配"
