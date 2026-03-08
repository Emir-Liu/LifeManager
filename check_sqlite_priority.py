#!/usr/bin/env python3
"""
检查 SQLite 数据库表结构
"""
import sqlite3

def check_sqlite_table():
    """检查 SQLite 表结构"""
    db_path = "e:/project/LifeManager/lifemanager.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取 goals 表结构
        cursor.execute("PRAGMA table_info(goals)")
        columns = cursor.fetchall()

        print("SQLite goals table structure:")
        print("-" * 80)
        for col in columns:
            print(f"  {col[1]:<20} {col[2]:<20} NOT NULL={col[3]} PK={col[5]}")
        print("-" * 80)

        # 检查 priority 是否存在
        has_priority = any(col[1] == 'priority' for col in columns)
        if has_priority:
            print("\n[OK] Priority column exists")
        else:
            print("\n[WARNING] Priority column does NOT exist!")

            # 添加 priority 字段
            print("\nAdding priority column...")
            cursor.execute("""
                ALTER TABLE goals
                ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium'
            """)
            conn.commit()
            print("[OK] Successfully added priority column")

        conn.close()

    except Exception as e:
        print(f"[ERROR] Failed to check SQLite table: {e}")
        raise

if __name__ == "__main__":
    check_sqlite_table()
