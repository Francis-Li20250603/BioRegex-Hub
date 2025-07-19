from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 从环境变量获取数据库URL，或使用默认值
from os import getenv

DATABASE_URL = getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bioregex_hub")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 依赖函数，用于每个请求获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
