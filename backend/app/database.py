frfrom sqlmodel import SQLModel, create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

def get_engine():
    return engine

def create_db_and_tables():
    """创建数据库表结构（显式导入所有模型）"""
    import app.models  # 强制加载所有模型，确保表结构正确生成
    SQLModel.metadata.create_all(engine)
