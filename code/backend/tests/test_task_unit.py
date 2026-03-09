"""
任务管理模块单元测试
"""
import pytest
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.goal import Goal
from app.models.task import Task
from app.models.plan import Plan
from app.services.task_service import TaskService


@pytest.fixture
def test_user(db: Session):
    """测试用户"""
    user = db.query(User).filter(User.username == "test_task_user").first()
    if not user:
        from app.core.security import get_password_hash
        user = User(
            username="test_task_user",
            password_hash=get_password_hash("password123"),
            email="test_task@example.com"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture
def test_goal(db: Session, test_user: User):
    """测试目标"""
    goal = db.query(Goal).filter(Goal.title == "测试目标").first()
    if not goal:
        goal = Goal(
            user_id=test_user.id,
            title="测试目标",
            description="用于测试任务功能",
            deadline=date(2026, 12, 31),
            status="confirmed"
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
    return goal


class TestTaskService:
    """测试任务服务"""

    def test_create_task(self, db_session: Session, test_goal: Goal):
        """测试创建任务"""
        task = task_service.create_task(
            db=db_session,
            goal_id=test_goal.id,
            title="测试任务",
            description="这是测试任务描述",
            due_date=date(2026, 6, 30),
            estimated_hours=2,
            stage_name="阶段1",
            task_order=1
        )

        assert task.id is not None
        assert task.title == "测试任务"
        assert task.goal_id == test_goal.id
        assert task.completed is False

    def test_get_user_tasks(self, db_session: Session, test_user: User, test_goal: Goal):
        """测试获取用户任务列表"""
        # 创建多个任务
        tasks_data = [
            {
                "title": f"任务{i}",
                "description": f"描述{i}",
                "due_date": date(2026, 6, 30),
                "estimated_hours": i,
                "stage_name": "阶段1",
                "task_order": i
            }
            for i in range(1, 4)
        ]

        for data in tasks_data:
            task_service.create_task(db_session, test_goal.id, **data)

        db_session.commit()

        # 获取任务列表
        tasks = task_service.get_user_tasks(db_session, test_user.id)
        assert len(tasks) >= 3

    def test_get_task_detail(self, db_session: Session, test_goal: Goal):
        """测试获取任务详情"""
        task = task_service.create_task(
            db=db_session,
            goal_id=test_goal.id,
            title="详情测试任务",
            due_date=date(2026, 6, 30),
            estimated_hours=1
        )

        db_session.commit()
        db_session.refresh(task)

        detail = task_service.get_task_detail(db_session, task.id, test_goal.user_id)

        assert detail["id"] == task.id
        assert detail["title"] == "详情测试任务"
        assert "goal_title" in detail

    def test_update_task(self, db_session: Session, test_goal: Goal):
        """测试更新任务"""
        task = task_service.create_task(
            db=db_session,
            goal_id=test_goal.id,
            title="原任务标题",
            due_date=date(2026, 6, 30),
            estimated_hours=1
        )

        db_session.commit()
        db_session.refresh(task)

        # 更新任务
        updated_task = task_service.update_task(
            db=db_session,
            task_id=task.id,
            user_id=test_goal.user_id,
            title="新任务标题",
            completed=True
        )

        assert updated_task.title == "新任务标题"
        assert updated_task.completed is True

    def test_delete_task(self, db_session: Session, test_goal: Goal):
        """测试删除任务"""
        task = task_service.create_task(
            db=db_session,
            goal_id=test_goal.id,
            title="待删除任务",
            due_date=date(2026, 6, 30),
            estimated_hours=1
        )

        db_session.commit()
        db_session.refresh(task)

        task_id = task.id

        # 删除任务
        result = task_service.delete_task(db_session, task_id, test_goal.user_id)
        assert result is True

        # 验证删除
        deleted_task = db_session.query(Task).filter(Task.id == task_id).first()
        assert deleted_task is None

    def test_update_task_status(self, db_session: Session, test_goal: Goal):
        """测试更新任务状态"""
        task = task_service.create_task(
            db=db_session,
            goal_id=test_goal.id,
            title="状态测试任务",
            due_date=date(2026, 6, 30),
            estimated_hours=1
        )

        db_session.commit()
        db_session.refresh(task)

        # 标记为完成
        updated = task_service.update_task_status(
            db=db_session,
            task_id=task.id,
            user_id=test_goal.user_id,
            completed=True
        )

        assert updated.completed is True

    def test_get_task_not_found(self, db_session: Session, test_goal: Goal):
        """测试获取不存在的任务"""
        with pytest.raises(ValueError, match="任务不存在"):
            task_service.get_task_detail(db_session, 99999, test_goal.user_id)

    def test_update_task_not_belong_to_user(self, db_session: Session, test_goal: Goal):
        """测试更新不属于用户的任务"""
        from app.core.security import get_password_hash

        # 创建另一个用户
        other_user = User(
            username="other_task_user",
            password_hash=get_password_hash("password123"),
            email="other_task@example.com"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # 创建属于其他用户的任务
        other_goal = Goal(
            user_id=other_user.id,
            title="其他目标",
            status="confirmed"
        )
        db_session.add(other_goal)
        db_session.commit()
        db_session.refresh(other_goal)

        task = task_service.create_task(
            db=db_session,
            goal_id=other_goal.id,
            title="其他用户任务",
            due_date=date(2026, 6, 30),
            estimated_hours=1
        )

        db_session.commit()
        db_session.refresh(task)

        # 尝试更新其他用户的任务
        with pytest.raises(ValueError, match="无权访问该任务"):
            task_service.update_task_status(
                db=db_session,
                task_id=task.id,
                user_id=test_goal.user_id,
                completed=True
            )

    def test_get_tasks_by_goal(self, db_session: Session, test_goal: Goal):
        """测试按目标获取任务"""
        # 创建多个任务
        for i in range(3):
            task_service.create_task(
                db=db_session,
                goal_id=test_goal.id,
                title=f"目标任务{i}",
                due_date=date(2026, 6, 30),
                estimated_hours=1
            )

        db_session.commit()

        # 获取目标的任务
        tasks = task_service.get_tasks_by_goal(db_session, test_goal.id, test_goal.user_id)
        assert len(tasks) >= 3
        for task in tasks:
            assert task.goal_id == test_goal.id

    def test_get_today_tasks(self, db_session: Session, test_goal: Goal):
        """测试获取今日任务"""
        today = date.today()

        # 创建今日任务
        task_service.create_task(
            db=db_session,
            goal_id=test_goal.id,
            title="今日任务",
            due_date=today,
            estimated_hours=1
        )

        # 创建其他日期的任务
        task_service.create_task(
            db=db_session,
            goal_id=test_goal.id,
            title="未来任务",
            due_date=date(2026, 12, 31),
            estimated_hours=1
        )

        db_session.commit()

        # 获取今日任务
        today_tasks = task_service.get_today_tasks(db_session, test_goal.user_id)
        assert any(task.due_date == today for task in today_tasks)

    def test_task_with_plan(self, db_session: Session, test_goal: Goal):
        """测试关联规划的任务"""
        # 创建规划
        plan = Plan(
            goal_id=test_goal.id,
            content='{"stages": []}',
            status="confirmed",
            total_stages=1,
            total_tasks=1
        )
        db_session.add(plan)
        db_session.commit()
        db_session.refresh(plan)

        # 创建关联规划的任务
        task = task_service.create_task(
            db=db_session,
            goal_id=test_goal.id,
            plan_id=plan.id,
            title="规划任务",
            due_date=date(2026, 6, 30),
            estimated_hours=1,
            stage_name="阶段1"
        )

        db_session.commit()
        db_session.refresh(task)

        assert task.plan_id == plan.id
        assert task.stage_name == "阶段1"
