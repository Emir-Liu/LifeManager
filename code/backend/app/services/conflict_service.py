"""
Conflict Detection Service
时间冲突检测服务
"""
from datetime import datetime, time
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.task import Task


class ConflictInfo:
    """冲突信息"""

    def __init__(
        self,
        task_id: int,
        task_title: str,
        conflict_with_id: int,
        conflict_with_title: str,
        conflict_type: str,
        start_time: datetime,
        end_time: datetime,
    ):
        self.task_id = task_id
        self.task_title = task_title
        self.conflict_with_id = conflict_with_id
        self.conflict_with_title = conflict_with_title
        self.conflict_type = conflict_type
        self.start_time = start_time
        self.end_time = end_time

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_title": self.task_title,
            "conflict_with_id": self.conflict_with_id,
            "conflict_with_title": self.conflict_with_title,
            "conflict_type": self.conflict_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
        }


class ConflictService:
    """冲突检测服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def detect_task_conflict(
        self,
        task_id: int,
        due_date: datetime,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        duration_minutes: Optional[int] = None,
    ) -> list[ConflictInfo]:
        """
        检测任务时间冲突

        Args:
            task_id: 任务ID
            due_date: 截止日期
            start_time: 开始时间
            end_time: 结束时间
            duration_minutes: 持续时间(分钟)

        Returns:
            冲突列表
        """
        conflicts = []

        # 如果没有具体时间段,只检查日期级别冲突
        if not start_time or not end_time:
            # 检查同一天是否有过多任务
            conflicts.extend(
                await self._check_date_conflicts(task_id, due_date)
            )
        else:
            # 检查具体时间冲突
            conflicts.extend(
                await self._check_time_conflicts(
                    task_id, due_date, start_time, end_time
                )
            )

        return conflicts

    async def _check_date_conflicts(
        self, task_id: int, due_date: datetime
    ) -> list[ConflictInfo]:
        """
        检查日期级别冲突

        检查同一天是否有超过8小时的已安排任务
        """
        # 获取同一天的所有任务
        result = await self.db.execute(
            select(Task).where(
                Task.due_date == due_date,
                Task.id != task_id,
                Task.completed == False,
                (Task.start_time.isnot(None)) | (Task.estimated_hours > 0),
            )
        )
        tasks = result.scalars().all()

        # 计算总工时
        total_hours = 0
        for task in tasks:
            total_hours += task.estimated_hours or 0

        # 如果超过8小时,提示可能过度安排
        if total_hours > 8:
            return [
                ConflictInfo(
                    task_id=task_id,
                    task_title="当前任务",
                    conflict_with_id=0,
                    conflict_with_title="同一天的总任务",
                    conflict_type="overload",
                    start_time=due_date,
                    end_time=due_date,
                )
            ]

        return []

    async def _check_time_conflicts(
        self,
        task_id: int,
        due_date: datetime,
        start_time: time,
        end_time: time,
    ) -> list[ConflictInfo]:
        """
        检查具体时间冲突

        检查与已有任务或日程的时间重叠
        """
        conflicts = []

        # 检查与任务的时间冲突
        conflicts.extend(
            await self._check_task_time_conflicts(task_id, due_date, start_time, end_time)
        )

        # 检查与日程的时间冲突
        conflicts.extend(
            await self._check_event_time_conflicts(task_id, due_date, start_time, end_time)
        )

        return conflicts

    async def _check_task_time_conflicts(
        self,
        task_id: int,
        due_date: datetime,
        start_time: time,
        end_time: time,
    ) -> list[ConflictInfo]:
        """检查与任务的时间冲突"""
        conflicts = []

        # 获取同一天有具体时间的任务
        result = await self.db.execute(
            select(Task).where(
                Task.due_date == due_date,
                Task.id != task_id,
                Task.start_time.isnot(None),
                Task.end_time.isnot(None),
            )
        )
        tasks = result.scalars().all()

        for task in tasks:
            if self._time_overlap(start_time, end_time, task.start_time, task.end_time):
                conflicts.append(
                    ConflictInfo(
                        task_id=task_id,
                        task_title="当前任务",
                        conflict_with_id=task.id,
                        conflict_with_title=task.title,
                        conflict_type="task_overlap",
                        start_time=due_date.replace(hour=start_time.hour, minute=start_time.minute),
                        end_time=due_date.replace(hour=end_time.hour, minute=end_time.minute),
                    )
                )

        return conflicts

    async def _check_event_time_conflicts(
        self,
        task_id: int,
        due_date: datetime,
        start_time: time,
        end_time: time,
    ) -> list[ConflictInfo]:
        """检查与日程的时间冲突"""
        conflicts = []

        # 获取同一天的日程
        result = await self.db.execute(
            select(Event).where(
                Event.start_date == due_date.date(),
                Event.is_active == True,
            )
        )
        events = result.scalars().all()

        for event in events:
            if self._time_overlap(start_time, end_time, event.start_time.time(), event.end_time.time()):
                conflicts.append(
                    ConflictInfo(
                        task_id=task_id,
                        task_title="当前任务",
                        conflict_with_id=event.id,
                        conflict_with_title=event.title,
                        conflict_type="event_overlap",
                        start_time=due_date.replace(hour=start_time.hour, minute=start_time.minute),
                        end_time=due_date.replace(hour=end_time.hour, minute=end_time.minute),
                    )
                )

        return conflicts

    def _time_overlap(
        self,
        start1: time,
        end1: time,
        start2: time,
        end2: time,
    ) -> bool:
        """
        检查两个时间段是否重叠

        Args:
            start1: 第一个时间段的开始时间
            end1: 第一个时间段的结束时间
            start2: 第二个时间段的开始时间
            end2: 第二个时间段的结束时间

        Returns:
            是否重叠
        """
        # 转换为分钟数进行比较
        start1_min = start1.hour * 60 + start1.minute
        end1_min = end1.hour * 60 + end1.minute
        start2_min = start2.hour * 60 + start2.minute
        end2_min = end2.hour * 60 + end2.minute

        # 检查重叠: 两个时间段有交集
        return not (end1_min <= start2_min or start1_min >= end2_min)

    async def suggest_resolution(
        self,
        conflict: ConflictInfo,
        user_id: int,
    ) -> dict:
        """
        提供冲突解决建议

        Args:
            conflict: 冲突信息
            user_id: 用户ID

        Returns:
            解决建议
        """
        suggestions = {
            "solutions": [],
            "message": "",
        }

        if conflict.conflict_type == "task_overlap":
            suggestions["solutions"] = [
                {
                    "type": "move_task",
                    "description": f"将任务 '{conflict.task_title}' 调整到其他时间",
                },
                {
                    "type": "move_other_task",
                    "description": f"将任务 '{conflict.conflict_with_title}' 调整到其他时间",
                },
                {
                    "type": "split_task",
                    "description": "将任务拆分为多个时间段",
                },
            ]
            suggestions["message"] = (
                f"任务 '{conflict.task_title}' 与 '{conflict.conflict_with_title}' 时间冲突。"
                "建议调整其中一个任务的时间或将任务拆分。"
            )

        elif conflict.conflict_type == "event_overlap":
            suggestions["solutions"] = [
                {
                    "type": "move_task",
                    "description": f"将任务 '{conflict.task_title}' 调整到其他时间",
                    "note": "日程通常不能调整",
                },
            ]
            suggestions["message"] = (
                f"任务 '{conflict.task_title}' 与固定日程 '{conflict.conflict_with_title}' 冲突。"
                "建议调整任务时间。"
            )

        elif conflict.conflict_type == "overload":
            suggestions["solutions"] = [
                {
                    "type": "reduce_tasks",
                    "description": "减少当天的任务数量",
                },
                {
                    "type": "extend_date",
                    "description": "将部分任务推迟到第二天",
                },
            ]
            suggestions["message"] = (
                "当天安排的任务过多,可能导致无法完成。"
                "建议减少任务数量或将部分任务推迟。"
            )

        return suggestions
