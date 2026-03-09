"""
Pytest 配置和 Fixtures
"""
import os
import pytest
from fastapi.testclient import TestClient
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 设置测试环境变量,使用文件数据库(避免多连接问题)
TEST_DB_PATH = "./test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["TESTING"] = "true"

# 导入模型和工具
from app.models import User, Goal, Plan, Task
from app.core.security import get_password_hash, create_access_token
from app.core.database import Base, get_db

# 创建测试专用引擎
test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def reset_database():
    """重置数据库：删除所有表并重新创建"""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    创建测试数据库会话
    每个测试函数开始前重置数据库
    """
    # 重置数据库
    reset_database()
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    创建测试客户端
    使用测试数据库覆盖默认的数据库依赖
    """
    from main import app

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """测试会话结束时清理测试数据库文件"""
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture
def test_user(db) -> User:
    """
    创建测试用户
    """
    # 使用统一的密码加密方法
    password_hash = get_password_hash('pass123')

    user = User(
        username="testuser",
        password_hash=password_hash,
        email="test@example.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> dict:
    """
    创建认证请求头
    """
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_goal(db, test_user) -> Goal:
    """
    创建测试目标
    """
    goal = Goal(
        user_id=test_user.id,
        title="学习 Python",
        description="在3个月内掌握 Python 基础",
        status="planning"
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@pytest.fixture
def test_plan(db, test_goal) -> Plan:
    """
    创建测试规划
    """
    import json
    plan_content = {
        "stages": [
            {
                "name": "基础学习",
                "order": 1,
                "tasks": [
                    {
                        "title": "安装 Python",
                        "description": "下载并安装 Python",
                        "estimated_hours": 0.5,
                        "order": 1
                    }
                ]
            }
        ]
    }

    plan = Plan(
        goal_id=test_goal.id,
        content=json.dumps(plan_content),
        status="draft",
        total_stages=1,
        total_tasks=1,
        estimated_total_hours=0.5
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@pytest.fixture
def test_task(db, test_goal, test_plan) -> Task:
    """
    创建测试任务
    """
    from datetime import date, datetime

    task = Task(
        goal_id=test_goal.id,
        plan_id=test_plan.id,
        title="安装 Python",
        description="下载并安装 Python 3.10+",
        due_date=date.today(),
        completed=False,
        stage_name="基础学习",
        estimated_hours=1,
        task_order=0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
