"""
数据库迁移脚本
用于数据库版本管理和迁移
"""
import sys
import os

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from alembic.config import Config
from alembic import command


def upgrade_migration():
    """执行数据库升级迁移"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("✅ 数据库升级完成")


def downgrade_migration():
    """执行数据库降级迁移"""
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, "-1")
    print("✅ 数据库降级完成")


def create_migration(message):
    """创建新的迁移脚本"""
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message=message)
    print(f"✅ 迁移脚本创建完成: {message}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据库迁移工具")
    parser.add_argument("action", choices=["upgrade", "downgrade", "create"], help="迁移操作")
    parser.add_argument("--message", default="Auto migration", help="迁移描述（仅用于create）")

    args = parser.parse_args()

    if args.action == "upgrade":
        upgrade_migration()
    elif args.action == "downgrade":
        downgrade_migration()
    elif args.action == "create":
        create_migration(args.message)
