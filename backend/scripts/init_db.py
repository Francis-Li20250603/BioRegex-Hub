# backend/scripts/init_db.py

import sys
from pathlib import Path

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.models import User, UserCreate
from app.database import get_engine  # 移除了未使用的get_password_hash
from sqlmodel import Session, SQLModel, select  # 添加select用于查询


def init_db():
    engine = get_engine()
    
    # 创建所有表
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # 检查管理员用户是否已存在（使用session.exec和select替代query）
        admin = session.exec(
            select(User).where(User.email == "admin@bioregex-hub.com")
        ).first()
        
        if not admin:
            # 创建管理员用户（匹配UserCreate模型字段）
            admin_data = UserCreate(
                email="admin@bioregex-hub.com",
                full_name="Administrator",  # 补充必填的full_name字段
                is_admin=True,  # 使用is_admin而非is_superuser（模型中定义的是is_admin）
                password="${{ secrets.TEST_ADMIN_PASSWORD }}"  # 明文密码由模型自动哈希
            )
            
            # 创建数据库用户对象（直接使用UserCreate的数据，无需手动处理密码）
            db_user = User(
                **admin_data.dict()  # 模型已自动处理hashed_password，无需排除password
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
