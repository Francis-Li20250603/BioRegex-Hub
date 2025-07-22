from sqlmodel import Session, select
from jose import jwt
from datetime import datetime, timedelta
from app.models import User, UserCreate
from app.database import get_engine  # 改用工厂函数获取引擎，确保配置正确

def create_test_user(session: Session, email: str = "test@example.com", is_admin: bool = False) -> User:
    """创建测试用户（确保会话由调用方管理）"""
    # 修正查询逻辑，确保条件正确
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    
    if not user:
        # 验证 UserCreate 模型参数完整性
        user_data = UserCreate(
            email=email,
            full_name="Test User",
            is_admin=is_admin,
            password="testpassword123"  # 符合密码验证要求
        )
        user = User.from_orm(user_data)
        session.add(user)
        session.commit()
        session.refresh(user)  # 刷新会话，确保获取完整字段
    return user

def create_test_token(
    user_id: int, 
    secret_key: str = "test-secret-key", 
    algorithm: str = "HS256",  # 显式指定算法，与项目配置一致
    expires_minutes: int = 30
) -> str:
    """生成测试用JWT令牌（与auth模块逻辑保持一致）"""
    to_encode = {"sub": str(user_id)}
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    try:
        return jwt.encode(to_encode, secret_key, algorithm=algorithm)
    except Exception as e:
        raise ValueError(f"令牌生成失败: {str(e)}") from e
