"""
集成测试配置
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# 设置测试环境变量
TEST_DB_PATH = "./test_integration.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["TESTING"] = "true"

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
    """重置数据库"""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """创建测试数据库会话"""
    reset_database()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """创建测试客户端"""
    from main import app

    def override_get_db():
        try:
            yield db
            db.commit()  # 每个请求后自动提交
        finally:
            db.rollback()  # 清理未提交的更改

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db) -> User:
    """创建测试用户"""
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
    """创建认证请求头"""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
