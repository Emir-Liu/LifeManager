"""
TimePreference Service
时间偏好管理服务
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.time_preference import TimePreference
from app.schemas.time_preference import TimePreferenceCreate, TimePreferenceUpdate


class TimePreferenceService:
    """时间偏好管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_time_preference(
        self, user_id: int, data: TimePreferenceCreate
    ) -> TimePreference:
        """创建时间偏好"""
        preference = TimePreference(
            user_id=user_id,
            sleep_type=data.sleep_type.value,
            wake_up_time=data.wake_up_time,
            sleep_time=data.sleep_time,
            lunch_start=data.lunch_start,
            lunch_end=data.lunch_end,
            work_start=data.work_start,
            work_end=data.work_end,
            work_days=data.work_days,
            study_start=data.study_start,
            study_end=data.study_end,
            preferred_task_start=data.preferred_task_start,
            preferred_task_end=data.preferred_task_end,
            buffer_time_minutes=data.buffer_time_minutes,
        )
        self.db.add(preference)
        await self.db.commit()
        await self.db.refresh(preference)
        return preference

    async def get_user_time_preference(
        self, user_id: int
    ) -> Optional[TimePreference]:
        """获取用户时间偏好"""
        result = await self.db.execute(
            select(TimePreference).where(TimePreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_time_preference(
        self, user_id: int, data: TimePreferenceUpdate
    ) -> Optional[TimePreference]:
        """更新时间偏好"""
        # 获取现有偏好
        preference = await self.get_user_time_preference(user_id)
        if not preference:
            return None

        # 构建更新数据
        update_data = {}
        if data.sleep_type is not None:
            update_data["sleep_type"] = data.sleep_type.value
        if data.wake_up_time is not None:
            update_data["wake_up_time"] = data.wake_up_time
        if data.sleep_time is not None:
            update_data["sleep_time"] = data.sleep_time
        if data.lunch_start is not None:
            update_data["lunch_start"] = data.lunch_start
        if data.lunch_end is not None:
            update_data["lunch_end"] = data.lunch_end
        if data.work_start is not None:
            update_data["work_start"] = data.work_start
        if data.work_end is not None:
            update_data["work_end"] = data.work_end
        if data.work_days is not None:
            update_data["work_days"] = data.work_days
        if data.study_start is not None:
            update_data["study_start"] = data.study_start
        if data.study_end is not None:
            update_data["study_end"] = data.study_end
        if data.preferred_task_start is not None:
            update_data["preferred_task_start"] = data.preferred_task_start
        if data.preferred_task_end is not None:
            update_data["preferred_task_end"] = data.preferred_task_end
        if data.buffer_time_minutes is not None:
            update_data["buffer_time_minutes"] = data.buffer_time_minutes

        if not update_data:
            return preference

        # 执行更新
        await self.db.execute(
            update(TimePreference)
            .where(TimePreference.user_id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        await self.db.refresh(preference)

        return preference

    async def get_time_stats(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:
        """获取时间统计"""
        from app.schemas.time_preference import TimeStatsResponse

        # 设置默认日期范围(最近30天)
        if not end_date:
            end_date = datetime.now().date()
        if not start_date:
            start_date = datetime(end_date.year, end_date.month - 1, end_date.day).date()

        # 获取时间范围内的任务
        query = select(Task).where(
            Task.completed == True,
            Task.due_date >= start_date,
            Task.due_date <= end_date,
        )

        # 假设任务通过Goal关联到用户
        result = await self.db.execute(query)
        tasks = result.scalars().all()

        # 统计总工时
        total_hours = sum((task.estimated_hours or 0) for task in tasks)

        # 按目标统计
        goal_hours = {}
        for task in tasks:
            if task.goal:
                goal_title = task.goal.title
                goal_hours[goal_title] = goal_hours.get(goal_title, 0) + (task.estimated_hours or 0)

        # 按任务类型统计
        task_type_hours = {}
        for task in tasks:
            task_type = task.task_type or "general"
            task_type_hours[task_type] = task_type_hours.get(task_type, 0) + (task.estimated_hours or 0)

        return {
            "total_hours": total_hours,
            "goal_hours": goal_hours,
            "task_type_hours": task_type_hours,
            "date_range": (start_date, end_date),
        }
