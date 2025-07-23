# backend/scripts/init_db.py

import sys
from pathlib import Path

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.models import User, UserCreate
from app.security import get_password_hash
from app.db import get_db_engine
from sqlmodel import Session, SQLModel, create_engine


def init_db():
    engine = get_db_engine()
    
    # 创建所有表
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # 检查管理员用户是否已存在
        admin = session.query(User).filter(User.email == "admin@bioregex-hub.com").first()
        
        if not admin:
            # 创建管理员用户
            admin_data = UserCreate(
                email="admin@bioregex-hub.com",
                username="admin",
                is_superuser=True,
                password="${{ secrets.TEST_ADMIN_PASSWORD }}"  # 使用明文密码字段
            )
            
            # 手动计算哈希密码
            hashed_password = get_password_hash(admin_data.password)
            
            # 创建数据库用户对象
            db_user = User(
                **admin_data.dict(exclude={"password"}),  # 排除明文密码
                hashed_password=hashed_password  # 设置哈希密码
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
