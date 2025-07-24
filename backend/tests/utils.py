from sqlmodel import Session, select
from jose import jwt
from datetime import datetime, timedelta
from app.models import User, UserCreate
from app.config import settings
from app.utils.security import get_password_hash  # 导入密码哈希工具


def create_test_user(session: Session, email: str = "test@example.com", is_admin: bool = False) -> User:
    """创建测试用户，用于测试用例"""
    # 检查用户是否已存在
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    
    if not user:
        # 创建新用户
        user_data = UserCreate(
            email=email,
            full_name="Test User",
            is_admin=is_admin,
            password="test-pass-123"  # 测试用密码
        )
        
        # 手动创建User实例并处理密码哈希
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            is_admin=user_data.is_admin,
            hashed_password=get_password_hash(user_data.password)  # 生成哈希密码
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
    
    return user


def create_test_token(user_id: int, expires_minutes: int = 30) -> str:
    """生成测试用JWT令牌，使用配置中的密钥"""
    to_encode = {"sub": str(user_id)}
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    
    # 使用项目配置中的密钥和算法
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
