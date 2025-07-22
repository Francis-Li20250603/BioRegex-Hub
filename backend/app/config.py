from pydantic_settings import BaseSettings
from pydantic import DirectoryPath, field_validator
from pathlib import Path
import os

# 修正 Pydantic 配置为 V2 风格
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    UPLOAD_DIR: DirectoryPath = Path("uploads")
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    FDA_GUIDANCE_URL: str | None = None
    EMA_GUIDANCE_URL: str | None = None

    # 确保上传目录存在
    @field_validator("UPLOAD_DIR")
    def ensure_upload_dir_exists(cls, v):
        v.mkdir(exist_ok=True, parents=True)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True  # 环境变量区分大小写


# 实例化配置
settings = Settings()
