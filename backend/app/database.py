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


def get_db() -> Generator[Session, None, None]:
    """数据库会话依赖，自动管理连接生命周期（修复命名错误）"""
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()  # 确保会话正确关闭，释放资源


def create_db_and_tables():
    """创建数据库表结构（显式导入所有模型）"""
    import app.models  # 强制加载所有模型，确保表结构正确生成
SQLModel.metadata.create_all(engine)
