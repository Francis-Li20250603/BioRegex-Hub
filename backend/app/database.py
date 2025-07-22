from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
from typing import Generator  # 新增类型提示

# 修正引擎创建逻辑（兼容不同数据库）
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # 测试环境可设为True便于调试
    connect_args={
        "check_same_thread": False  # 仅SQLite需要，自动适配
    } if settings.DATABASE_URL.startswith("sqlite") else {}
)

# 提供引擎访问函数（供测试和外部调用）
def get_engine():
    return engine

# 会话生成器（修正类型提示）
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()  # 确保会话正确关闭

# 数据库表创建函数（确保模型加载完成）
def create_db_and_tables():
    # 确保所有模型都已导入，避免表创建遗漏
    import app.models  # 显式导入模型模块
    SQLModel.metadata.create_all(engine)
