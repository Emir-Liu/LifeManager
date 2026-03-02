"""
应用配置管理
"""
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    """应用配置类"""
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    # 应用基本信息
    APP_NAME: str = "LifeManager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 天

    # 数据库配置
    DB_TYPE: str = "sqlite"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "lifemanager"
    DB_CHARSET: str = "utf8mb4"
    DATABASE_URL: str = "sqlite:///./lifemanager.db"

    @property
    def effective_database_url(self) -> str:
        """有效的数据库 URL (优先使用环境变量)"""
        return os.getenv("DATABASE_URL", self.DATABASE_URL)

    # 大模型配置 (OpenAI兼容接口)
    LLM_MODEL_NAME: str = "qwen3_32b_awq"
    LLM_MODEL_BASE_URL: str = "http://192.168.0.125:12300/v1"
    LLM_MODEL_API_KEY: str = ""
    LLM_MODEL_API_TYPE: str = "openai"  # 支持 openai/deepseek 等

    # 跨域配置
    CORS_ORIGINS: List[str] = ["*"]

    # 日志配置
    LOG_LEVEL: str = "INFO"


# 创建全局配置实例
settings = Settings()
