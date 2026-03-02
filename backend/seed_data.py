"""
数据库Seed脚本
用于创建测试数据
"""
import sys
import os
from datetime import datetime, timedelta

# 添加backend路径
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.core.database import engine, get_db
from app.models import user, goal, plan, task
from app.core.security import get_password_hash


def seed_users(db: Session):
    """创建测试用户"""
    users_data = [
        {
            "username": "testuser1",
            "password_hash": get_password_hash("password123"),
            "email": "test1@example.com",
            "is_active": 1
        },
        {
            "username": "testuser2",
            "password_hash": get_password_hash("password456"),
            "email": "test2@example.com",
            "is_active": 1
        }
    ]

    for user_data in users_data:
        existing_user = db.query(user.User).filter(
            user.User.username == user_data["username"]
        ).first()
        if not existing_user:
            db_user = user.User(**user_data)
            db.add(db_user)
            print(f"[OK] 创建用户: {user_data['username']}")
        else:
            print(f"[SKIP] 用户已存在: {user_data['username']}")

    db.commit()
    return db.query(user.User).first()


def seed_goals(db: Session, test_user: user.User):
    """创建测试目标"""
    goals_data = [
        {
            "user_id": test_user.id,
            "title": "学习Python编程",
            "description": "在3个月内掌握Python基础和进阶知识",
            "deadline": (datetime.now() + timedelta(days=90)).date(),
            "status": "planning"
        },
        {
            "user_id": test_user.id,
            "title": "完成LifeManager MVP开发",
            "description": "在17天内完成LifeManager MVP版本开发",
            "deadline": (datetime.now() + timedelta(days=17)).date(),
            "status": "confirmed"
        },
        {
            "user_id": test_user.id,
            "title": "健康生活计划",
            "description": "养成健康的生活习惯",
            "deadline": (datetime.now() + timedelta(days=180)).date(),
            "status": "planning"
        }
    ]

    for goal_data in goals_data:
        existing_goal = db.query(goal.Goal).filter(
            goal.Goal.title == goal_data["title"],
            goal.Goal.user_id == test_user.id
        ).first()
        if not existing_goal:
            db_goal = goal.Goal(**goal_data)
            db.add(db_goal)
            print(f"[OK] 创建目标: {goal_data['title']}")
        else:
            print(f"[SKIP] 目标已存在: {goal_data['title']}")

    db.commit()
    return db.query(goal.Goal).filter(goal.Goal.user_id == test_user.id).first()


def seed_plans_and_tasks(db: Session, test_goal: goal.Goal):
    """创建测试规划和任务"""
    # 创建规划
    plan_content = '''{
        "stages": [
            {
                "name": "阶段1: 基础知识学习",
                "duration": "30天",
                "tasks": [
                    {"title": "学习Python语法基础", "hours": 20},
                    {"title": "学习数据结构", "hours": 15},
                    {"title": "学习面向对象编程", "hours": 15}
                ]
            },
            {
                "name": "阶段2: 实战项目开发",
                "duration": "60天",
                "tasks": [
                    {"title": "开发个人博客", "hours": 30},
                    {"title": "开发API服务", "hours": 25}
                ]
            }
        ]
    }'''

    existing_plan = db.query(plan.Plan).filter(
        plan.Plan.goal_id == test_goal.id
    ).first()

    if not existing_plan:
        db_plan = plan.Plan(
            goal_id=test_goal.id,
            content=plan_content,
            status="confirmed",
            total_stages=2,
            total_tasks=5,
            estimated_total_hours=105.0
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        print(f"[OK] 创建规划: {test_goal.title}")
    else:
        db_plan = existing_plan
        print(f"[SKIP] 规划已存在: {test_goal.title}")

    # 创建任务
    tasks_data = [
        {
            "goal_id": test_goal.id,
            "plan_id": db_plan.id,
            "title": "学习Python语法基础",
            "description": "掌握Python基本语法、数据类型、控制流",
            "due_date": (datetime.now() + timedelta(days=10)).date(),
            "completed": False,
            "stage_name": "阶段1: 基础知识学习",
            "estimated_hours": 20,
            "task_order": 1
        },
        {
            "goal_id": test_goal.id,
            "plan_id": db_plan.id,
            "title": "学习数据结构",
            "description": "学习列表、字典、集合等数据结构",
            "due_date": (datetime.now() + timedelta(days=20)).date(),
            "completed": False,
            "stage_name": "阶段1: 基础知识学习",
            "estimated_hours": 15,
            "task_order": 2
        },
        {
            "goal_id": test_goal.id,
            "plan_id": db_plan.id,
            "title": "学习面向对象编程",
            "description": "理解类、对象、继承、多态",
            "due_date": (datetime.now() + timedelta(days=30)).date(),
            "completed": True,
            "stage_name": "阶段1: 基础知识学习",
            "estimated_hours": 15,
            "task_order": 3
        }
    ]

    for task_data in tasks_data:
        existing_task = db.query(task.Task).filter(
            task.Task.title == task_data["title"],
            task.Task.goal_id == test_goal.id
        ).first()
        if not existing_task:
            db_task = task.Task(**task_data)
            db.add(db_task)
            print(f"[OK] 创建任务: {task_data['title']}")
        else:
            print(f"[SKIP] 任务已存在: {task_data['title']}")

    db.commit()


def seed_all():
    """创建所有测试数据"""
    from app.core.database import Base

    # 创建数据库表
    Base.metadata.create_all(bind=engine)

    # 获取数据库会话
    db = next(get_db())

    try:
        print("\n[Seed] 开始创建测试数据...")
        print("=" * 50)

        # 创建用户
        test_user = seed_users(db)

        # 创建目标
        test_goal = seed_goals(db, test_user)

        # 创建规划和任务
        seed_plans_and_tasks(db, test_goal)

        print("=" * 50)
        print("[OK] 测试数据创建完成！\n")
        print("[Info] 测试账号:")
        print("   用户名: testuser1")
        print("   密码: password123")
        print("   用户名: testuser2")
        print("   密码: password456\n")

    except Exception as e:
        print(f"[ERROR] 创建测试数据失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
