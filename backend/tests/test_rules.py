from fastapi.testclient import TestClient
from app.main import app
from app.models import SQLModel, Rule, User  # 导入所有模型
from app.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from datetime import datetime
from .utils import create_test_user, create_test_token

# 使用 PostgreSQL 进行测试（更接近生产环境）
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 覆盖应用的数据库依赖
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# 设置测试客户端
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# 在每个测试前创建表，测试后删除表
@pytest.fixture(autouse=True)
def setup_and_teardown():
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)

# 创建测试用户辅助函数
def create_test_user(session):
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="testpassword",
        is_admin=True
    )
    session.add(user)
    session.commit()
    return user

# 获取测试 token 辅助函数
def get_test_token():
    # 模拟 JWT token
    return "fake_token"

def test_list_rules():
    # 创建测试用户和规则
    with TestingSessionLocal() as session:
        user = create_test_user(session)
        
        rule = Rule(
            pattern="^[A-Z]{3}\\d{5}$",
            description="Test rule",
            data_type="Test",
            region="Test",
            created_at=datetime.now(),
            # 添加用户关联（如果需要）
        )
        session.add(rule)
        session.commit()

    token = create_test_token(user)
    
    # 添加认证头
    response = client.get(
        "/rules",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_create_rule():
    with TestingSessionLocal() as session:
        user = create_test_user(session)
    # 使用唯一的测试数据
    test_rule = {
        "pattern": "^[A-Z]{4}\\d{6}$",
        "description": "Unique Test Rule",
        "data_type": "Test",
        "region": "Test"
    }
    token = create_test_token(user)
    # 添加认证头
    response = client.post(
        "/rules",
        json=test_rule,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["pattern"] == test_rule["pattern"]
    assert "id" in data
