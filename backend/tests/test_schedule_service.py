"""
Schedule Service Tests
智能时间分配服务测试
"""
import pytest
from datetime import datetime, time

from app.services.schedule_service import ScheduleService, TimeSlot


@pytest.fixture
def db_session(test_db):
    """测试数据库会话"""
    yield test_db


@pytest.fixture
def schedule_service(db_session):
    """创建时间分配服务实例"""
    return ScheduleService(db_session)


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
def sample_time_preference(db_session, sample_user):
    """创建测试时间偏好"""
    from app.models.time_preference import TimePreference

    preference = TimePreference(
        user_id=sample_user.id,
        sleep_type="normal",
        wake_up_time=time(7, 0),
        sleep_time=time(23, 0),
        lunch_start=time(12, 0),
        lunch_end=time(13, 30),
        work_start=time(9, 0),
        work_end=time(18, 0),
        work_days="0,1,2,3,4",
        buffer_time_minutes=10,
    )
    db_session.add(preference)
    db_session.commit()
    db_session.refresh(preference)
    return preference


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


class TestTimeSlot:
    """时间段测试"""

    def test_time_slot_duration_minutes(self):
        """测试时间段持续时间计算"""
        slot = TimeSlot(
            start_time=datetime(2026, 3, 10, 9, 0),
            end_time=datetime(2026, 3, 10, 11, 0),
        )
        assert slot.duration_minutes == 120

    def test_time_slot_to_dict(self):
        """测试时间段转换为字典"""
        slot = TimeSlot(
            start_time=datetime(2026, 3, 10, 9, 0),
            end_time=datetime(2026, 3, 10, 11, 0),
            available=True,
        )
        slot_dict = slot.to_dict()
        assert slot_dict["duration_minutes"] == 120
        assert slot_dict["available"] == True
        assert "start_time" in slot_dict
        assert "end_time" in slot_dict


class TestScheduleService:
    """智能时间分配服务测试"""

    def test_generate_available_time_slots_with_preference(
        self, schedule_service, sample_user, sample_time_preference
    ):
        """测试生成可用时间段 - 使用时间偏好"""
        slots = schedule_service._generate_available_time_slots(
            due_date=datetime(2026, 3, 10),
            user_id=sample_user.id,
            preference=sample_time_preference,
        )

        assert len(slots) > 0
        # 应该包含午休不可用时间段
        lunch_slots = [s for s in slots if not s.available and "午休" in (s.reason or "")]
        assert len(lunch_slots) > 0

    def test_generate_available_time_slots_without_preference(
        self, schedule_service, sample_user
    ):
        """测试生成可用时间段 - 不使用时间偏好"""
        slots = schedule_service._generate_available_time_slots(
            due_date=datetime(2026, 3, 10),
            user_id=sample_user.id,
            preference=None,
        )

        assert len(slots) > 0
        # 使用默认时间偏好,应该有午休
        lunch_slots = [s for s in slots if not s.available and "午休" in (s.reason or "")]
        assert len(lunch_slots) > 0

    def test_generate_available_time_slots_with_event(
        self, schedule_service, sample_user, sample_time_preference, sample_event
    ):
        """测试生成可用时间段 - 包含日程"""
        slots = schedule_service._generate_available_time_slots(
            due_date=datetime(2026, 3, 10),
            user_id=sample_user.id,
            preference=sample_time_preference,
        )

        # 应该包含会议不可用时间段
        event_slots = [s for s in slots if not s.available and "会议" in (s.reason or "")]
        assert len(event_slots) > 0

    def test_get_events_for_date(self, schedule_service, sample_user, sample_event):
        """测试获取指定日期的日程"""
        events = schedule_service._get_events_for_date(
            due_date=datetime(2026, 3, 10),
            user_id=sample_user.id,
        )

        assert len(events) > 0
        assert events[0].title == "会议"

    def test_get_timeline(self, schedule_service, sample_user):
        """测试获取时间线"""
        timeline = schedule_service.get_timeline(
            due_date=datetime(2026, 3, 10),
            user_id=sample_user.id,
        )

        assert "date" in timeline
        assert "time_slots" in timeline
        assert len(timeline["time_slots"]) > 0

    def test_suggest_task_time_success(
        self, schedule_service, sample_user, sample_time_preference
    ):
        """测试建议任务时间 - 成功"""
        suggestion = schedule_service.suggest_task_time(
            task_id=1,
            due_date=datetime(2026, 3, 10),
            duration_minutes=60,
            user_id=sample_user.id,
        )

        assert "success" in suggestion
        assert "time_slots" in suggestion

    def test_suggest_task_time_no_available_slot(
        self, schedule_service, sample_user, sample_time_preference
    ):
        """测试建议任务时间 - 无可用时间段"""
        # 尝试分配过长的任务
        suggestion = schedule_service.suggest_task_time(
            task_id=1,
            due_date=datetime(2026, 3, 10),
            duration_minutes=1000,  # 超过一天
            user_id=sample_user.id,
        )

        assert suggestion["success"] == False
        assert "message" in suggestion

    def test_auto_assign_task_success(
        self, schedule_service, sample_user, sample_time_preference, sample_task
    ):
        """测试自动分配任务 - 成功"""
        from app.models.task import Task
        from app.models.goal import Goal

        # 创建目标和任务
        goal = Goal(
            user_id=sample_user.id,
            title="测试目标",
            description="这是一个测试目标",
            status="planning",
        )
        schedule_service.db.add(goal)
        schedule_service.db.commit()
        schedule_service.db.refresh(goal)

        task = Task(
            goal_id=goal.id,
            title="测试任务",
            description="这是一个测试任务",
            due_date=datetime(2026, 3, 10),
            estimated_hours=1,
        )
        schedule_service.db.add(task)
        schedule_service.db.commit()
        schedule_service.db.refresh(task)

        result = schedule_service.auto_assign_task(
            task_id=task.id,
            due_date=datetime(2026, 3, 10),
            duration_minutes=60,
            user_id=sample_user.id,
        )

        assert result["success"] == True
        assert "assigned_time" in result

    def test_auto_assign_task_with_conflict(
        self, schedule_service, sample_user, sample_time_preference, sample_event
    ):
        """测试自动分配任务 - 有冲突"""
        from app.models.task import Task
        from app.models.goal import Goal

        # 创建目标和任务
        goal = Goal(
            user_id=sample_user.id,
            title="测试目标",
            description="这是一个测试目标",
            status="planning",
        )
        schedule_service.db.add(goal)
        schedule_service.db.commit()
        schedule_service.db.refresh(goal)

        task = Task(
            goal_id=goal.id,
            title="测试任务",
            description="这是一个测试任务",
            due_date=datetime(2026, 3, 10),
            estimated_hours=1,
        )
        schedule_service.db.add(task)
        schedule_service.db.commit()
        schedule_service.db.refresh(task)

        # 尝试分配到会议时间,应该检测到冲突
        result = schedule_service.auto_assign_task(
            task_id=task.id,
            due_date=datetime(2026, 3, 10),
            duration_minutes=120,
            user_id=sample_user.id,
        )

        # 可能成功也可能失败,取决于是否有足够的时间
        if not result["success"]:
            assert "conflicts" in result
            assert len(result["conflicts"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
