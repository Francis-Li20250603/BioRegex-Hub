# 替换 import jwt 为 from jose import jwt
from jose import jwt
from datetime import datetime, timedelta
from sqlmodel import Session
from app.database import engine
from app.models import User, UserCreate

# 其余代码保持不变
def create_test_user(email: str = "test@example.com", is_admin: bool = False) -> User:
    with Session(engine) as session:
        user = session.exec(User.select().where(User.email == email)).first()
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

def create_test_token(user_id: int, secret_key: str = "test-secret-key", expires_minutes: int = 30) -> str:
    to_encode = {"sub": str(user_id)}
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm="HS256")
