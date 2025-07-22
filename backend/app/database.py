from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
from typing import Generator

# 云端环境适配：自动处理不同数据库类型的连接参数
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # 云端环境关闭SQL日志
    connect_args={
        # 仅SQLite需要此参数，云端通常使用PostgreSQL
        "check_same_thread": False
    } if settings.DATABASE_URL.startswith("sqlite") else {}
)

def get_engine():
    """提供引擎访问接口，供测试和迁移使用"""
    return engine

def get_session() -> Generator[Session, None, None]:
    """数据库会话依赖，自动管理连接生命周期"""
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()  # 确保会话正确关闭，释放资源

def create_db_and_tables():
    """创建数据库表结构（云端初始化使用）"""
    # 显式导入模型确保被加载
    import app.models
    SQLModel.metadata.create_all(engine)
