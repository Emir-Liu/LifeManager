"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置类"""

    # 应用基本信息
    APP_NAME: str = "LifeManager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 安全密钥
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./lifemanager.db"

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI 配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    # FCM 配置
    FCM_SERVER_KEY: str = ""

    # 短信配置
    SMS_API_KEY: str = ""

    # 跨域配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # 日志配置
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
