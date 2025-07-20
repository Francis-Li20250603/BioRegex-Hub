import os
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseSettings, DirectoryPath  # 添加 BaseSettings 导入

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "please-change-this-in-production")  # 改为更安全的默认值
    ALGORITHM: str = "HS256"  # 直接设置默认值，简化配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 直接设置默认值，简化配置
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    UPLOAD_DIR: DirectoryPath = UPLOAD_DIR  # 使用 pydantic 的 DirectoryPath 类型
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB，直接设置默认值
    FDA_GUIDANCE_URL: str | None = os.getenv("FDA_GUIDANCE_URL")  # 可选值
    EMA_GUIDANCE_URL: str | None = os.getenv("EMA_GUIDANCE_URL")  # 可选值

    class Config:
        env_file = ".env"  # 指定环境变量文件位置（如果需要）

settings = Settings()
