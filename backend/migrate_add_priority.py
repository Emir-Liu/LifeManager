#!/usr/bin/env python3
"""
为 goals 表添加 priority 字段
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# 从环境变量构建数据库URL
DB_TYPE = os.getenv("DB_TYPE", "mysql")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "lifemanager")
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

if DB_TYPE == "mysql":
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}"
else:
    DATABASE_URL = "sqlite:///./lifemanager.db"

def migrate():
    """添加 priority 字段"""
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # 检查字段是否已存在
            result = conn.execute(text("SHOW COLUMNS FROM goals LIKE 'priority'"))
            if result.fetchone():
                print("[OK] priority field already exists, no migration needed")
                return

            # 添加 priority 字段
            conn.execute(text("""
                ALTER TABLE goals
                ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium'
                COMMENT 'Priority: low/medium/high'
                AFTER status
            """))
            conn.commit()
            print("[OK] Successfully added priority field to goals table")

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate()
