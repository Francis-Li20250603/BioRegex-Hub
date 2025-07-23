from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from pathlib import Path
import os


class Settings(BaseSettings):
    # 数据库配置（从云端环境变量获取）
    DATABASE_URL: str

    # 安全配置
    SECRET_KEY: str = "default-secret-key-for-testing"  # 测试环境默认值
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 任务队列配置
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # 存储配置（云端使用临时目录）
    UPLOAD_DIR: Path = Path("/tmp/bioregex-uploads")  # 云端临时目录
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # 外部API配置
    FDA_GUIDANCE_URL: str | None = None
    EMA_GUIDANCE_URL: str | None = None

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("UPLOAD_DIR")
    def ensure_upload_dir_exists(cls, v: Path) -> Path:
        """确保上传目录存在（云端自动创建）"""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        """仅在生产环境强制密钥长度（放宽CI环境限制）"""
        if os.getenv("GITHUB_ACTIONS") != "true" and len(v) < 16:
            raise ValueError("生产环境SECRET_KEY长度必须至少16位")
        return v


# 实例化配置
settings = Settings()
