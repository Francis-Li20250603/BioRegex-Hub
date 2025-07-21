import os
from dotenv import load_dotenv
from pathlib import Path
# 从 pydantic-settings 导入 BaseSettings（关键修改）
from pydantic_settings import BaseSettings
from pydantic import DirectoryPath  # 其他类型仍从 pydantic 导入


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "please-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    UPLOAD_DIR: DirectoryPath = UPLOAD_DIR
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    FDA_GUIDANCE_URL: str | None = os.getenv("FDA_GUIDANCE_URL")
    EMA_GUIDANCE_URL: str | None = os.getenv("EMA_GUIDANCE_URL")

    class Config:
        env_file = ".env"


settings = Settings()
