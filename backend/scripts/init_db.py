# backend/scripts/init_db.py

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.models import User, UserCreate
from app.database import get_engine
from sqlmodel import Session, SQLModel, select
# 从 User 类导入密码哈希方法（或从 security.py 导入）
from app.models import User  # 确保能访问 User.create_password_hash

def init_db():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        admin = session.exec(
            select(User).where(User.email == "admin@bioregex-hub.com")
        ).first()
        
        if not admin:
            # 创建 UserCreate 实例（仅包含定义的字段）
            admin_create_data = UserCreate(
                email="admin@bioregex-hub.com",
                full_name="Administrator",
                is_admin=True,
                password="${{ secrets.TEST_ADMIN_PASSWORD }}"  # 原始密码
            )
            
            # 手动计算哈希密码（使用 User 类的方法）
            hashed_password = User.create_password_hash(admin_create_data.password)
            
            # 创建 User 实例（包含 hashed_password）
            db_user = User(
                **admin_create_data.dict(exclude={"password"}),  # 排除原始密码
                hashed_password=hashed_password  # 手动传入哈希密码
            )
            
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            print("管理员账户创建成功")
        else:
            print("管理员账户已存在")

if __name__ == "__main__":
    print("Starting database initialization...")
    init_db()
