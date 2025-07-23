import sys
import os
import logging
from sqlmodel import Session, select
from dotenv import load_dotenv

# 强制添加项目根目录到Python路径（解决模块导入问题）
BACKEND_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, BACKEND_DIR)

# 导入核心模块
from app.database import create_db_and_tables, engine
from app.models import User, UserCreate  # 使用修正后的UserCreate模型


# 加载环境变量（优先读取项目根目录的.env）
if os.path.exists(os.path.join(BACKEND_DIR, ".env")):
    load_dotenv(os.path.join(BACKEND_DIR, ".env"))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """初始化数据库：创建表结构和默认管理员"""
    logger.info("Starting database initialization...")
    
    # 创建表结构（确保所有模型被正确加载）
    create_db_and_tables()
    
    # 创建默认管理员（仅首次运行时）
    with Session(engine) as session:
        # 检查是否已有管理员用户
        admin_user = session.exec(select(User).where(User.is_admin == True)).first()
        
        if not admin_user:
            # 从环境变量获取管理员密码（云端使用secret，本地用默认）
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            
            # 使用UserCreate模型创建用户数据（自动处理密码哈希）
            admin_data = UserCreate(
                email="admin@bioregex.example",
                full_name="System Admin",
                is_admin=True,
                password=admin_password  # 传入原始密码，由UserCreate自动哈希
            )
            
            # 转换为数据库模型并存储
            admin_user = User.from_orm(admin_data)
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            
            logger.info(f"Created default admin user: {admin_user.email}")
        else:
            logger.info("Admin user already exists")


if __name__ == "__main__":
    init_db()
