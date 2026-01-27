"""
数据库配置
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# 创建数据库引擎 (使用环境变量或配置文件)
database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
engine = create_engine(
    database_url,
    pool_pre_ping=True,  # 检查连接有效性
    echo=False,          # 测试时禁用 SQL 输出
    connect_args={"check_same_thread": False}  # 允许跨线程使用
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 依赖注入：获取数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
