from fastapi.testclient import TestClient  # 直接使用fastapi内置的TestClient
from sqlmodel import Session, select
from app.main import app
from app.database import engine, get_db  # 修改导入的依赖函数
from app.models import Rule
from .utils import create_test_user, create_test_token
import pytest


# 初始化测试客户端（无需额外安装fastapi-testclient）
client = TestClient(app)


@pytest.fixture(scope="function")
def test_session():
    """创建独立测试会话，确保测试隔离"""
    with Session(engine) as session:
        yield session
        session.rollback()  # 回滚事务，清理测试数据


@pytest.fixture(scope="function")
def override_dependency(test_session):
    """覆盖应用的数据库会话依赖"""
    def get_test_db():  # 修改依赖函数名称
        yield test_session
    
    app.dependency_overrides[get_db] = get_test_db  # 修改被覆盖的依赖
    yield
    app.dependency_overrides.clear()  # 清理覆盖


def test_list_rules(override_dependency, test_session):
    """测试获取规则列表"""
    # 创建测试用户并获取令牌
    user = create_test_user(test_session, email="list@test.com")
    token = create_test_token(user.id)
    
    # 发送请求
    response = client.get(
        "/rules",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 验证响应
    assert response.status_code == 200, f"请求失败: {response.text}"
    assert isinstance(response.json(), list)


def test_create_rule(override_dependency, test_session):
    """测试创建新规则"""
    # 创建管理员用户
    admin_user = create_test_user(
        test_session, 
        email="create@test.com", 
        is_admin=True
    )
    token = create_test_token(admin_user.id)
    
    # 准备测试数据
    rule_data = {
        "pattern": r"^[A-Za-z0-9_]+$",
        "description": "Cloud test rule",
        "data_type": "string",
        "region": "FDA",
        "reference_url": "https://example.com/cloud"
    }
    
    # 发送请求
    response = client.post(
        "/rules",
        json=rule_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 验证响应
    assert response.status_code == 201, f"创建失败: {response.text}"
    created_rule = response.json()
    assert created_rule["pattern"] == rule_data["pattern"]
    
    # 验证数据库
    statement = select(Rule).where(Rule.id == created_rule["id"])
    db_rule = test_session.exec(statement).first()
    assert db_rule is not None
    assert db_rule.pattern == rule_data["pattern"]
