from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.main import app
from app.database import engine, get_session
from app.models import Rule, User
from .utils import create_test_user, create_test_token
import pytest

# 初始化测试客户端
client = TestClient(app)

# 测试会话 fixture（确保每个测试独立）
@pytest.fixture(scope="function")
def test_session():
    """创建独立的测试会话，自动清理数据"""
    with Session(engine) as session:
        yield session
        # 回滚未提交的事务，确保测试隔离
        session.rollback()

# 覆盖 FastAPI 的会话依赖
@pytest.fixture(scope="function")
def override_dependency(test_session):
    """将应用的数据库会话替换为测试会话"""
    def get_test_session():
        yield test_session
    app.dependency_overrides[get_session] = get_test_session
    yield
    # 清除依赖覆盖，避免影响其他测试
    app.dependency_overrides.clear()

def test_list_rules(override_dependency, test_session):
    """测试获取规则列表"""
    # 创建测试用户
    user = create_test_user(test_session, email="list_rules@test.com")
    token = create_test_token(user.id)
    
    # 发送请求
    response = client.get(
        "/rules",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 验证响应
    assert response.status_code == 200, f"请求失败: {response.text}"
    assert isinstance(response.json(), list), "响应应为列表格式"

def test_create_rule(override_dependency, test_session):
    """测试创建新规则"""
    # 创建管理员用户（假设创建规则需要管理员权限）
    admin_user = create_test_user(
        test_session, 
        email="create_rule@test.com", 
        is_admin=True
    )
    token = create_test_token(admin_user.id)
    
    # 准备测试数据
    rule_payload = {
        "pattern": r"^[A-Za-z0-9_]+$",
        "description": "测试规则",
        "data_type": "string",
        "region": "FDA",
        "reference_url": "https://example.com/guideline"
    }
    
    # 发送创建请求
    response = client.post(
        "/rules",
        json=rule_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 验证响应
    assert response.status_code == 201, f"创建失败: {response.text}"
    created_rule = response.json()
    assert created_rule["pattern"] == rule_payload["pattern"], "规则模式不匹配"
    assert created_rule["description"] == rule_payload["description"], "描述不匹配"
    
    # 验证数据库中是否存在该规则
    statement = select(Rule).where(Rule.id == created_rule["id"])
    db_rule = test_session.exec(statement).first()
    assert db_rule is not None, "规则未保存到数据库"
    assert db_rule.region == rule_payload["region"], "区域信息不匹配"

def test_create_rule_unauthorized(override_dependency, test_session):
    """测试非管理员创建规则（应拒绝）"""
    # 创建普通用户
    regular_user = create_test_user(
        test_session, 
        email="unauth_create@test.com", 
        is_admin=False
    )
    token = create_test_token(regular_user.id)
    
    # 尝试创建规则
    response = client.post(
        "/rules",
        json={"pattern": "^test$", "description": "未授权测试", "data_type": "string", "region": "EMA"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 验证是否被拒绝（假设状态码为403）
    assert response.status_code in [403, 401], "非管理员应被拒绝创建规则"
