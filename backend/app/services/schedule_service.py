"""
Schedule Service
智能时间分配服务
"""
from datetime import datetime, time, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.task import Task
from app.models.time_preference import TimePreference
from app.services.conflict_service import ConflictService


class TimeSlot:
    """时间段"""

    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
        available: bool = True,
        reason: Optional[str] = None,
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.available = available
        self.reason = reason

    @property
    def duration_minutes(self) -> int:
        """持续时间(分钟)"""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_minutes": self.duration_minutes,
            "available": self.available,
            "reason": self.reason,
        }


class ScheduleService:
    """智能时间分配服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conflict_service = ConflictService(db)

    async def suggest_task_time(
        self,
        task_id: int,
        due_date: datetime,
        duration_minutes: int,
        user_id: int,
    ) -> dict:
        """
        为任务建议最佳时间

        Args:
            task_id: 任务ID
            due_date: 截止日期
            duration_minutes: 持续时间(分钟)
            user_id: 用户ID

        Returns:
            时间分配建议
        """
        # 获取用户时间偏好
        preference = await self._get_user_preference(user_id)

        # 生成可用时间段
        time_slots = await self._generate_available_time_slots(
            due_date, user_id, preference
        )

        # 找到最合适的时间段
        best_slot = None
        for slot in time_slots:
            if slot.available and slot.duration_minutes >= duration_minutes:
                best_slot = slot
                break

        if not best_slot:
            return {
                "success": False,
                "message": "没有找到足够的时间段",
                "time_slots": [slot.to_dict() for slot in time_slots],
            }

        # 检测冲突
        conflicts = await self.conflict_service.detect_task_conflict(
            task_id=task_id,
            due_date=due_date,
            start_time=best_slot.start_time.time(),
            end_time=best_slot.end_time.time(),
            duration_minutes=duration_minutes,
        )

        return {
            "success": True,
            "suggested_time": {
                "start_time": best_slot.start_time.isoformat(),
                "end_time": best_slot.end_time.isoformat(),
                "duration_minutes": best_slot.duration_minutes,
            },
            "conflicts": [conflict.to_dict() for conflict in conflicts],
            "time_slots": [slot.to_dict() for slot in time_slots],
        }

    async def auto_assign_task(
        self,
        task_id: int,
        due_date: datetime,
        duration_minutes: int,
        user_id: int,
    ) -> dict:
        """
        自动为任务分配时间

        Args:
            task_id: 任务ID
            due_date: 截止日期
            duration_minutes: 持续时间(分钟)
            user_id: 用户ID

        Returns:
            分配结果
        """
        # 获取时间建议
        suggestion = await self.suggest_task_time(
            task_id=task_id,
            due_date=due_date,
            duration_minutes=duration_minutes,
            user_id=user_id,
        )

        if not suggestion["success"]:
            return {
                "success": False,
                "message": "无法自动分配时间",
                "reason": suggestion["message"],
            }

        # 如果没有冲突,直接分配
        if not suggestion["conflicts"]:
            # 更新任务时间
            await self._update_task_time(
                task_id=task_id,
                start_time=suggestion["suggested_time"]["start_time"],
                end_time=suggestion["suggested_time"]["end_time"],
                duration_minutes=duration_minutes,
            )

            return {
                "success": True,
                "message": "任务已自动分配时间",
                "assigned_time": suggestion["suggested_time"],
            }
        else:
            return {
                "success": False,
                "message": "检测到时间冲突",
                "conflicts": suggestion["conflicts"],
                "suggested_time": suggestion["suggested_time"],
            }

    async def _get_user_preference(self, user_id: int) -> Optional[TimePreference]:
        """获取用户时间偏好"""
        result = await self.db.execute(
            select(TimePreference).where(TimePreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def _generate_available_time_slots(
        self,
        due_date: datetime,
        user_id: int,
        preference: Optional[TimePreference] = None,
    ) -> list[TimeSlot]:
        """
        生成可用时间段

        Args:
            due_date: 日期
            user_id: 用户ID
            preference: 用户时间偏好

        Returns:
            时间段列表
        """
        slots = []

        # 使用用户偏好或默认值
        if preference:
            wake_up = preference.wake_up_time if isinstance(preference.wake_up_time, time) else time(7, 0)
            sleep_time = preference.sleep_time if isinstance(preference.sleep_time, time) else time(23, 0)
            lunch_start = preference.lunch_start if isinstance(preference.lunch_start, time) else time(12, 0)
            lunch_end = preference.lunch_end if isinstance(preference.lunch_end, time) else time(13, 30)
            buffer_minutes = preference.buffer_time_minutes or 10
        else:
            wake_up = time(7, 0)
            sleep_time = time(23, 0)
            lunch_start = time(12, 0)
            lunch_end = time(13, 30)
            buffer_minutes = 10

        # 创建时间范围
        day_start = due_date.replace(hour=wake_up.hour, minute=wake_up.minute, second=0)
        day_end = due_date.replace(hour=sleep_time.hour, minute=sleep_time.minute, second=0)

        # 获取固定日程
        events = await self._get_events_for_date(due_date, user_id)

        # 初始化当前时间
        current_time = day_start

        # 遍历日程,生成时间段
        for event in events:
            event_start = due_date.replace(
                hour=event.start_time.hour,
                minute=event.start_time.minute,
                second=0,
            )
            event_end = due_date.replace(
                hour=event.end_time.hour,
                minute=event.end_time.minute,
                second=0,
            )

            # 如果当前时间早于日程开始,生成可用时间段
            if current_time < event_start:
                # 添加缓冲时间
                end_time = event_start - timedelta(minutes=buffer_minutes)
                if end_time > current_time:
                    slots.append(
                        TimeSlot(
                            start_time=current_time,
                            end_time=end_time,
                            available=True,
                        )
                    )

            # 添加不可用时间段(日程)
            slots.append(
                TimeSlot(
                    start_time=event_start,
                    end_time=event_end,
                    available=False,
                    reason=f"日程: {event.title}",
                )
            )

            # 更新当前时间
            current_time = event_end

        # 处理午休
        lunch_start_dt = due_date.replace(
            hour=lunch_start.hour,
            minute=lunch_start.minute,
            second=0,
        )
        lunch_end_dt = due_date.replace(
            hour=lunch_end.hour,
            minute=lunch_end.minute,
            second=0,
        )

        if current_time < lunch_start_dt:
            slots.append(
                TimeSlot(
                    start_time=current_time,
                    end_time=lunch_start_dt,
                    available=True,
                )
            )
            slots.append(
                TimeSlot(
                    start_time=lunch_start_dt,
                    end_time=lunch_end_dt,
                    available=False,
                    reason="午休",
                )
            )
            current_time = lunch_end_dt

        # 处理剩余时间
        if current_time < day_end:
            slots.append(
                TimeSlot(
                    start_time=current_time,
                    end_time=day_end,
                    available=True,
                )
            )

        return slots

    async def _get_events_for_date(
        self,
        due_date: datetime,
        user_id: int,
    ) -> list[Event]:
        """获取指定日期的日程"""
        result = await self.db.execute(
            select(Event).where(
                Event.start_date == due_date.date(),
                Event.user_id == user_id,
                Event.is_active == True,
            )
            .order_by(Event.start_time)
        )
        return list(result.scalars().all())

    async def _update_task_time(
        self,
        task_id: int,
        start_time: str,
        end_time: str,
        duration_minutes: int,
    ):
        """更新任务时间"""
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        # 更新任务
        await self.db.execute(
            f"UPDATE tasks SET start_time = '{start_dt.time()}', end_time = '{end_dt.time()}', "
            f"duration_minutes = {duration_minutes} WHERE id = {task_id}"
        )
        await self.db.commit()

    async def get_timeline(
        self,
        due_date: datetime,
        user_id: int,
    ) -> dict:
        """
        获取指定日期的时间线

        Args:
            due_date: 日期
            user_id: 用户ID

        Returns:
            时间线数据
        """
        # 获取用户时间偏好
        preference = await self._get_user_preference(user_id)

        # 生成时间段
        time_slots = await self._generate_available_time_slots(due_date, user_id, preference)

        # 获取任务
        tasks = await self._get_tasks_for_date(due_date, user_id)

        # 组装数据
        timeline = {
            "date": due_date.date().isoformat(),
            "time_slots": [],
        }

        for slot in time_slots:
            slot_data = slot.to_dict()

            # 查找在该时间段的任务
            if slot.available:
                slot_tasks = []
                for task in tasks:
                    if task.start_time and task.end_time:
                        task_start = due_date.replace(
                            hour=task.start_time.hour,
                            minute=task.start_time.minute,
                        )
                        task_end = due_date.replace(
                            hour=task.end_time.hour,
                            minute=task.end_time.minute,
                        )

                        if task_start >= slot.start_time and task_end <= slot.end_time:
                            slot_tasks.append(
                                {
                                    "id": task.id,
                                    "title": task.title,
                                    "start_time": task_start.isoformat(),
                                    "end_time": task_end.isoformat(),
                                    "duration_minutes": task.duration_minutes,
                                    "completed": task.completed,
                                }
                            )

                slot_data["tasks"] = slot_tasks

            timeline["time_slots"].append(slot_data)

        return timeline

    async def _get_tasks_for_date(
        self,
        due_date: datetime,
        user_id: int,
    ) -> list[Task]:
        """获取指定日期的任务"""
        # 通过Goal关联查找任务
        result = await self.db.execute(
            select(Task)
            .join(Task.goal)
            .where(
                Task.due_date == due_date,
                Task.goal.has(user_id=user_id),
            )
            .order_by(Task.start_time)
        )
        return list(result.scalars().all())
