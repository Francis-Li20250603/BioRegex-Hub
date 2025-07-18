from fastapi.testclient import TestClient
from app.main import app
from app.models import Rule
from app.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite:///./test.db"
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
    Rule.metadata.create_all(bind=engine)
    yield
    Rule.metadata.drop_all(bind=engine)

def test_list_rules():
    # 先创建一个规则以便测试列表
    test_rule = {
        "pattern": "^[A-Z]{3}\\d{5}$",
        "description": "Test rule",
        "data_type": "Test",
        "region": "Test"
    }
    client.post("/rules", json=test_rule)
    
    response = client.get("/rules")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_create_rule():
    test_rule = {
        "pattern": "^[A-Z]{3}\\d{5}$",
        "description": "Test rule",
        "data_type": "Test",
        "region": "Test"
    }
    response = client.post("/rules", json=test_rule)
    assert response.status_code == 201  # 创建成功应该返回201
    data = response.json()
    assert data["pattern"] == test_rule["pattern"]
    assert "id" in data
