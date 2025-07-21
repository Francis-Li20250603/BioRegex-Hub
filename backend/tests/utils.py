from app.models import User
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from typing import Optional

SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"

def create_test_user(session: Session, email="test@example.com", password="test123", is_admin=True) -> User:
    """创建测试用户"""
    user = User(
        email=email,
        full_name="Test User",
        hashed_password=User.create_password_hash(password),
        is_admin=is_admin
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def create_test_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """生成测试用 JWT token"""
    to_encode = {"sub": user.email, "id": user.id, "is_admin": user.is_admin}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
