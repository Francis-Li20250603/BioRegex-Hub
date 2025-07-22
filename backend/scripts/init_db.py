import sys
import logging
from pathlib import Path
from sqlmodel import Session, select
from app.database import create_db_and_tables, engine
from app.models import User, UserCreate
from dotenv import load_dotenv
import os

# 将项目根目录添加到Python路径，解决模块导入问题
sys.path.append(str(Path(__file__).parent.parent))

# 云端环境适配：加载环境变量
if os.path.exists(".env"):
    load_dotenv()  # 本地开发时加载，云端通过环境变量注入

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """初始化数据库：创建表结构和默认数据"""
    logger.info("Starting database initialization...")
    
    # 创建表结构
    create_db_and_tables()
    
    # 创建默认管理员（仅首次运行时）
    with Session(engine) as session:
        # 检查是否已有管理员
        admin_user = session.exec(select(User).where(User.is_admin == True)).first()
        
        if not admin_user:
            # 云端环境使用随机密码，本地开发使用默认密码
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            
            admin_data = UserCreate(
                email="admin@bioregex.example",
                full_name="System Admin",
                is_admin=True,
                password=admin_password
            )
            
            admin_user = User.from_orm(admin_data)
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            
            logger.info(f"Created default admin user: {admin_user.email}")
        else:
            logger.info("Admin user already exists")

if __name__ == "__main__":
    init_db()
