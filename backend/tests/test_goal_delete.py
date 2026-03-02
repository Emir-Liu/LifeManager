"""
目标删除功能单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.goal import Goal
from app.models.task import Task
from app.services.goal_service import goal_service


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """数据库会话"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def test_user(db_session: Session):
    """测试用户"""
    user = db_session.query(User).filter(User.username == "test_delete_user").first()
    if not user:
        user = User(
            username="test_delete_user",
            password_hash=get_password_hash("password123"),
            email="test_delete@example.com"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User):
    """认证头"""
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}


class TestDeleteGoal:
    """测试目标删除功能"""

    def test_delete_goal_success(self, client: TestClient, db_session: Session, test_user: User, auth_headers: dict):
        """测试成功删除目标"""
        # 创建目标
        goal = Goal(
            user_id=test_user.id,
            title="待删除的目标",
            description="这个目标将被删除",
            status="planning"
        )
        db_session.add(goal)
        db_session.commit()
        db_session.refresh(goal)

        # 删除目标
        response = client.delete(f"/api/goals/{goal.id}", headers=auth_headers)
        assert response.status_code == 200

        # 验证目标已删除
        deleted_goal = db_session.query(Goal).filter(Goal.id == goal.id).first()
        assert deleted_goal is None

    def test_delete_goal_with_tasks(self, client: TestClient, db_session: Session, test_user: User, auth_headers: dict):
        """测试删除包含任务的目标（级联删除）"""
        # 创建目标
        goal = Goal(
            user_id=test_user.id,
            title="带任务的目标",
            description="包含多个任务",
            status="confirmed"
        )
        db_session.add(goal)
        db_session.commit()
        db_session.refresh(goal)

        # 创建关联任务
        tasks = [
            Task(
                goal_id=goal.id,
                title=f"任务{i}",
                due_date="2026-12-31",
                completed=False,
                estimated_hours=2
            )
            for i in range(1, 4)
        ]
        db_session.add_all(tasks)
        db_session.commit()

        # 删除目标
        response = client.delete(f"/api/goals/{goal.id}", headers=auth_headers)
        assert response.status_code == 200

        # 验证目标和任务都已删除
        deleted_goal = db_session.query(Goal).filter(Goal.id == goal.id).first()
        assert deleted_goal is None

        deleted_tasks = db_session.query(Task).filter(Task.goal_id == goal.id).all()
        assert len(deleted_tasks) == 0

    def test_delete_goal_not_found(self, client: TestClient, test_user: User, auth_headers: dict):
        """测试删除不存在的目标"""
        response = client.delete("/api/goals/99999", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 1011  # GOAL_NOT_FOUND

    def test_delete_goal_not_belong_to_user(self, client: TestClient, db_session: Session, test_user: User, auth_headers: dict):
        """测试删除不属于当前用户的目标"""
        # 创建另一个用户
        other_user = User(
            username="other_user",
            password_hash=get_password_hash("password123"),
            email="other@example.com"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # 创建属于另一个用户的目标
        other_goal = Goal(
            user_id=other_user.id,
            title="其他用户的目标",
            description="不应被当前用户删除",
            status="planning"
        )
        db_session.add(other_goal)
        db_session.commit()
        db_session.refresh(other_goal)

        # 尝试删除其他用户的目标
        response = client.delete(f"/api/goals/{other_goal.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 1013  # GOAL_NOT_BELONG_TO_USER

    def test_delete_goal_without_auth(self, client: TestClient, db_session: Session):
        """测试未认证删除目标"""
        # 创建目标
        user = db_session.query(User).filter(User.username == "test_delete_user").first()
        goal = Goal(
            user_id=user.id,
            title="未认证目标",
            description="需要认证才能删除",
            status="planning"
        )
        db_session.add(goal)
        db_session.commit()
        db_session.refresh(goal)

        # 未认证删除
        response = client.delete(f"/api/goals/{goal.id}")
        assert response.status_code == 401

    def test_delete_goal_with_plan(self, client: TestClient, db_session: Session, test_user: User, auth_headers: dict):
        """测试删除包含规划的目标（级联删除）"""
        from app.models.plan import Plan

        # 创建目标
        goal = Goal(
            user_id=test_user.id,
            title="带规划的目标",
            description="包含规划",
            status="confirmed"
        )
        db_session.add(goal)
        db_session.commit()
        db_session.refresh(goal)

        # 创建规划
        plan = Plan(
            goal_id=goal.id,
            content='{"stages": []}',
            status="confirmed",
            total_stages=1,
            total_tasks=1
        )
        db_session.add(plan)
        db_session.commit()

        # 删除目标
        response = client.delete(f"/api/goals/{goal.id}", headers=auth_headers)
        assert response.status_code == 200

        # 验证规划和目标都已删除
        deleted_goal = db_session.query(Goal).filter(Goal.id == goal.id).first()
        assert deleted_goal is None

        deleted_plan = db_session.query(Plan).filter(Plan.id == plan.id).first()
        assert deleted_plan is None


class TestGoalServiceDelete:
    """测试目标服务删除方法"""

    def test_goal_service_delete_success(self, db_session: Session, test_user: User):
        """测试服务层删除成功"""
        goal = Goal(
            user_id=test_user.id,
            title="服务层测试目标",
            description="测试服务层删除",
            status="planning"
        )
        db_session.add(goal)
        db_session.commit()
        db_session.refresh(goal)

        # 调用服务删除
        result = goal_service.delete_goal(db_session, goal.id, test_user.id)
        assert result is True

        # 验证删除
        deleted_goal = db_session.query(Goal).filter(Goal.id == goal.id).first()
        assert deleted_goal is None

    def test_goal_service_delete_not_found(self, db_session: Session, test_user: User):
        """测试服务层删除不存在的目标"""
        with pytest.raises(ValueError, match="目标不存在"):
            goal_service.delete_goal(db_session, 99999, test_user.id)

    def test_goal_service_delete_not_belong(self, db_session: Session, test_user: User):
        """测试服务层删除不属于用户的目标"""
        other_user = User(
            username="other_service_user",
            password_hash=get_password_hash("password123"),
            email="other_service@example.com"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        goal = Goal(
            user_id=other_user.id,
            title="其他用户目标",
            status="planning"
        )
        db_session.add(goal)
        db_session.commit()
        db_session.refresh(goal)

        with pytest.raises(ValueError, match="无权删除该目标"):
            goal_service.delete_goal(db_session, goal.id, test_user.id)
