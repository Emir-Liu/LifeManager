"""
Conflict Service Tests
冲突检测服务测试
"""
import pytest
from datetime import datetime, time

from app.services.conflict_service import ConflictService, ConflictInfo


@pytest.fixture
def db_session(test_db):
    """测试数据库会话"""
    yield test_db


@pytest.fixture
def conflict_service(db_session):
    """创建冲突检测服务实例"""
    return ConflictService(db_session)


@pytest.fixture
def sample_user(db_session):
    """创建测试用户"""
    from app.models.user import User
    from app.core.security import get_password_hash

    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_task(db_session, sample_user):
    """创建测试任务"""
    from app.models.task import Task
    from app.models.goal import Goal

    # 创建目标
    goal = Goal(
        user_id=sample_user.id,
        title="测试目标",
        description="这是一个测试目标",
        status="planning",
    )
    db_session.add(goal)
    db_session.commit()
    db_session.refresh(goal)

    # 创建任务
    task = Task(
        goal_id=goal.id,
        title="测试任务",
        description="这是一个测试任务",
        due_date=datetime(2026, 3, 10),
        estimated_hours=2,
        start_time=time(9, 0),
        end_time=time(11, 0),
        duration_minutes=120,
        completed=False,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture
def sample_event(db_session, sample_user):
    """创建测试日程"""
    from app.models.event import Event

    event = Event(
        user_id=sample_user.id,
        title="会议",
        description="团队例会",
        event_type="meeting",
        start_date=datetime(2026, 3, 10).date(),
        start_time=time(14, 0),
        end_time=time(16, 0),
        duration_minutes=120,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


class TestConflictService:
    """冲突检测服务测试"""

    def test_detect_task_conflict_no_conflict(
        self, conflict_service, sample_task, db_session
    ):
        """测试无冲突场景"""
        conflicts = conflict_service._check_task_time_conflicts(
            task_id=sample_task.id,
            due_date=datetime(2026, 3, 11),
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
        assert len(conflicts) == 0

    def test_detect_task_conflict_task_overlap(
        self, conflict_service, sample_task, db_session
    ):
        """测试任务时间重叠冲突"""
        # 创建重叠任务
        from app.models.task import Task

        overlap_task = Task(
            goal_id=sample_task.goal_id,
            title="重叠任务",
            description="时间重叠的任务",
            due_date=datetime(2026, 3, 10),
            start_time=time(10, 0),
            end_time=time(12, 0),
            duration_minutes=120,
        )
        db_session.add(overlap_task)
        db_session.commit()

        conflicts = conflict_service._check_task_time_conflicts(
            task_id=sample_task.id,
            due_date=datetime(2026, 3, 10),
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
        assert len(conflicts) > 0
        assert conflicts[0].conflict_type == "task_overlap"

    def test_detect_task_conflict_event_overlap(
        self, conflict_service, sample_task, sample_event, db_session
    ):
        """测试日程重叠冲突"""
        conflicts = conflict_service._check_event_time_conflicts(
            task_id=sample_task.id,
            due_date=datetime(2026, 3, 10),
            start_time=time(14, 0),
            end_time=time(15, 0),
        )
        assert len(conflicts) > 0
        assert conflicts[0].conflict_type == "event_overlap"

    def test_time_overlap_true(self, conflict_service):
        """测试时间重叠判断 - 重叠"""
        assert conflict_service._time_overlap(
            time(9, 0), time(11, 0),
            time(10, 0), time(12, 0)
        )

    def test_time_overlap_false(self, conflict_service):
        """测试时间重叠判断 - 不重叠"""
        assert not conflict_service._time_overlap(
            time(9, 0), time(11, 0),
            time(12, 0), time(14, 0)
        )

    def test_time_overlap_boundary(self, conflict_service):
        """测试时间重叠判断 - 边界情况"""
        # 刚好结束时间=开始时间,不算重叠
        assert not conflict_service._time_overlap(
            time(9, 0), time(11, 0),
            time(11, 0), time(13, 0)
        )

    def test_suggest_resolution_task_overlap(self, conflict_service):
        """测试任务冲突解决建议"""
        conflict = ConflictInfo(
            task_id=1,
            task_title="任务A",
            conflict_with_id=2,
            conflict_with_title="任务B",
            conflict_type="task_overlap",
            start_time=datetime(2026, 3, 10, 9, 0),
            end_time=datetime(2026, 3, 10, 11, 0),
        )

        suggestion = conflict_service.suggest_resolution(conflict, user_id=1)

        assert "solutions" in suggestion
        assert len(suggestion["solutions"]) > 0
        assert suggestion["message"] != ""

    def test_suggest_resolution_event_overlap(self, conflict_service):
        """测试日程冲突解决建议"""
        conflict = ConflictInfo(
            task_id=1,
            task_title="任务A",
            conflict_with_id=2,
            conflict_with_title="会议",
            conflict_type="event_overlap",
            start_time=datetime(2026, 3, 10, 14, 0),
            end_time=datetime(2026, 3, 10, 16, 0),
        )

        suggestion = conflict_service.suggest_resolution(conflict, user_id=1)

        assert "solutions" in suggestion
        assert len(suggestion["solutions"]) > 0
        # 日程冲突通常只能调整任务
        assert any(sol["type"] == "move_task" for sol in suggestion["solutions"])

    def test_suggest_resolution_overload(self, conflict_service):
        """测试过载解决建议"""
        conflict = ConflictInfo(
            task_id=1,
            task_title="任务A",
            conflict_with_id=0,
            conflict_with_title="同一天的总任务",
            conflict_type="overload",
            start_time=datetime(2026, 3, 10, 0, 0),
            end_time=datetime(2026, 3, 10, 23, 59),
        )

        suggestion = conflict_service.suggest_resolution(conflict, user_id=1)

        assert "solutions" in suggestion
        assert len(suggestion["solutions"]) > 0
        assert suggestion["message"] != ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
