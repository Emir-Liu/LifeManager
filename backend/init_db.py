#!/usr/bin/env python3
"""
LifeManager 数据库初始化脚本
用于创建数据库和表结构
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DEFAULT_DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/lifemanager"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

def parse_mysql_url(url: str) -> dict:
    """解析 MySQL URL 获取连接信息"""
    # 格式: mysql+pymysql://user:password@host:port/database
    url = url.replace("mysql+pymysql://", "")
    
    # 分割认证信息和地址
    auth, rest = url.split("@", 1)
    user, password = auth.split(":", 1)
    
    # 分割地址和数据库名
    host_port, database = rest.split("/", 1)
    
    # 分割主机和端口
    if ":" in host_port:
        host, port = host_port.split(":", 1)
        port = int(port)
    else:
        host = host_port
        port = 3306
    
    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "database": database
    }

def create_database():
    """创建数据库（如果不存在）"""
    try:
        # 解析数据库连接信息
        db_info = parse_mysql_url(DATABASE_URL)
        
        # 连接到 MySQL 服务器（不指定数据库）
        server_url = f"mysql+pymysql://{db_info['user']}:{db_info['password']}@{db_info['host']}:{db_info['port']}"
        engine = create_engine(server_url)
        
        with engine.connect() as conn:
            # 创建数据库
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_info['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
            print(f"✅ 数据库 '{db_info['database']}' 创建成功或已存在")
            
    except OperationalError as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查:")
        print("  1. MySQL 服务是否已启动")
        print("  2. 用户名和密码是否正确")
        print("  3. 主机地址和端口是否正确")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        sys.exit(1)

def create_tables():
    """创建数据表"""
    try:
        # 导入模型
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app.core.database import engine, Base
        from app.models.user import User
        from app.models.goal import Goal
        from app.models.plan import Plan
        from app.models.task import Task
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据表创建成功")
        
    except ImportError as e:
        print(f"⚠️ 无法导入模型: {e}")
        print("使用 SQL 语句创建表...")
        create_tables_sql()
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        sys.exit(1)

def create_tables_sql():
    """使用 SQL 语句创建表"""
    from sqlalchemy import create_engine, text
    
    engine = create_engine(DATABASE_URL)
    
    # SQL 建表语句
    create_tables_sql = """
    -- 用户表
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
        password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
        email VARCHAR(100) UNIQUE COMMENT '邮箱',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        INDEX idx_username (username)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
    
    -- 目标表
    CREATE TABLE IF NOT EXISTS goals (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        user_id BIGINT NOT NULL COMMENT '用户ID',
        title VARCHAR(200) NOT NULL COMMENT '目标标题',
        description TEXT COMMENT '目标描述',
        deadline DATE COMMENT '截止日期',
        status VARCHAR(20) DEFAULT 'planning' COMMENT '状态: planning/confirmed/completed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        INDEX idx_user_id (user_id),
        INDEX idx_status (status),
        INDEX idx_deadline (deadline),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='目标表';
    
    -- 规划表
    CREATE TABLE IF NOT EXISTS plans (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        goal_id BIGINT NOT NULL COMMENT '目标ID',
        content TEXT NOT NULL COMMENT '规划内容(JSON)',
        status VARCHAR(20) DEFAULT 'draft' COMMENT '状态: draft/confirmed',
        total_stages INT DEFAULT 0 COMMENT '阶段数量',
        total_tasks INT DEFAULT 0 COMMENT '任务数量',
        estimated_total_hours FLOAT DEFAULT 0 COMMENT '预估总工时',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        INDEX idx_goal_id (goal_id),
        INDEX idx_status (status),
        FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='规划表';
    
    -- 任务表
    CREATE TABLE IF NOT EXISTS tasks (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        goal_id BIGINT NOT NULL COMMENT '目标ID',
        plan_id BIGINT COMMENT '规划ID',
        title VARCHAR(200) NOT NULL COMMENT '任务标题',
        description TEXT COMMENT '任务描述',
        estimated_hours FLOAT DEFAULT 0 COMMENT '预估工时',
        due_date TIMESTAMP NOT NULL COMMENT '截止时间',
        completed TINYINT(1) DEFAULT 0 COMMENT '是否完成',
        completed_at TIMESTAMP NULL COMMENT '完成时间',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        INDEX idx_goal_id (goal_id),
        INDEX idx_plan_id (plan_id),
        INDEX idx_due_date (due_date),
        INDEX idx_completed (completed),
        INDEX idx_goal_due (goal_id, due_date),
        FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE,
        FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务表';
    """
    
    with engine.connect() as conn:
        # 执行 SQL
        for statement in create_tables_sql.strip().split(';'):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()
    
    print("✅ 数据表创建成功 (使用 SQL)")

def main():
    """主函数"""
    print("=" * 50)
    print("LifeManager 数据库初始化")
    print("=" * 50)
    print()
    
    # 检查是否是 MySQL
    if not DATABASE_URL.startswith("mysql"):
        print(f"⚠️ 当前数据库不是 MySQL: {DATABASE_URL}")
        print("本脚本仅支持 MySQL 数据库")
        sys.exit(1)
    
    # 创建数据库
    print("📦 步骤 1: 创建数据库...")
    create_database()
    print()
    
    # 创建数据表
    print("📦 步骤 2: 创建数据表...")
    create_tables()
    print()
    
    print("=" * 50)
    print("✅ 数据库初始化完成!")
    print("=" * 50)
    print()
    print("数据库连接信息:")
    print(f"  URL: {DATABASE_URL}")
    print()
    print("提示: 如需重新初始化，请手动删除数据库后重新运行此脚本")

if __name__ == "__main__":
    main()
