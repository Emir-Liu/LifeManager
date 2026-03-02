"""
数据库配置
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 加载 .env 环境变量
from dotenv import load_dotenv
load_dotenv()

# 创建数据库 URL
# 优先使用环境变量 DATABASE_URL，否则根据配置构建
database_url = os.getenv("DATABASE_URL")

if not database_url:
    # 根据 .env 配置构建数据库 URL
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    if db_type == "mysql":
        database_url = (
            f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}"
            f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}"
            f"/{os.getenv('DB_NAME', 'lifemanager')}?charset={os.getenv('DB_CHARSET', 'utf8mb4')}"
        )
    elif db_type == "postgresql":
        database_url = (
            f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
    else:
        # 默认使用 SQLite
        database_url = "sqlite:///./lifemanager.db"

# 根据 URL 类型设置连接参数
if database_url.startswith("mysql"):
    # MySQL 配置
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # 检查连接有效性
        echo=False,          # 禁用 SQL 输出
        pool_size=10,        # 连接池大小
        max_overflow=20,     # 最大溢出连接数
        pool_recycle=3600,   # 连接回收时间(秒)
    )
elif database_url.startswith("sqlite"):
    # SQLite 配置
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        echo=False,
        connect_args={"check_same_thread": False}  # 允许跨线程使用
    )
else:
    # PostgreSQL 或其他数据库
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        echo=False,
    )

print(f"数据库连接: {database_url}")

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 依赖注入:获取数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
