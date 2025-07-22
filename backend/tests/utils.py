from sqlmodel import Session, select
from jose import jwt
from datetime import datetime, timedelta
from app.models import User, UserCreate
from app.database import engine  # 直接使用engine

def create_test_user(session: Session, email: str = "test@example.com", is_admin: bool = False) -> User:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    
    if not user:
        user_data = UserCreate(
            email=email,
            full_name="Test User",
            is_admin=is_admin,
            password="testpassword123"
        )
        user = User.from_orm(user_data)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

def create_test_token(
    user_id: int, 
    secret_key: str = "test-secret-key", 
    algorithm: str = "HS256",
    expires_minutes: int = 30
) -> str:
    to_encode = {"sub": str(user_id)}
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    try:
        return jwt.encode(to_encode, secret_key, algorithm=algorithm)
    except Exception as e:
        raise ValueError(f"令牌生成失败: {str(e)}") from e
