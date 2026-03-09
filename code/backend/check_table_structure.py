#!/usr/bin/env python3
"""
检查数据库表结构
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

def check_table():
    """检查表结构"""
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # 获取 goals 表结构
            result = conn.execute(text("SHOW COLUMNS FROM goals"))
            print("Current goals table structure:")
            print("-" * 80)
            for row in result:
                print(f"  {row[0]:<20} {row[1]:<20} {row[2]:<10} {row[3] if len(row) > 3 else ''}")
            print("-" * 80)

            # 检查 priority 是否存在
            result = conn.execute(text("SHOW COLUMNS FROM goals LIKE 'priority'"))
            priority_row = result.fetchone()
            if priority_row:
                print("\n[OK] Priority column exists:")
                print(f"  Field: {priority_row[0]}")
                print(f"  Type: {priority_row[1]}")
                print(f"  Null: {priority_row[2]}")
                print(f"  Key: {priority_row[3] if len(priority_row) > 3 else ''}")
                print(f"  Default: {priority_row[4] if len(priority_row) > 4 else ''}")
            else:
                print("\n[WARNING] Priority column does NOT exist!")

    except Exception as e:
        print(f"[ERROR] Failed to check table structure: {e}")
        raise

if __name__ == "__main__":
    check_table()
