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

    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./lifemanager.db"

    # AI 配置 (DeepSeek)
    OPENAI_API_BASE: str = "https://api.deepseek.com"
    OPENAI_API_KEY: str = ""
    AI_MODEL: str = "deepseek-chat"
    AI_MAX_TOKENS: int = 4000
    AI_TEMPERATURE: float = 0.7

    # 跨域配置
    CORS_ORIGINS: List[str] = ["*"]

    # 日志配置
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
